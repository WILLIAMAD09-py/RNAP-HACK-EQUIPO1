import json
import urllib.request

from receipt.config import OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS, OLLAMA_URL
from receipt.extraction import rules
from receipt.numbers import normalize_text, strip_accents
from receipt.ticket import Ticket, normalize_time

SCHEMA = {
    "type": "object",
    "properties": {
        "cliente": {"type": ["string", "null"]},
        "producto_id": {"type": ["string", "null"]},
        "cantidad": {"type": ["integer", "null"]},
        "hora_entrega": {"type": ["string", "null"]},
    },
    "required": ["cliente", "producto_id", "cantidad", "hora_entrega"],
}

SYSTEM_PROMPT = """Eres el capturista de pedidos de una ferretería en Monterrey. Recibes la transcripción de una nota de voz y devuelves un JSON con estos campos:
- cliente: nombre de quien pide, tal como se dijo, o null. Solo si la persona dice su nombre ("soy...", "habla...", "de parte de..."); si nadie lo dice, cliente es null. Nunca uses una palabra común como nombre.
- producto_id: el id del catálogo que corresponde al producto pedido, o null si ninguno coincide.
- cantidad: cuántas unidades se piden, como entero, o null.
- hora_entrega: hora de entrega en formato 24 horas HH:MM, o null.
Reglas: el calibre o la medida forman parte del producto y NO son la cantidad. Ejemplo: en "50 metros de cable del doce" la cantidad es 50 y el 12 es el calibre del producto. En "cable calibre 12, 50 metros" también. Convierte la hora a 24 horas: "las tres de la tarde" es "15:00". Si un dato no se dijo, usa null. Nunca inventes datos.

Catálogo (id | nombre | cómo lo piden los clientes):
"""


def build_messages(text, catalog):
    lines = [f"{p.id} | {p.nombre} | {' / '.join(p.sinonimos)}" for p in catalog.products]
    return [{"role": "system", "content": SYSTEM_PROMPT + "\n".join(lines)},
            {"role": "user", "content": text}]


def call_ollama(payload):
    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat", data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def ticket_from_data(data, catalog, text):
    cliente = data.get("cliente")
    cliente = cliente.strip() if isinstance(cliente, str) and cliente.strip() else None
    try:
        cantidad = int(round(float(data.get("cantidad"))))
    except (TypeError, ValueError):
        cantidad = None
    if cliente:
        first_word = strip_accents(cliente.split()[0]).lower()
        if first_word in rules.NAME_STOPWORDS or normalize_text(cliente) not in normalize_text(text):
            cliente = None
    ticket = Ticket(cliente=cliente, cantidad=cantidad if cantidad and cantidad > 0 else None,
                    hora_entrega=normalize_time(data.get("hora_entrega")))
    product = catalog.by_id.get(data.get("producto_id"))
    return ticket.with_product(product) if product else ticket


def extract(text, catalog):
    payload = {"model": OLLAMA_MODEL, "messages": build_messages(text, catalog), "stream": False,
               "format": SCHEMA, "options": {"temperature": 0}}
    try:
        reply = call_ollama(payload)
        return ticket_from_data(json.loads(reply["message"]["content"]), catalog, text), False
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return rules.extract(text, catalog), True
