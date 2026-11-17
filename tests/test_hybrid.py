import json
import urllib.error

from receipt import pipeline
from receipt.config import MODES
from receipt.extraction import llm


def fake_reply(data):
    return lambda payload: {"message": {"content": json.dumps(data)}}


def test_hybrid_takes_quantity_and_hour_from_rules(monkeypatch):
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": "Pedro", "producto_id": "CAB-003", "cantidad": 12, "hora_entrega": "09:00"}))
    result = pipeline.process_text("soy Pedro, mándame 50 metros de cable del doce para las 3 de la tarde", "solution")
    assert result.ticket.cliente == "Pedro"
    assert result.ticket.producto_id == "CAB-003"
    assert result.ticket.cantidad == 50
    assert result.ticket.hora_entrega == "15:00"
    assert result.used_fallback is False


def test_hybrid_uses_llm_when_rules_find_nothing(monkeypatch):
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": None, "producto_id": "CAB-003", "cantidad": 7, "hora_entrega": "16:00"}))
    result = pipeline.process_text("cable del doce", "solution")
    assert result.ticket.cantidad == 7
    assert result.ticket.hora_entrega == "16:00"


def test_hybrid_falls_back_to_rules(monkeypatch):
    def down(payload):
        raise urllib.error.URLError("sin servidor")

    monkeypatch.setattr(llm, "call_ollama", down)
    result = pipeline.process_text("50 metros de cable del doce", "solution")
    assert result.used_fallback is True
    assert result.ticket.cantidad == 50


def test_other_modes_keep_their_extractor():
    assert MODES["baseline"]["extractor"] == "rules"
    assert MODES["pretrained"]["extractor"] == "llm"
    assert MODES["solution"]["extractor"] == "hybrid"


class FakeCatalogEmbeddings:
    def __init__(self, monkeypatch, match=None, similarity=0.0):
        from receipt.catalog import Catalog
        monkeypatch.setattr(Catalog, "match_by_embedding", lambda self, text, threshold=0.6: match)
        monkeypatch.setattr(Catalog, "product_similarity", lambda self, phrase, product: similarity)


def test_invented_product_becomes_out_of_catalog(monkeypatch):
    FakeCatalogEmbeddings(monkeypatch)
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": "Luis", "producto_solicitado": "tornillos M4", "producto_id": "CEM-001",
         "cantidad": 200, "hora_entrega": "17:00"}))
    result = pipeline.process_text("soy Luis, tráeme 200 tornillos M4 para las cinco", "solution")
    ticket = result.ticket
    assert ticket.fuera_de_catalogo is True
    assert (ticket.producto_id, ticket.producto, ticket.medida) == (None, None, None)
    assert ticket.producto_solicitado == "tornillos M4"
    assert ticket.cantidad == 200
    assert "producto_id" in ticket.review_fields


def test_null_product_from_llm_is_out_of_catalog(monkeypatch):
    FakeCatalogEmbeddings(monkeypatch)
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": None, "producto_solicitado": "tornillos M4", "producto_id": None,
         "cantidad": 10, "hora_entrega": None}))
    result = pipeline.process_text("10 tornillos M4", "solution")
    assert result.ticket.fuera_de_catalogo is True


def test_coherent_product_is_kept(monkeypatch):
    FakeCatalogEmbeddings(monkeypatch)
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": None, "producto_solicitado": "cable del doce", "producto_id": "CAB-003",
         "cantidad": 50, "hora_entrega": None}))
    result = pipeline.process_text("50 metros de cable del doce", "solution")
    assert result.ticket.producto_id == "CAB-003"
    assert result.ticket.fuera_de_catalogo is False
    assert result.ticket.producto_solicitado == "cable del doce"


def test_similar_phrase_is_kept_by_embeddings(monkeypatch):
    FakeCatalogEmbeddings(monkeypatch, similarity=0.9)
    monkeypatch.setattr(llm, "call_ollama", fake_reply(
        {"cliente": None, "producto_solicitado": "alambre grueso", "producto_id": "CAB-003",
         "cantidad": 5, "hora_entrega": None}))
    result = pipeline.process_text("5 de alambre grueso", "solution")
    assert result.ticket.producto_id == "CAB-003"
    assert result.ticket.fuera_de_catalogo is False
