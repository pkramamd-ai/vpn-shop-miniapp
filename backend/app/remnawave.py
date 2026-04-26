"""Thin async client for the subset of Remnawave panel API the mini-app needs."""

from __future__ import annotations

import httpx

from .config import settings


class RemnawaveClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.remnawave_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.remnawave_token}"},
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
