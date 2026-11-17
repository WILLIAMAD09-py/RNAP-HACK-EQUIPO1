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
             "cantidad": 50, "medida": "calibre 12", "hora_entrega": "15:00"},
  "review_fields": ["medida"],
  "extra_products": [],
  "sibling_options": [{"id": "CAB-002", "nombre": "Cable THW calibre 10", "medida": "calibre 10"}],
  "used_fallback": false,
  "timings": {"transcription": 2.1, "extraction": 0.9, "total": 3.0}
}
```
`review_fields` uses the names `cliente`, `producto_id`, `cantidad`, `medida`, `hora_entrega`.
Errors: 400 `{"detail": "..."}` for missing or undecodable audio.

## GET /api/orders
Today's confirmed orders, newest first:
`[{"timestamp": "2026-11-17T10:42:03", "cliente": "Pedro", "producto_id": "CAB-003", "producto": "Cable THW calibre 12", "cantidad": 50, "medida": "calibre 12", "hora_entrega": "15:00"}]`

## POST /api/orders
JSON body `{"cliente", "producto_id", "cantidad", "medida", "hora_entrega"}`. `producto_id` and `cantidad` (> 0) are required, `hora_entrega` must be `HH:MM` or empty. Returns 201 with the updated list of today's orders (same shape as GET). 422 with `{"detail": "..."}` on invalid input.

## GET /api/metrics
Real results read from `results/*.json`, never hard-coded:
`[{"name": "solution", "mode": "solution", "split": "test", "notes": 5, "wer": 0.12, "fields_correct": 0.8, "total_seconds_mean": 3.4}]`
Empty list if there are no results.

## Static files
If `app/web/dist/` exists, the server serves it at `/` (SPA fallback to `index.html`). In development, Vite runs on port 5173 and proxies `/api` to `http://127.0.0.1:8000`.
