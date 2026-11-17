# App

FastAPI backend for Receipt. It only calls `receipt.pipeline` and `receipt.orders`, with no order logic of its own. The React frontend lives in `app/web/` and talks to the endpoints in `docs/api-contract.md`.

## Run

```bash
python -m app.server                  # http://127.0.0.1:8000, loads the solution mode at startup
python -m app.server --modes baseline,pretrained,solution
python -m app.server --no-models      # development without models
```

If `app/web/dist/` exists it is served at `/`. For development run Vite on port 5173, which proxies `/api` to the server.

## Telegram bot

Customers send voice notes to a Telegram bot and the orders arrive in the store inbox (`/api/inbox`).

1. In Telegram, talk to `@BotFather`, send `/newbot` and follow the steps. It gives you a token.
2. Create a `.env` file in the repo root (ignored by git) with `TELEGRAM_BOT_TOKEN=<your token>`. The variable can also be set in the environment.
3. Run `python -m app.server`. If the token is present the bot starts (long polling thread) and `GET /api/telegram` returns its username.

Use `--no-telegram` to skip the bot even when the token exists. Never commit the token.
