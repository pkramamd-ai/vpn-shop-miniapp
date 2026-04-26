"""Telegram Bot API client — only the calls the mini-app actually makes."""

from __future__ import annotations

import httpx

from .config import settings


class TelegramAPIError(RuntimeError):
    pass


async def create_stars_invoice_link(
    *, title: str, description: str, payload: str, stars_amount: int
) -> str:
    """https://core.telegram.org/bots/api#createinvoicelink

    For Telegram Stars: provider_token must be empty, currency='XTR',
    prices.amount in Stars units (no minor units).
    """
    if not settings.telegram_bot_token:
        raise TelegramAPIError("TELEGRAM_BOT_TOKEN is not configured")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/createInvoiceLink"
    body = {
        "title": title,
        "description": description,
        "payload": payload,
        "provider_token": "",
        "currency": "XTR",
        "prices": [{"label": title, "amount": stars_amount}],
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=body)
    data = resp.json()
    if not data.get("ok"):
        raise TelegramAPIError(data.get("description", "createInvoiceLink failed"))
    return str(data["result"])
