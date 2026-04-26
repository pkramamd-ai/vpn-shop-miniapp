"""Lightweight async Postgres access for the bot's database.

We share the bot's `customer`, `purchase` and `referral` tables (see
db/migrations in the bot repo). The mini-app strictly does:

- read counts from `referral`
- upsert into `customer`
- insert a `purchase` row when starting a Telegram Stars flow

We never touch tables/columns outside that surface, and we never alter
schema — the bot owns migrations.
"""

from __future__ import annotations

from typing import Any

import asyncpg

from .config import settings

_pool: asyncpg.Pool | None = None


async def pool() -> asyncpg.Pool | None:
    global _pool
    if not settings.database_url:
        return None
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=1,
            max_size=4,
            command_timeout=10,
        )
    return _pool


async def close() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def referral_stats(referrer_telegram_id: int) -> tuple[int, int]:
    """Returns (invited_count, bonus_granted_count) for the given referrer."""
    p = await pool()
    if p is None:
        return 0, 0
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
              COUNT(*)::int                                            AS invited,
              COUNT(*) FILTER (WHERE bonus_granted = TRUE)::int        AS granted
            FROM referral
            WHERE referrer_id = $1
            """,
            referrer_telegram_id,
        )
    if row is None:
        return 0, 0
    return int(row["invited"]), int(row["granted"])


async def upsert_customer(telegram_id: int, language: str) -> int:
    """Returns the customer.id for telegram_id, creating the row if needed."""
    p = await pool()
    if p is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO customer (telegram_id, language)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE SET language = EXCLUDED.language
            RETURNING id
            """,
            telegram_id,
            language,
        )
    if row is None:
        raise RuntimeError("upsert_customer failed")
    return int(row["id"])


async def insert_stars_purchase(
    customer_id: int, month: int, stars_amount: int
) -> int:
    """Insert a 'new' purchase for the Telegram Stars flow.

    Bot's payment_service.ProcessPurchaseById will pick this row up by id once
    Telegram delivers `successful_payment` to the bot, mark it 'paid', and
    provision/extend the user in the Remnawave panel.
    """
    p = await pool()
    if p is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO purchase
                (amount, customer_id, month, currency, status, invoice_type)
            VALUES ($1, $2, $3, 'XTR', 'new', 'telegram')
            RETURNING id
            """,
            stars_amount,
            customer_id,
            month,
        )
    if row is None:
        raise RuntimeError("insert_stars_purchase failed")
    return int(row["id"])


async def get_customer_subscription(telegram_id: int) -> dict[str, Any] | None:
    """Subscription info from the bot's customer table when DB is available.

    Returns None when DATABASE_URL isn't set (caller falls back to Remnawave).
    """
    p = await pool()
    if p is None:
        return None
    async with p.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT expire_at, subscription_link
            FROM customer
            WHERE telegram_id = $1
            """,
            telegram_id,
        )
    if row is None:
        return None
    return {
        "expire_at": row["expire_at"],
        "subscription_link": row["subscription_link"],
    }
