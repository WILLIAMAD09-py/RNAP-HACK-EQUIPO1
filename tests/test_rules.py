import pytest

from receipt.catalog import load_catalog
from receipt.extraction import rules


def extract(text):
    return rules.extract(text, load_catalog())


def test_full_example():
    ticket = extract("Soy Carlos Treviño, mándame 50 metros de cable del doce para las tres de la tarde")
    assert ticket.cliente == "Carlos Treviño"
    assert ticket.producto_id == "CAB-003"
    assert ticket.cantidad == 50
    assert ticket.medida == "calibre 12"
    assert ticket.hora_entrega == "15:00"


def test_twelve_is_measure_when_spoken_first():
    ticket = extract("50 metros de cable del doce")
    assert (ticket.producto_id, ticket.cantidad, ticket.medida) == ("CAB-003", 50, "calibre 12")


def test_twelve_is_measure_when_spoken_last():
    ticket = extract("cable calibre 12, 50 metros")
    assert (ticket.producto_id, ticket.cantidad, ticket.medida) == ("CAB-003", 50, "calibre 12")


def test_digits_from_whisper():
    ticket = extract("Habla Ana López, necesito 3 tubos de tres cuartos conduit a las 10:30 de la mañana")
    assert ticket.cliente == "Ana López"
    assert ticket.producto_id == "TUB-002"
    assert ticket.cantidad == 3
    assert ticket.hora_entrega == "10:30"


@pytest.mark.parametrize("phrase, expected", [
    ("para las tres y media de la tarde", "15:30"),
    ("a las 8 de la noche", "20:00"),
    ("para las doce de la mañana", "00:00"),
    ("para las cuatro menos cuarto de la tarde", "15:45"),
    ("al mediodía", "12:00"),
    ("para las 15:20", "15:20"),
])
def test_times(phrase, expected):
    assert extract(f"un bulto de cemento {phrase}").hora_entrega == expected


def test_client_triggers():
    assert extract("De parte de Luis Garza quiero cemento").cliente == "Luis Garza"
    assert extract("hola soy jesus necesito cemento").cliente == "Jesus"
    assert extract("necesito cemento").cliente is None


def test_missing_fields_stay_empty():
    ticket = extract("necesito algo")
    assert ticket.empty_fields() == ["cliente", "producto_id", "cantidad", "medida", "hora_entrega"]


def test_article_means_one():
    assert extract("un bulto de cemento").cantidad == 1


def test_hour_without_period_gets_afternoon_for_1_to_6():
    assert extract("necesito cemento para las tres").hora_entrega == "15:00"
    assert extract("necesito cemento para las nueve").hora_entrega == "09:00"
    assert extract("necesito cemento mañana a las nueve de la mañana").hora_entrega == "09:00"


def test_fraction_does_not_break_quantity():
    ticket = extract("3 tubos de media")
    assert (ticket.producto_id, ticket.cantidad) == ("TUB-001", 3)
    ticket = extract("mandame 10 tubos de 3 cuartos")
    assert (ticket.producto_id, ticket.cantidad, ticket.medida) == ("TUB-002", 10, "3/4 pulgada")


def test_medio_dia_is_noon_not_a_half():
    ticket = extract("Soy Ana Leal, cinco tubos de media para medio día")
    assert (ticket.producto_id, ticket.hora_entrega) == ("TUB-001", "12:00")


BASELINE_NOTE = ("150 metros de cable THW, calibre 12 y dos cubetas de pintura vinílica blanca. "
                 "Necesito para las 3.30 pm, de parte del ingeniero Carlos Ruiz.")
SOLUTION_NOTE = ("150 metros de cable THW, calibre doce y dos cubetas de pintura vinílica blanca, "
                 "necesito para las tres 30 PM, de parte del ingeniero Carlos Ruiz")


@pytest.mark.parametrize("note", [BASELINE_NOTE, SOLUTION_NOTE])
def test_real_note_picks_first_product_with_its_quantity(note):
    ticket = extract(note)
    assert (ticket.cliente, ticket.producto_id, ticket.cantidad, ticket.medida, ticket.hora_entrega) == (
        "Carlos Ruiz", "CAB-003", 150, "calibre 12", "15:30")


@pytest.mark.parametrize("phrase, expected", [
    ("para las 3.30 pm", "15:30"),
    ("para las 3:30 p.m.", "15:30"),
    ("para las tres 30 PM", "15:30"),
    ("para las 9 30 am", "09:30"),
    ("para las 8 am", "08:00"),
])
def test_times_with_minutes_and_meridiem(phrase, expected):
    assert extract(f"2 bultos de cemento {phrase}").hora_entrega == expected


def test_minutes_do_not_swallow_quantities():
    ticket = extract("para las 3 20 bultos de cemento")
    assert ticket.cantidad == 20 and ticket.hora_entrega == "15:00"


def test_client_titles_are_skipped():
    assert extract("de parte del ingeniero Carlos Ruiz cemento").cliente == "Carlos Ruiz"
    assert extract("soy don Luis Garza cemento").cliente == "Luis Garza"
    assert extract("de parte del licenciado Pedro Gómez cemento").cliente == "Pedro Gómez"
