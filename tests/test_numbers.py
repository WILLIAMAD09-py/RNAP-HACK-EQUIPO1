import pytest

from receipt.numbers import normalize_text, numbers_to_digits


@pytest.mark.parametrize("spoken, expected", [
    ("cincuenta y dos", "52"),
    ("doscientos", "200"),
    ("doce", "12"),
    ("veintitrés", "23"),
    ("ciento veinte", "120"),
    ("mil quinientos", "1500"),
    ("dos mil", "2000"),
    ("treinta y un", "31"),
    ("cien metros", "100 metros"),
])
def test_converts_spanish_numbers(spoken, expected):
    assert numbers_to_digits(spoken) == expected


def test_keeps_measures_as_words():
    assert numbers_to_digits("tubo de tres cuartos") == "tubo de tres cuartos"
    assert numbers_to_digits("pulgada y media") == "pulgada y media"
    assert numbers_to_digits("taquete de un cuarto") == "taquete de un cuarto"


def test_converts_inside_sentence_and_keeps_punctuation():
    assert numbers_to_digits("Mándame cincuenta metros, por favor.") == "Mándame 50 metros, por favor."


def test_normalize_text_for_wer():
    assert normalize_text("¡Hola, Carlos Treviño! Cincuenta metros a las 3:30") == "hola carlos trevino 50 metros a las 3:30"
    assert normalize_text("tubo de 3/4.") == "tubo de 3/4"


def test_fractions_share_one_canonical_form():
    for variant in ("tres cuartos", "3 cuartos", "3/4"):
        assert normalize_text(f"tubo de {variant}") == "tubo de 3/4"
    for variant in ("media", "1/2", "media pulgada"):
        assert normalize_text(f"tubo de {variant}").startswith("tubo de 1/2")
    assert normalize_text("las tres y media") == "las 3 y media"
