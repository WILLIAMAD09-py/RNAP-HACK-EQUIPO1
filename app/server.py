import argparse
import csv
import json
import tempfile
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from receipt import config, orders, pipeline
from receipt.catalog import load_catalog
from receipt.ticket import Ticket, normalize_time

DEFAULT_MODE = "solution"
DIST_DIR = Path(__file__).resolve().parent / "web" / "dist"
STARTUP_MODES = [DEFAULT_MODE]
state = {"models_loaded": False}


@asynccontextmanager
async def lifespan(app):
    for mode in STARTUP_MODES:
        pipeline.load_models(mode)
    state["models_loaded"] = bool(STARTUP_MODES)
    yield


app = FastAPI(title="Receipt", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"],
                   allow_headers=["*"])


class OrderIn(BaseModel):
    cliente: str | None = None
    producto_id: str | None = None
    cantidad: int | None = None
    medida: str | None = None
    hora_entrega: str | None = None


def product_dict(product, catalog):
    return {"id": product.id, "nombre": product.nombre, "categoria": product.categoria,
            "unidad": product.unidad, "medida": product.medida,
            "siblings": [other.id for other in catalog.siblings(product)]}


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
    ticket = result.ticket
    catalog = load_catalog()
    product = catalog.by_id.get(ticket.producto_id)
    siblings = catalog.siblings(product) if product else []
    return {
        "transcription": result.transcription,
        "ticket": {"cliente": ticket.cliente, "producto_id": ticket.producto_id, "producto": ticket.producto,
                   "cantidad": ticket.cantidad, "medida": ticket.medida, "hora_entrega": ticket.hora_entrega},
        "review_fields": list(ticket.review_fields),
        "extra_products": list(result.extra_products),
        "sibling_options": [{"id": other.id, "nombre": other.nombre, "medida": other.medida}
                            for other in siblings],
        "used_fallback": result.used_fallback,
        "timings": {"transcription": round(result.transcription_seconds, 3),
                    "extraction": round(result.extraction_seconds, 3),
                    "total": round(result.transcription_seconds + result.extraction_seconds, 3)},
    }


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
                       "producto_id": row["producto_id"], "producto": row["producto"],
                       "cantidad": int(quantity) if quantity.isdigit() else quantity,
                       "medida": row["medida"] or None, "hora_entrega": row["hora_entrega"] or None})
    return result


@app.get("/api/orders")
def list_orders():
    return todays_orders()


@app.post("/api/orders", status_code=201)
def create_order(body: OrderIn):
    product = load_catalog().by_id.get(body.producto_id or "")
    if not product:
        return JSONResponse({"detail": "Producto no válido o ausente."}, status_code=422)
    if not body.cantidad or body.cantidad <= 0:
        return JSONResponse({"detail": "La cantidad debe ser mayor que 0."}, status_code=422)
    hour = None
    if (body.hora_entrega or "").strip():
        hour = normalize_time(body.hora_entrega)
        if hour is None:
            return JSONResponse({"detail": "La hora debe tener formato HH:MM."}, status_code=422)
    ticket = Ticket(cliente=(body.cliente or "").strip() or None, producto_id=product.id,
                    producto=product.nombre, cantidad=body.cantidad,
                    medida=(body.medida or "").strip() or product.medida, hora_entrega=hour)
    orders.confirm(ticket, config.ORDERS_PATH)
    return todays_orders()


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
    parser.add_argument("--modes", default=DEFAULT_MODE, help="comma-separated modes to load at startup")
    args = parser.parse_args()
    modes = [] if args.no_models else [name for name in args.modes.split(",") if name]
    STARTUP_MODES[:] = modes
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
