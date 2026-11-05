from receipt.catalog import load_catalog
from receipt.ticket import TICKET_FIELDS, Ticket, normalize_time


def test_ticket_fields():
    assert TICKET_FIELDS == ["cliente", "producto_id", "cantidad", "medida", "hora_entrega"]


def test_empty_fields_lists_missing_values():
    ticket = Ticket(cliente="Ana", cantidad=3)
    assert ticket.empty_fields() == ["producto_id", "medida", "hora_entrega"]


def test_with_product_fills_catalog_data():
    product = load_catalog().by_id["CAB-003"]
    ticket = Ticket(cliente="Ana").with_product(product)
    assert (ticket.producto_id, ticket.medida) == ("CAB-003", "calibre 12")
    assert ticket.producto == product.nombre


def test_normalize_time():
    assert normalize_time("3:05") == "03:05"
    assert normalize_time("15:00:00") == "15:00"
    assert normalize_time("25:00") is None
    assert normalize_time("tres") is None
    assert normalize_time(None) is None
