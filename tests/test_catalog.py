from receipt.catalog import load_catalog
from receipt.numbers import normalize_text


def find(text):
    return load_catalog().find_by_synonym(normalize_text(text))


def test_catalog_loads_all_products():
    catalog = load_catalog()
    assert len(catalog.products) == 42
    assert catalog.by_id["TUB-001"].sinonimos[0] == "tubo de media"


def test_spoken_number_matches_synonym():
    assert find("cincuenta metros de cable del doce").product.id == "CAB-003"
    assert find("cable del 12").product.id == "CAB-003"


def test_longest_synonym_wins():
    assert find("un bulto de cemento blanco").product.id == "MAT-002"
    assert find("un bulto de cemento").product.id == "MAT-001"
    assert find("rollo de cable doce").product.id == "CAB-005"


def test_fraction_words_and_plurals():
    assert find("dos tubos de tres cuartos").product.id == "TUB-002"
    assert find("cien tornillos de pulgada y media").product.id == "FIJ-001"


def test_no_match():
    assert find("hola buenas tardes") is None


def test_siblings_share_family():
    catalog = load_catalog()
    ids = {product.id for product in catalog.siblings(catalog.by_id["CAB-003"])}
    assert {"CAB-001", "CAB-002", "CAB-004"} <= ids
    assert "TUB-001" not in ids


def test_is_unambiguous():
    catalog = load_catalog()
    assert catalog.is_unambiguous(normalize_text("cable del doce"), catalog.by_id["CAB-003"])
    assert catalog.is_unambiguous(normalize_text("bulto de cemento"), catalog.by_id["MAT-001"])
    assert not catalog.is_unambiguous(normalize_text("cemento"), catalog.by_id["MAT-001"])


def test_vocabulary_prompt_mentions_products():
    prompt = load_catalog().vocabulary_prompt()
    assert "tubo de media" in prompt and prompt.endswith(".")


def test_fraction_variants_find_same_product():
    for variant in ("media", "1/2", "media pulgada"):
        assert find(f"tubo de {variant}").product.id == "TUB-001"
    for variant in ("tres cuartos", "3 cuartos", "3/4"):
        assert find(f"tubo de {variant}").product.id == "TUB-002"
