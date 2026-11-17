# Receipt API contract

The FastAPI server in `app/server.py` exposes these endpoints. The React frontend in `app/web/` only talks to them. All JSON. Base path `/api`.

## GET /api/health
`{"status": "ok", "mode": "solution", "models_loaded": true}`

## GET /api/catalog
List of products:
`[{"id": "CAB-003", "nombre": "Cable THW calibre 12", "categoria": "Cable", "unidad": "metro", "medida": "calibre 12", "siblings": ["CAB-001", "CAB-002"]}]`

## POST /api/process
Multipart form, field `audio` (webm/ogg/wav/mp3/m4a from the browser recorder or an upload). Optional form field `mode` (`baseline`, `pretrained`, `solution`; default `solution`).
Response:
```json
{
  "transcription": "soy pedro mándame cincuenta metros de cable del doce",
  "ticket": {"cliente": "Pedro", "producto_id": "CAB-003", "producto": "Cable THW calibre 12",
             "cantidad": 50, "medida": "calibre 12", "hora_entrega": "15:00",
             "producto_solicitado": "cable del doce", "fuera_de_catalogo": false},
  "review_fields": ["medida"],
  "extra_products": [],
  "sibling_options": [{"id": "CAB-002", "nombre": "Cable THW calibre 10", "medida": "calibre 10"}],
  "used_fallback": false,
  "timings": {"transcription": 2.1, "extraction": 0.9, "total": 3.0}
}
```
`producto_solicitado` is the product exactly as the customer said it (or null). When no catalog product matches with enough confidence, `producto_id`, `producto` and `medida` are null, `fuera_de_catalogo` is true and the interface shows `producto_solicitado` as is (for example "tornillos M4"). `review_fields` then includes `producto_id`.
`review_fields` uses the names `cliente`, `producto_id`, `cantidad`, `medida`, `hora_entrega`.
Errors: 400 `{"detail": "..."}` for missing or undecodable audio.

## GET /api/orders
Today's confirmed orders, newest first:
`[{"timestamp": "2026-11-17T10:42:03", "cliente": "Pedro", "producto_id": "CAB-003", "producto": "Cable THW calibre 12", "cantidad": 50, "medida": "calibre 12", "hora_entrega": "15:00"}]`

## POST /api/orders
JSON body `{"cliente", "producto_id", "producto_solicitado", "cantidad", "medida", "hora_entrega"}`. `cantidad` (> 0) is required, and either a valid `producto_id` or a non-empty `producto_solicitado` (off-catalog order), `hora_entrega` must be `HH:MM` or empty. Returns 201 with the updated list of today's orders (same shape as GET). 422 with `{"detail": "..."}` on invalid input.

## GET /api/metrics
Real results read from `results/*.json`, never hard-coded:
`[{"name": "solution", "mode": "solution", "split": "test", "notes": 5, "wer": 0.12, "fields_correct": 0.8, "total_seconds_mean": 3.4}]`
Empty list if there are no results.

## Static files
If `app/web/dist/` exists, the server serves it at `/` (SPA fallback to `index.html`). In development, Vite runs on port 5173 and proxies `/api` to `http://127.0.0.1:8000`.

# Store inbox (Telegram)

Orders that arrive from the Telegram bot wait in an inbox until the store accepts or rejects them. The inbox is stored in `data/inbox/` (ignored by git): `inbox.json` plus the audio files. The bot runs inside `python -m app.server` (long polling thread) only when `TELEGRAM_BOT_TOKEN` is set in the environment or in `.env`.

Inbox item:
```json
{
  "id": "a1b2c3",
  "received_at": "2026-11-17T10:42:03",
  "source": "telegram",
  "customer": {"name": "Pedro Garza", "username": "pedrog", "chat_id": 123456},
  "status": "pending",
  "audio_url": "/api/inbox/a1b2c3/audio",
  "result": { ...same object as POST /api/process returns... }
}
```
`status` is `pending`, `accepted` or `rejected`. If the voice note does not say a name, `result.ticket.cliente` is filled with the Telegram name and `cliente` is not in `review_fields`.

## GET /api/inbox
All items of today, newest first. Optional `?status=pending`. The store page polls it every 2 seconds and plays a sound when a new pending id appears.

## GET /api/inbox/{id}/audio
The original voice note (`audio/ogg`).

## POST /api/inbox/{id}/accept
Body: the ticket as edited by the store (same body as POST /api/orders) plus optional `"reply": "<text>"`. Saves the order (same as POST /api/orders), sets status `accepted` and sends `reply` to the customer on Telegram (or the default accepted message). Returns the updated item.

## POST /api/inbox/{id}/reject
Body `{"reply": "<text>"}` (optional). Sets status `rejected` and sends the reply (or the default rejected message). Returns the updated item.

## GET /api/replies
Predefined replies the store can choose from, with placeholders filled by the frontend:
`[{"id": "confirmado", "label": "Confirmar", "text": "Hola {cliente}, tu pedido de {cantidad} {producto} quedó confirmado para las {hora}."}, ...]`
Placeholders: `{cliente}`, `{cantidad}`, `{producto}`, `{hora}`. At least: confirmado, sin_existencia, cambio_de_hora, pedir_medida, rechazado.

## GET /api/telegram
`{"enabled": true, "bot_username": "ferre_nogales_bot"}` or `{"enabled": false, "bot_username": null}`.

When the bot receives a voice note it answers right away "Recibimos tu nota de voz, la tienda la está revisando." and, if processing fails, a friendly error. Text messages get a short help message.
