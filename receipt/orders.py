import csv
from datetime import datetime

from receipt.config import ORDERS_PATH
from receipt.ticket import Ticket

COLUMNS = ["timestamp", "cliente", "producto_id", "producto", "cantidad", "medida", "hora_entrega"]


def confirm(ticket: Ticket, path=ORDERS_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if is_new:
            writer.writerow(COLUMNS)
        writer.writerow([datetime.now().isoformat(timespec="seconds"), ticket.cliente, ticket.producto_id,
                         ticket.producto, ticket.cantidad, ticket.medida, ticket.hora_entrega])
