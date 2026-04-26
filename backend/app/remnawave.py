"""Thin async client for the subset of Remnawave panel API the mini-app needs."""

from __future__ import annotations

import httpx

from .config import settings


def _parse_extra_headers(raw: str) -> dict[str, str]:
    """Parse "Key:Value,Key2:Value2" into a dict.

    Mirrors the bot's REMNAWAVE_HEADERS handling so the same env value can
    be reused for both services.
    """
    headers: dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        key, _, value = entry.partition(":")
        key = key.strip()
        value = value.strip()
        if key:
            headers[key] = value
    return headers


class RemnawaveClient:
    def __init__(self) -> None:
        headers = {"Authorization": f"Bearer {settings.remnawave_token}"}
        extra = _parse_extra_headers(settings.remnawave_headers)
        for k, v in extra.items():
            # Convert "Cookie-Name:value" pairs into a single Cookie header so
            # the panel's reverse-proxy lets the request through.
            if k.lower() == "cookie":
                headers["Cookie"] = v
            else:
                headers.setdefault("Cookie", "")
                if headers["Cookie"]:
                    headers["Cookie"] += "; "
                headers["Cookie"] += f"{k}={v}"
        self._client = httpx.AsyncClient(
            base_url=settings.remnawave_url.rstrip("/"),
            headers=headers,
            timeout=10.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Returns the first Remnawave user matching telegram_id, or None."""
        if not settings.remnawave_url or not settings.remnawave_token:
            return None
        try:
            resp = await self._client.get(f"/api/users/by-telegram-id/{telegram_id}")
        except httpx.RequestError:
            return None
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        body = resp.json().get("response") or []
        if isinstance(body, list) and body:
            return body[0]
        if isinstance(body, dict):
            return body
        return None


remnawave = RemnawaveClient()
