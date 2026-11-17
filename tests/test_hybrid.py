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
