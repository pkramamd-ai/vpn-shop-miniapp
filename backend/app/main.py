"""FastAPI entrypoint for the mini-app backend.

Exposed routes:
- GET  /api/health        -> liveness probe
- GET  /api/subscription  -> current user's Remnawave subscription state
- GET  /api/tariffs       -> static tariff list (driven by env)
- GET  /api/referral      -> referral link & stats (real numbers when
                             DATABASE_URL is configured)
- POST /api/invoice       -> for method=stars and DATABASE_URL set, returns a
                             Telegram createInvoiceLink URL the mini-app opens
                             via WebApp.openInvoice. Otherwise falls back to a
                             t.me/<bot>?start=buy_<n>_<method> deep link.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal

import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import db, telegram
from .auth import TelegramUser, telegram_user_dep
from .config import settings
from .remnawave import remnawave


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await remnawave.aclose()
    await db.close()


app = FastAPI(title="vpn-shop-miniapp", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _stars_for(months: int) -> int:
    return {
        1: settings.stars_price_1,
        3: settings.stars_price_3,
        6: settings.stars_price_6,
        12: settings.stars_price_12,
    }[months]


class SubscriptionResponse(BaseModel):
    status: Literal["active", "expired", "trial", "none"]
    expireAt: datetime | None
    daysLeft: int
    trafficLimitBytes: int
    trafficUsedBytes: int
    subscriptionUrl: str | None


class TariffResponse(BaseModel):
    months: Literal[1, 3, 6, 12]
    priceRub: int
    priceStars: int


class ReferralResponse(BaseModel):
    link: str
    invitedCount: int
    bonusDaysEarned: int
    bonusDaysPerInvite: int


class InvoiceRequest(BaseModel):
    months: Literal[1, 3, 6, 12]
    method: Literal["stars", "yookassa", "cryptobot"]


class InvoiceResponse(BaseModel):
    paymentUrl: str
    invoiceId: str
    # When true, the mini-app should call WebApp.openInvoice(paymentUrl).
    # Otherwise it should open paymentUrl as a Telegram link.
    isTelegramInvoice: bool


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/subscription", response_model=SubscriptionResponse)
async def get_subscription(user: TelegramUser = Depends(telegram_user_dep)) -> SubscriptionResponse:
    raw = await remnawave.get_user_by_telegram_id(user.id)
    if not raw:
        return SubscriptionResponse(
            status="none",
            expireAt=None,
            daysLeft=0,
            trafficLimitBytes=0,
            trafficUsedBytes=0,
            subscriptionUrl=None,
        )

    expire_raw = raw.get("expireAt")
    expire_at: datetime | None = None
    if expire_raw:
        expire_at = datetime.fromisoformat(str(expire_raw).replace("Z", "+00:00"))

    days_left = 0
    sub_status: Literal["active", "expired", "trial", "none"] = "none"
    if expire_at:
        delta = expire_at - datetime.now(timezone.utc)
        days_left = max(0, delta.days)
        sub_status = "active" if days_left > 0 else "expired"

    raw_status = str(raw.get("status", "")).lower()
    if "trial" in raw_status:
        sub_status = "trial"

    return SubscriptionResponse(
        status=sub_status,
        expireAt=expire_at,
        daysLeft=days_left,
        trafficLimitBytes=int(raw.get("trafficLimitBytes") or 0),
        trafficUsedBytes=int(raw.get("usedTrafficBytes") or raw.get("trafficUsedBytes") or 0),
        subscriptionUrl=raw.get("subscriptionUrl"),
    )


@app.get("/api/tariffs", response_model=list[TariffResponse])
async def get_tariffs() -> list[TariffResponse]:
    return [
        TariffResponse(months=1, priceRub=settings.price_1, priceStars=settings.stars_price_1),
        TariffResponse(months=3, priceRub=settings.price_3, priceStars=settings.stars_price_3),
        TariffResponse(months=6, priceRub=settings.price_6, priceStars=settings.stars_price_6),
        TariffResponse(months=12, priceRub=settings.price_12, priceStars=settings.stars_price_12),
    ]


@app.get("/api/referral", response_model=ReferralResponse)
async def get_referral(user: TelegramUser = Depends(telegram_user_dep)) -> ReferralResponse:
    bot = settings.telegram_bot_username or "your_bot"
    invited, granted = await db.referral_stats(user.id)
    return ReferralResponse(
        link=f"https://t.me/{bot}?start=ref_{user.id}",
        invitedCount=invited,
        bonusDaysEarned=granted * settings.referral_days,
        bonusDaysPerInvite=settings.referral_days,
    )


@app.post("/api/invoice", response_model=InvoiceResponse)
async def create_invoice(
    body: InvoiceRequest,
    user: TelegramUser = Depends(telegram_user_dep),
) -> InvoiceResponse:
    """Telegram Stars: create a real invoice link the mini-app can open inline.
    Other methods (or when DATABASE_URL is unset): hand off to the bot via a
    deep link, since payment flows already live there.
    """
    bot = settings.telegram_bot_username
    if not bot:
        raise HTTPException(500, "TELEGRAM_BOT_USERNAME is not configured")

    if body.method == "stars" and settings.database_url:
        try:
            customer_id = await db.upsert_customer(user.id, user.language_code)
            stars = _stars_for(body.months)
            purchase_id = await db.insert_stars_purchase(customer_id, body.months, stars)
            payload = f"{purchase_id}&{user.username or ''}"
            url = await telegram.create_stars_invoice_link(
                title=f"VPN — {body.months} mo",
                description=f"VPN subscription, {body.months} month(s)",
                payload=payload,
                stars_amount=stars,
            )
        except telegram.TelegramAPIError as exc:
            raise HTTPException(502, f"telegram: {exc}") from exc
        return InvoiceResponse(
            paymentUrl=url,
            invoiceId=str(purchase_id),
            isTelegramInvoice=True,
        )

    payload = f"buy_{body.months}_{body.method}"
    return InvoiceResponse(
        paymentUrl=f"https://t.me/{bot}?start={payload}",
        invoiceId=f"{user.id}-{body.months}-{body.method}",
        isTelegramInvoice=False,
    )


# When the frontend is bundled into the same image, serve it from /static.
# Mounted last so /api/* routes win.
_static_dir = os.environ.get("STATIC_DIR", "/app/static")
if os.path.isdir(_static_dir):
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
