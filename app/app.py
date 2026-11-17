import argparse
import csv
from datetime import date

import gradio as gr

from receipt import orders, pipeline
from receipt.catalog import load_catalog
from receipt.config import MODES, ORDERS_PATH
from receipt.ticket import Ticket, normalize_time

DEFAULT_MODE = "solution" if "solution" in MODES else next(iter(MODES))
CATALOG = load_catalog()
PRODUCT_CHOICES = [(f"{product.nombre} ({product.id})", product.id) for product in CATALOG.products]
FIELD_NAMES = ["cliente", "producto_id", "cantidad", "medida", "hora_entrega"]
ORDER_HEADERS = ["Hora", "Cliente", "Producto", "Cantidad", "Medida", "Entrega"]

CSS = """
.dudoso input, .dudoso textarea { background: #fff3b0 !important; border-color: #e0a800 !important; }
"""


def todays_orders():
    if not ORDERS_PATH.exists():
        return []
    today = date.today().isoformat()
    with open(ORDERS_PATH, encoding="utf-8", newline="") as handle:
        return [[row["timestamp"][11:], row["cliente"], row["producto"], row["cantidad"], row["medida"],
                 row["hora_entrega"]]
                for row in csv.DictReader(handle) if row["timestamp"].startswith(today)]


def sibling_choices(product_id):
    product = CATALOG.by_id.get(product_id)
    if not product:
        return []
    return [(f"{other.nombre} ({other.medida})", other.id) for other in CATALOG.siblings(product)]


def field_updates(ticket, review):
    values = [ticket.cliente or "", ticket.producto_id, ticket.cantidad, ticket.medida or "",
              ticket.hora_entrega or ""]
    return [gr.update(value=value, elem_classes=["dudoso"] if name in review else [])
            for name, value in zip(FIELD_NAMES, values)]


def run_pipeline(audio_path, mode):
    if not audio_path:
        return ("", *[gr.update()] * 5, "Graba o sube un audio primero.", gr.update(choices=[], visible=False), "")
    result = pipeline.process_audio(audio_path, mode)
    values = field_updates(result.ticket, result.ticket.review_fields)
    names = {"cliente": "cliente", "producto_id": "producto", "cantidad": "cantidad", "medida": "medida",
             "hora_entrega": "hora de entrega"}
    notes = []
    if result.ticket.review_fields:
        notes.append("Confirma antes de agregar, campos en amarillo: "
                     + ", ".join(names[name] for name in result.ticket.review_fields) + ".")
    if result.extra_products:
        notes.append("Se mencionaron otros productos: " + ", ".join(result.extra_products)
                     + ". Registra cada uno como pedido aparte.")
    if result.used_fallback:
        notes.append("Se usó el respaldo de reglas porque el modelo de lenguaje no respondió.")
    options = sibling_choices(result.ticket.producto_id)
    timing = (f"Transcripción: {result.transcription_seconds:.1f} s · Extracción: "
              f"{result.extraction_seconds:.1f} s · Total: "
              f"{result.transcription_seconds + result.extraction_seconds:.1f} s")
    return (result.transcription, *values, "\n\n".join(notes) or "Sin campos dudosos.",
            gr.update(choices=options, value=None, visible=bool(options)), timing)


def change_product(product_id):
    product = CATALOG.by_id.get(product_id)
    if not product:
        return gr.update(), gr.update(), gr.update(choices=[], visible=False)
    options = sibling_choices(product_id)
    return product.medida, gr.update(), gr.update(choices=options, value=None, visible=bool(options))


def pick_sibling(product_id):
    product = CATALOG.by_id.get(product_id)
    if not product:
        return gr.update(), gr.update()
    return product_id, product.medida


def confirm_order(cliente, producto_id, cantidad, medida, hora):
    product = CATALOG.by_id.get(producto_id)
    if not product or not cantidad:
        return "Faltan producto o cantidad.", todays_orders()
    time_value = normalize_time(hora)
    if hora and time_value is None:
        return "La hora debe tener formato HH:MM.", todays_orders()
    ticket = Ticket(cliente=(cliente or "").strip() or None, producto_id=product.id, producto=product.nombre,
                    cantidad=int(cantidad), medida=medida or product.medida, hora_entrega=time_value)
    orders.confirm(ticket)
    return f"Pedido agregado: {ticket.cantidad} x {ticket.producto}.", todays_orders()


def build_interface():
    with gr.Blocks(title="Receipt · Ferretería Los Nogales") as demo:
        gr.Markdown("# Receipt\nNota de voz a ticket de pedido para Ferretería Los Nogales.")
        with gr.Row():
            with gr.Column():
                mode = gr.Dropdown(list(MODES), value=DEFAULT_MODE, label="Modo")
                audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Nota de voz")
                process = gr.Button("Generar ticket", variant="primary")
                transcript = gr.Textbox(label="Transcripción", lines=3, interactive=False)
                timing = gr.Markdown()
            with gr.Column():
                notice = gr.Markdown()
                cliente = gr.Textbox(label="Cliente")
                producto = gr.Dropdown(PRODUCT_CHOICES, label="Producto", filterable=True)
                siblings = gr.Radio([], label="Otras medidas de este producto", visible=False)
                cantidad = gr.Number(label="Cantidad", precision=0, minimum=0)
                medida = gr.Textbox(label="Medida")
                hora = gr.Textbox(label="Hora de entrega (HH:MM)")
                confirm = gr.Button("Confirmar pedido", variant="primary")
                status = gr.Markdown()
        gr.Markdown("## Pedidos del día")
        table = gr.Dataframe(headers=ORDER_HEADERS, value=todays_orders, interactive=False)

        fields = [cliente, producto, cantidad, medida, hora]
        process.click(run_pipeline, [audio, mode], [transcript, *fields, notice, siblings, timing])
        producto.input(change_product, producto, [medida, producto, siblings])
        siblings.input(pick_sibling, siblings, [producto, medida])
        confirm.click(confirm_order, fields, [status, table])
    return demo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    for name in MODES:
        pipeline.load_models(name)
    build_interface().launch(server_name="127.0.0.1", server_port=args.port, share=args.share, css=CSS)


if __name__ == "__main__":
    main()
