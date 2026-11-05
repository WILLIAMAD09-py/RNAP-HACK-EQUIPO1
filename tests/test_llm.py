import json
import urllib.error

from receipt.catalog import load_catalog
from receipt.extraction import llm


def fake_reply(data):
    return {"message": {"content": json.dumps(data)}}


def test_uses_model_answer(monkeypatch):
    answer = {"cliente": "Carlos Treviño", "producto_id": "CAB-003", "cantidad": 50, "hora_entrega": "15:00"}
    monkeypatch.setattr(llm, "call_ollama", lambda payload: fake_reply(answer))
    ticket, used_fallback = llm.extract("soy Carlos Treviño, cable", load_catalog())
    assert used_fallback is False
    assert (ticket.cliente, ticket.producto_id, ticket.cantidad, ticket.medida, ticket.hora_entrega) == (
        "Carlos Treviño", "CAB-003", 50, "calibre 12", "15:00")


def test_invalid_values_become_empty(monkeypatch):
    answer = {"cliente": " ", "producto_id": "XXX-999", "cantidad": None, "hora_entrega": "tarde"}
    monkeypatch.setattr(llm, "call_ollama", lambda payload: fake_reply(answer))
    ticket, used_fallback = llm.extract("x", load_catalog())
    assert not used_fallback
    assert ticket.empty_fields() == ["cliente", "producto_id", "cantidad", "medida", "hora_entrega"]


def test_falls_back_to_rules_when_ollama_is_down(monkeypatch):
    def down(payload):
        raise urllib.error.URLError("conexión rechazada")

    monkeypatch.setattr(llm, "call_ollama", down)
    ticket, used_fallback = llm.extract("50 metros de cable del doce", load_catalog())
    assert used_fallback is True
    assert (ticket.producto_id, ticket.cantidad) == ("CAB-003", 50)


def test_falls_back_on_bad_json(monkeypatch):
    monkeypatch.setattr(llm, "call_ollama", lambda payload: {"message": {"content": "no es json"}})
    _, used_fallback = llm.extract("cemento", load_catalog())
    assert used_fallback is True


def test_http_failure_is_caught(monkeypatch):
    def refuse(*args, **kwargs):
        raise urllib.error.URLError("sin servidor")

    monkeypatch.setattr(llm.urllib.request, "urlopen", refuse)
    _, used_fallback = llm.extract("cemento", load_catalog())
    assert used_fallback is True


def test_request_has_catalog_and_json_schema(monkeypatch):
    sent = {}

    def capture(payload):
        sent.update(payload)
        return fake_reply({"cliente": None, "producto_id": None, "cantidad": None, "hora_entrega": None})

    monkeypatch.setattr(llm, "call_ollama", capture)
    llm.extract("hola", load_catalog())
    assert sent["stream"] is False and sent["options"]["temperature"] == 0
    assert sent["format"]["required"]
    assert "CAB-003" in sent["messages"][0]["content"]


def test_invented_client_is_discarded(monkeypatch):
    for invented in ("necesito", "Pedro Pérez"):
        answer = {"cliente": invented, "producto_id": "CAB-003", "cantidad": 3, "hora_entrega": None}
        monkeypatch.setattr(llm, "call_ollama", lambda payload, answer=answer: fake_reply(answer))
        ticket, _ = llm.extract("necesito tres cables del doce", load_catalog())
        assert ticket.cliente is None
