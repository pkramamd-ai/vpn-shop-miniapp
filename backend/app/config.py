from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables.

    Mirrors the relevant subset of the bot's .env so the mini-app can run
    against the same Remnawave panel and use the same pricing.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""

    remnawave_url: str = ""
    remnawave_token: str = ""

    price_1: int = 100
    price_3: int = 289
    price_6: int = 550
    price_12: int = 1020

    stars_price_1: int = 75
    stars_price_3: int = 220
    stars_price_6: int = 425
    stars_price_12: int = 785

    days_in_month: int = 30
    referral_days: int = 7

    # Postgres DSN for the bot's database (same value as the bot's own
    # DATABASE_URL). When set, /api/referral returns real numbers and
    # /api/invoice with method=stars creates a Telegram Stars invoice.
    # When unset, /api/referral returns zeros and /api/invoice falls back
    # to a t.me/<bot>?start=buy_<n>_<method> deep link.
    database_url: str = ""

    cors_origins: str = "*"

    allow_unsigned_dev: bool = False


settings = Settings()
