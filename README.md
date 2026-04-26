# vpn-shop-miniapp

Telegram Mini App for the VPN shop bot. Two parts in one repo:

| Folder | What | Where it runs |
| --- | --- | --- |
| `frontend/` | React 19 + Vite + TypeScript + Tailwind v4 + `@twa-dev/sdk` UI | Vercel (free, automatic HTTPS) |
| `backend/` | FastAPI service that validates Telegram WebApp `initData` and proxies the Remnawave panel | Fly.io (free `*.fly.dev` HTTPS subdomain) |

The mini-app is a thin read-only viewer on top of the existing Go bot
([pkramamd-ai/remnawave-telegram-shop](https://github.com/pkramamd-ai/remnawave-telegram-shop)).
Purchases happen through a deep-link back to the bot — the bot still owns all
payment flows (Telegram Stars, YooKassa, CryptoBot).

---

## Архитектура

```
┌──────────────┐    HTTPS, initData   ┌──────────────┐    Bearer    ┌────────────┐
│  Mini App    │ ───────────────────▶ │  FastAPI     │ ───────────▶ │ Remnawave  │
│  (Vercel)    │ ◀─────────────────── │  (Fly.io)    │ ◀─────────── │  panel     │
└──────────────┘                      └──────────────┘              └────────────┘
       │                                       ▲
       │ "Купить" → t.me/<bot>?start=buy_3_stars
       ▼
┌──────────────┐
│  Telegram    │
│  Bot (Go)    │  → платёжки уже встроены
└──────────────┘
```

---

## Деплой за 30 минут

### 1. Бэкенд → Fly.io (бесплатно)

Один раз: `curl -L https://fly.io/install.sh | sh && fly auth signup` (или `fly auth login`).

```bash
git clone https://github.com/pkramamd-ai/vpn-shop-miniapp.git
cd vpn-shop-miniapp/backend

# уникальное имя — оно станет частью URL <name>.fly.dev
fly apps create vpn-shop-api

# впиши секреты
fly secrets set \
  TELEGRAM_BOT_TOKEN='123:abc' \
  TELEGRAM_BOT_USERNAME='your_bot_username' \
  REMNAWAVE_URL='https://panel.example.com' \
  REMNAWAVE_TOKEN='remnawave_master_token' \
  CORS_ORIGINS='https://vpn-shop-miniapp.vercel.app'

# в fly.toml уже стоит app = "vpn-shop-api" — поменяй на своё имя если нужно
fly deploy
```

Через ~2 минуты API станет доступен по `https://<name>.fly.dev/api/health`.

### 2. Фронт → Vercel (бесплатно)

1. https://vercel.com/new → выбираешь репозиторий `vpn-shop-miniapp`.
2. **Root Directory** → `frontend`. **Framework** определится сам (Vite).
3. **Environment Variables**:
   - `VITE_API_BASE` = `https://<name>.fly.dev`
   - `VITE_SUPPORT_URL` = `https://t.me/your_support` (опционально)
4. **Deploy**. Через ~1 минуту получишь URL вида
   `https://vpn-shop-miniapp-xyz.vercel.app`.

### 3. Подключение mini-app к боту

В `@BotFather`:

```
/mybots → выбираешь бота → Bot Settings → Menu Button →
Configure Menu Button → впиши URL = https://vpn-shop-miniapp-xyz.vercel.app
```

Готово. Теперь у юзеров рядом с полем ввода появится кнопка mini-app.

Также обнови переменную `MINI_APP_URL` в боте (`pkramamd-ai/vpn-shop/.env`) на
тот же URL — бот вставляет её в инлайн-кнопки.

---

## Локальная разработка

```bash
# backend
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # ALLOW_UNSIGNED_DEV=true для отладки без Telegram
uvicorn app.main:app --reload

# frontend (в другом терминале)
cd frontend
npm install
cp .env.example .env  # VITE_API_BASE=http://localhost:8000
npm run dev
```

Открой `http://localhost:5173` — UI работает, но без Telegram-контекста.
Чтобы протестировать честно — нужен HTTPS-туннель (ngrok / cloudflared) и
ссылка из @BotFather Menu Button.

---

## Endpoints

| Method | Path | Описание |
| --- | --- | --- |
| GET | `/api/health` | liveness check |
| GET | `/api/subscription` | состояние подписки текущего юзера |
| GET | `/api/tariffs` | список тарифов |
| GET | `/api/referral` | реф-ссылка и статистика (v0.1: статистика заглушка) |
| POST | `/api/invoice` | возвращает `t.me/<bot>?start=buy_<n>_<method>` |

Все эндпоинты, кроме `/api/health`, требуют HTTP-заголовок
`X-Telegram-Init-Data` с подписью от `Telegram.WebApp.initData`. Подпись
валидируется HMAC-SHA256 по официальной спеке
(<https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app>).

---

## Что НЕ сделано (для следующих итераций)

- **Реферальная статистика**: сейчас возвращает нули, нужно подключиться к
  Postgres бота, читать из таблицы `customer` (`referrals_count`, `bonus_days`).
- **Покупка прямо из mini-app**: сейчас редирект на бота. Чтобы делать
  `WebApp.openInvoice` (Telegram Stars) внутри mini-app, нужно добавить в
  бэкенд эндпоинт, который вызывает `createInvoiceLink` Telegram Bot API.
- **Бот не обрабатывает start-параметры** `buy_<n>_<method>` — после редиректа
  юзер попадает в обычное /start меню. Можно допилить в форке отдельным PR.

---

## License

AGPL-3.0 (наследуется от
[upstream remnawave-telegram-shop](https://github.com/Jolymmiles/remnawave-telegram-shop)).
