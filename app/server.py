import argparse
import csv
import json
import os
import tempfile
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app import inbox, telegram_bot
from receipt import config, orders, pipeline
from receipt.catalog import load_catalog
from receipt.ticket import Ticket, normalize_time

DEFAULT_MODE = "solution"
DIST_DIR = Path(__file__).resolve().parent / "web" / "dist"
ENV_PATH = config.ROOT / ".env"
STARTUP_MODES = [DEFAULT_MODE]
state = {"models_loaded": False, "telegram": True}

REPLIES = [
    {"id": "confirmado", "label": "Confirmar",
     "text": "Hola {cliente}, tu pedido de {cantidad} {producto} quedó confirmado para las {hora}."},
    {"id": "sin_existencia", "label": "Sin existencia",
     "text": "Hola {cliente}, por ahora no tenemos {producto} en existencia. Disculpa la molestia."},
    {"id": "cambio_de_hora", "label": "Cambio de hora",
     "text": "Hola {cliente}, no podemos entregar tu pedido a las {hora}. ¿Te funciona otra hora?"},
    {"id": "pedir_medida", "label": "Pedir medida",
     "text": "Hola {cliente}, ¿qué medida necesitas de {producto}? Con eso preparamos tu pedido."},
    {"id": "rechazado", "label": "Rechazar",
     "text": "Hola {cliente}, lamentamos no poder atender tu pedido por ahora. Gracias por escribirnos."},
]
DEFAULT_ACCEPTED = "Hola, tu pedido quedó confirmado. Gracias por tu compra."
DEFAULT_REJECTED = "Hola, lamentamos no poder atender tu pedido por ahora. Gracias por escribirnos."


def read_env_token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if token or not ENV_PATH.is_file():
        return token
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() == "TELEGRAM_BOT_TOKEN":
            return value.strip().strip('"').strip("'")
    return ""


@asynccontextmanager
async def lifespan(app):
    for mode in STARTUP_MODES:
        pipeline.load_models(mode)
    state["models_loaded"] = bool(STARTUP_MODES)
    token = read_env_token() if state["telegram"] else ""
    if token:
        try:
            print(f"Bot de Telegram activo: @{telegram_bot.start(token, build_result)}")
        except Exception as error:
            print(f"No se pudo iniciar el bot de Telegram: {type(error).__name__}")
            telegram_bot.stop()
    yield
    telegram_bot.stop()


app = FastAPI(title="Receipt", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"],
                   allow_headers=["*"])


class OrderIn(BaseModel):
    cliente: str | None = None
    producto_id: str | None = None
    producto_solicitado: str | None = None
    cantidad: int | None = None
    medida: str | None = None
    hora_entrega: str | None = None


class AcceptIn(OrderIn):
    reply: str | None = None


class RejectIn(BaseModel):
    reply: str | None = None


def product_dict(product, catalog):
    return {"id": product.id, "nombre": product.nombre, "categoria": product.categoria,
            "unidad": product.unidad, "medida": product.medida,
            "siblings": [other.id for other in catalog.siblings(product)]}


def build_result(result):
    ticket = result.ticket
    catalog = load_catalog()
    product = catalog.by_id.get(ticket.producto_id)
    siblings = catalog.siblings(product) if product else []
    return {
        "transcription": result.transcription,
        "ticket": {"cliente": ticket.cliente, "producto_id": ticket.producto_id, "producto": ticket.producto,
                   "cantidad": ticket.cantidad, "medida": ticket.medida, "hora_entrega": ticket.hora_entrega,
                   "producto_solicitado": getattr(ticket, "producto_solicitado", None),
                   "fuera_de_catalogo": getattr(ticket, "fuera_de_catalogo", False)},
        "review_fields": list(ticket.review_fields),
        "extra_products": list(result.extra_products),
        "sibling_options": [{"id": other.id, "nombre": other.nombre, "medida": other.medida}
                            for other in siblings],
        "used_fallback": result.used_fallback,
        "timings": {"transcription": round(result.transcription_seconds, 3),
                    "extraction": round(result.extraction_seconds, 3),
                    "total": round(result.transcription_seconds + result.extraction_seconds, 3)},
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": DEFAULT_MODE, "models_loaded": state["models_loaded"]}


@app.get("/api/catalog")
def catalog_endpoint():
    catalog = load_catalog()
    return [product_dict(product, catalog) for product in catalog.products]


@app.post("/api/process")
async def process(audio: UploadFile | None = File(None), mode: str = Form(DEFAULT_MODE)):
    if mode not in config.MODES:
        raise HTTPException(400, f"Modo desconocido: {mode}")
    data = await audio.read() if audio else b""
    if not data:
        raise HTTPException(400, "Falta el audio o está vacío.")
    suffix = Path(audio.filename or "").suffix or ".webm"
    handle = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        with handle:
            handle.write(data)
        try:
            result = pipeline.process_audio(handle.name, mode)
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(400, f"No se pudo procesar el audio: {error}")
    finally:
        Path(handle.name).unlink(missing_ok=True)
    return build_result(result)


def todays_orders():
    path = config.ORDERS_PATH
    if not path.exists():
        return []
    today = date.today().isoformat()
    with open(path, encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["timestamp"].startswith(today)]
    result = []
    for row in reversed(rows):
        quantity = row["cantidad"]
        result.append({"timestamp": row["timestamp"], "cliente": row["cliente"] or None,
                       "producto_id": row["producto_id"] or None, "producto": row["producto"],
                       "cantidad": int(quantity) if quantity.isdigit() else quantity,
                       "medida": row["medida"] or None, "hora_entrega": row["hora_entrega"] or None})
    return result


@app.get("/api/orders")
def list_orders():
    return todays_orders()


def save_order(body):
    product = load_catalog().by_id.get(body.producto_id or "")
    requested = (body.producto_solicitado or "").strip()
    if not product and not requested:
        return JSONResponse({"detail": "Producto no válido o ausente."}, status_code=422)
    if not body.cantidad or body.cantidad <= 0:
        return JSONResponse({"detail": "La cantidad debe ser mayor que 0."}, status_code=422)
    hour = None
    if (body.hora_entrega or "").strip():
        hour = normalize_time(body.hora_entrega)
        if hour is None:
            return JSONResponse({"detail": "La hora debe tener formato HH:MM."}, status_code=422)
    client_name = (body.cliente or "").strip() or None
    measure = (body.medida or "").strip() or None
    if product:
        ticket = Ticket(cliente=client_name, producto_id=product.id, producto=product.nombre,
                        cantidad=body.cantidad, medida=measure or product.medida, hora_entrega=hour)
    else:
        ticket = Ticket(cliente=client_name, producto_id=None, producto=requested,
                        cantidad=body.cantidad, medida=measure, hora_entrega=hour)
    orders.confirm(ticket, config.ORDERS_PATH)
    return None


@app.post("/api/orders", status_code=201)
def create_order(body: OrderIn):
    return save_order(body) or todays_orders()


def get_item_or_404(item_id):
    item = inbox.get(item_id)
    if not item:
        raise HTTPException(404, "Pedido no encontrado.")
    return item


def reply_to_customer(item, text):
    chat_id = (item.get("customer") or {}).get("chat_id")
    if chat_id and text:
        telegram_bot.send_message(chat_id, text)


@app.get("/api/inbox")
def list_inbox(status: str | None = None):
    return inbox.list_today(status)


@app.get("/api/inbox/{item_id}/audio")
def inbox_audio(item_id: str):
    get_item_or_404(item_id)
    path = inbox.audio_path(item_id)
    if not path.is_file():
        raise HTTPException(404, "Audio no encontrado.")
    return FileResponse(path, media_type="audio/ogg")


@app.post("/api/inbox/{item_id}/accept")
def accept_inbox(item_id: str, body: AcceptIn):
    item = get_item_or_404(item_id)
    if item["status"] != "pending":
        return JSONResponse({"detail": "El pedido ya fue atendido."}, status_code=409)
    error = save_order(body)
    if error:
        return error
    updated = inbox.set_status(item_id, "accepted")
    reply_to_customer(item, (body.reply or "").strip() or DEFAULT_ACCEPTED)
    return updated


@app.post("/api/inbox/{item_id}/reject")
def reject_inbox(item_id: str, body: RejectIn | None = None):
    item = get_item_or_404(item_id)
    if item["status"] != "pending":
        return JSONResponse({"detail": "El pedido ya fue atendido."}, status_code=409)
    updated = inbox.set_status(item_id, "rejected")
    reply_to_customer(item, ((body.reply if body else None) or "").strip() or DEFAULT_REJECTED)
    return updated


@app.get("/api/replies")
def replies():
    return REPLIES


@app.get("/api/telegram")
def telegram_status():
    return telegram_bot.status()


@app.get("/api/metrics")
def metrics():
    items = []
    for path in sorted(config.RESULTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append({"name": path.stem, "mode": data["mode"], "split": data["split"],
                          "notes": data["notes"], "wer": data["wer"],
                          "fields_correct": data["fields_correct"],
                          "total_seconds_mean": data["total_seconds"]["mean"]})
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return items


@app.get("/{path:path}", include_in_schema=False)
def spa(path: str):
    if path.startswith("api/") or not DIST_DIR.is_dir():
        raise HTTPException(404, "Not found")
    candidate = (DIST_DIR / path).resolve()
    if path and candidate.is_file() and DIST_DIR.resolve() in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(DIST_DIR / "index.html")


def main():
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-models", action="store_true")
    parser.add_argument("--no-telegram", action="store_true")
    parser.add_argument("--modes", default=DEFAULT_MODE, help="comma-separated modes to load at startup")
    args = parser.parse_args()
    modes = [] if args.no_models else [name for name in args.modes.split(",") if name]
    STARTUP_MODES[:] = modes
    state["telegram"] = not args.no_telegram
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
