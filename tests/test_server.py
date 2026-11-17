import io
import json

import pytest
from fastapi.testclient import TestClient

from app import server
from receipt import config
from receipt.pipeline import PipelineResult
from receipt.ticket import Ticket


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ORDERS_PATH", tmp_path / "orders.csv")
    monkeypatch.setattr(config, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(server, "STARTUP_MODES", [])
    with TestClient(server.app) as test_client:
        yield test_client


def fake_result():
    ticket = Ticket("Pedro", "CAB-003", "Cable THW calibre 12", 50, "calibre 12", "15:00", ["medida"])
    return PipelineResult("cincuenta metros de cable del doce", ticket, 1.0, 0.5, False, ["Clavo"])


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok", "mode": "solution", "models_loaded": False}


def test_catalog_has_siblings(client):
    products = {item["id"]: item for item in client.get("/api/catalog").json()}
    assert "CAB-003" in products
    assert products["CAB-003"]["siblings"]
    assert set(products["CAB-003"]) == {"id", "nombre", "categoria", "unidad", "medida", "siblings"}


def test_process_returns_contract(client, monkeypatch):
    seen = {}

    def fake_process(path, mode):
        seen["suffix"] = path[path.rfind("."):]
        seen["mode"] = mode
        return fake_result()

    monkeypatch.setattr(server.pipeline, "process_audio", fake_process)
    response = client.post("/api/process", files={"audio": ("nota.ogg", io.BytesIO(b"abc"))},
                           data={"mode": "baseline"})
    assert response.status_code == 200
    body = response.json()
    assert seen == {"suffix": ".ogg", "mode": "baseline"}
    assert body["ticket"]["producto_id"] == "CAB-003"
    assert body["review_fields"] == ["medida"]
    assert body["extra_products"] == ["Clavo"]
    assert body["sibling_options"]
    assert set(body["sibling_options"][0]) == {"id", "nombre", "medida"}
    assert body["timings"] == {"transcription": 1.0, "extraction": 0.5, "total": 1.5}
    assert body["used_fallback"] is False


def test_process_without_audio_is_400(client):
    assert client.post("/api/process").status_code == 400


def test_process_failure_is_400(client, monkeypatch):
    def boom(path, mode):
        raise RuntimeError("bad file")

    monkeypatch.setattr(server.pipeline, "process_audio", boom)
    response = client.post("/api/process", files={"audio": ("nota.wav", io.BytesIO(b"abc"))})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_orders_roundtrip(client):
    assert client.get("/api/orders").json() == []
    payload = {"cliente": "Pedro", "producto_id": "CAB-003", "cantidad": 50, "medida": "calibre 12",
               "hora_entrega": "9:05"}
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 201
    first = response.json()[0]
    assert first["hora_entrega"] == "09:05"
    assert first["cantidad"] == 50
    assert first["producto"]
    client.post("/api/orders", json={**payload, "cliente": "Ana"})
    assert [order["cliente"] for order in client.get("/api/orders").json()] == ["Ana", "Pedro"]


@pytest.mark.parametrize("changes", [{"producto_id": "NOPE"}, {"cantidad": 0}, {"cantidad": None},
                                      {"hora_entrega": "tarde"}])
def test_orders_invalid_is_422(client, changes):
    payload = {"cliente": "Pedro", "producto_id": "CAB-003", "cantidad": 5, "medida": "", "hora_entrega": ""}
    response = client.post("/api/orders", json={**payload, **changes})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_metrics_reads_results(client, tmp_path):
    assert client.get("/api/metrics").json() == []
    results = tmp_path / "results"
    results.mkdir()
    (results / "solution_test.json").write_text(json.dumps({
        "mode": "solution", "split": "test", "notes": 5, "wer": 0.12, "fields_correct": 0.8,
        "total_seconds": {"mean": 3.4}}), encoding="utf-8")
    (results / "broken.json").write_text("{", encoding="utf-8")
    assert client.get("/api/metrics").json() == [
        {"name": "solution_test", "mode": "solution", "split": "test", "notes": 5, "wer": 0.12,
         "fields_correct": 0.8, "total_seconds_mean": 3.4}]


def test_unknown_api_path_is_404(client):
    assert client.get("/api/nothing").status_code == 404
