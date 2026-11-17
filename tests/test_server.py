import io
import json

import pytest
from fastapi.testclient import TestClient

from app import inbox, server, telegram_bot
from receipt import config
from receipt.pipeline import PipelineResult
from receipt.ticket import Ticket


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ORDERS_PATH", tmp_path / "orders.csv")
    monkeypatch.setattr(config, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(server, "STARTUP_MODES", [])
    monkeypatch.setattr(server, "ENV_PATH", tmp_path / ".env")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(inbox, "INBOX_DIR", tmp_path / "inbox")
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


def test_orders_off_catalog(client):
    payload = {"cliente": "Pedro", "producto_solicitado": "tornillos M4", "cantidad": 10}
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 201
    first = response.json()[0]
    assert first["producto"] == "tornillos M4"
    assert first["producto_id"] is None
    assert client.post("/api/orders", json={"cantidad": 10}).status_code == 422


def test_process_includes_off_catalog_fields(client, monkeypatch):
    monkeypatch.setattr(server.pipeline, "process_audio", lambda path, mode: fake_result())
    body = client.post("/api/process", files={"audio": ("nota.ogg", io.BytesIO(b"abc"))}).json()
    assert "producto_solicitado" in body["ticket"]
    assert body["ticket"]["fuera_de_catalogo"] is False


def test_telegram_disabled_without_token(client):
    assert client.get("/api/telegram").json() == {"enabled": False, "bot_username": None}


def test_replies_cover_required_ids(client):
    replies = client.get("/api/replies").json()
    ids = {reply["id"] for reply in replies}
    assert {"confirmado", "sin_existencia", "cambio_de_hora", "pedir_medida", "rechazado"} <= ids
    assert all(reply["text"] and reply["label"] for reply in replies)


def test_env_file_token(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(server, "ENV_PATH", tmp_path / ".env")
    assert server.read_env_token() == ""
    (tmp_path / ".env").write_text('OTHER=1\nTELEGRAM_BOT_TOKEN = "abc"\n', encoding="utf-8")
    assert server.read_env_token() == "abc"


def make_item(chat_id=9):
    ticket = {"cliente": "Pedro", "producto_id": "CAB-003", "cantidad": 50}
    return inbox.create({"name": "Pedro", "username": None, "chat_id": chat_id},
                        {"ticket": ticket, "review_fields": []}, "item01")


def test_inbox_accept_saves_order_and_replies(client, monkeypatch):
    sent = []
    monkeypatch.setattr(telegram_bot, "send_message", lambda chat_id, text: sent.append((chat_id, text)))
    make_item()
    assert client.get("/api/inbox?status=pending").json()[0]["id"] == "item01"
    body = {"cliente": "Pedro", "producto_id": "CAB-003", "cantidad": 50, "reply": "Listo, Pedro"}
    response = client.post("/api/inbox/item01/accept", json=body)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert sent == [(9, "Listo, Pedro")]
    assert len(client.get("/api/orders").json()) == 1
    assert client.post("/api/inbox/item01/accept", json=body).status_code == 409


def test_inbox_accept_invalid_keeps_pending(client, monkeypatch):
    monkeypatch.setattr(telegram_bot, "send_message", lambda chat_id, text: None)
    make_item()
    response = client.post("/api/inbox/item01/accept", json={"producto_id": "CAB-003", "cantidad": 0})
    assert response.status_code == 422
    assert inbox.get("item01")["status"] == "pending"


def test_inbox_reject_uses_default_reply(client, monkeypatch):
    sent = []
    monkeypatch.setattr(telegram_bot, "send_message", lambda chat_id, text: sent.append(text))
    make_item()
    response = client.post("/api/inbox/item01/reject")
    assert response.json()["status"] == "rejected"
    assert sent == [server.DEFAULT_REJECTED]


def test_inbox_audio_and_unknown(client):
    make_item()
    assert client.get("/api/inbox/item01/audio").status_code == 404
    inbox.audio_path("item01").write_bytes(b"ogg")
    response = client.get("/api/inbox/item01/audio")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/ogg"
    assert client.get("/api/inbox/nope/audio").status_code == 404
    assert client.post("/api/inbox/nope/reject").status_code == 404
