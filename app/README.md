# App

FastAPI backend for Receipt. It only calls `receipt.pipeline` and `receipt.orders`, with no order logic of its own. The React frontend lives in `app/web/` and talks to the endpoints in `docs/api-contract.md`.

## Run

```bash
python -m app.server                  # http://127.0.0.1:8000, loads the solution mode at startup
python -m app.server --modes baseline,pretrained,solution
python -m app.server --no-models      # development without models
```

If `app/web/dist/` exists it is served at `/`. For development run Vite on port 5173, which proxies `/api` to the server.
