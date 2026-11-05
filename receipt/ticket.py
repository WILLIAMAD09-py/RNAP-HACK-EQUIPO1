import re
from dataclasses import dataclass, field, replace

TICKET_FIELDS = ["cliente", "producto_id", "cantidad", "medida", "hora_entrega"]


@dataclass
class Ticket:
    cliente: str | None = None
    producto_id: str | None = None
    producto: str | None = None
    cantidad: int | None = None
    medida: str | None = None
    hora_entrega: str | None = None
    review_fields: list[str] = field(default_factory=list)

    def with_product(self, product):
        return replace(self, producto_id=product.id, producto=product.nombre, medida=product.medida)

    def empty_fields(self):
        return [name for name in TICKET_FIELDS if getattr(self, name) in (None, "")]


def normalize_time(value):
    if value is None:
        return None
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})(?::\d{2})?\s*", str(value))
    if not match:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"
