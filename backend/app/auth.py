"""Validate Telegram WebApp initData per the official spec.

https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException, status

from .config import settings


def _verify_signature(init_data: str, bot_token: str) -> dict[str, str]:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("hash missing")

    data_check = "\n".join(f"{k}={parsed[k]}" for k in sorted(parsed))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("hash mismatch")
    return parsed


class TelegramUser:
    def __init__(self, raw: dict[str, object]) -> None:
        self.id: int = int(raw["id"])  # type: ignore[arg-type]
        self.username: str | None = raw.get("username")  # type: ignore[assignment]
        self.first_name: str = str(raw.get("first_name", ""))
        self.language_code: str = str(raw.get("language_code", "en"))


def telegram_user_dep(
    x_telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
) -> TelegramUser:
    """FastAPI dependency that returns the verified Telegram user."""

    if not x_telegram_init_data:
        if settings.allow_unsigned_dev:
            return TelegramUser({"id": 0, "first_name": "dev", "language_code": "en"})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing initData")

    if not settings.telegram_bot_token:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "TELEGRAM_BOT_TOKEN is not configured"
        )

    try:
        parsed = _verify_signature(x_telegram_init_data, settings.telegram_bot_token)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid initData: {exc}") from exc

    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "no user in initData")

    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "user JSON malformed") from exc

    return TelegramUser(user)
