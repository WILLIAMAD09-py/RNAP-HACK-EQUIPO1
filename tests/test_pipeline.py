import urllib.error

import pytest

from receipt import pipeline
from receipt.extraction import llm


def test_baseline_text():
    result = pipeline.process_text(
        "Soy Carlos Treviño, mándame 50 metros de cable del doce para las tres de la tarde", "baseline")
    assert result.ticket.producto_id == "CAB-003"
    assert result.ticket.review_fields == []
    assert result.used_fallback is False
    assert result.transcription_seconds == 0.0


def test_missing_fields_are_flagged():
    result = pipeline.process_text("necesito cable del doce", "baseline")
    assert result.ticket.review_fields == ["cliente", "cantidad", "hora_entrega"]


def test_unheard_measure_is_flagged():
    clear = pipeline.process_text("Soy Ana, un bulto de cemento, para las 3 de la tarde", "baseline")
    assert clear.ticket.review_fields == []
    vague = pipeline.process_text("Soy Ana, 2 de cemento, para las 3 de la tarde", "baseline")
    assert vague.ticket.review_fields == ["medida"]


def test_fallback_is_reported(monkeypatch):
    def down(payload):
        raise urllib.error.URLError("sin servidor")

    monkeypatch.setattr(llm, "call_ollama", down)
    result = pipeline.process_text("50 metros de cable del doce", "pretrained")
    assert result.used_fallback is True
    assert result.ticket.producto_id == "CAB-003"


def test_unknown_mode():
    with pytest.raises(ValueError):
        pipeline.process_text("hola", "inexistente")


def test_hour_without_period_is_flagged():
    vague = pipeline.process_text("Soy Ana, 2 bultos de cemento para las 3", "baseline")
    assert vague.ticket.hora_entrega == "15:00"
    assert vague.ticket.review_fields == ["hora_entrega"]
    clear = pipeline.process_text("Soy Ana, 2 bultos de cemento para las 15:00", "baseline")
    assert clear.ticket.review_fields == []
    morning = pipeline.process_text("mañana a las nueve de la mañana, soy Ana, 2 bultos de cemento", "baseline")
    assert morning.ticket.review_fields == []
