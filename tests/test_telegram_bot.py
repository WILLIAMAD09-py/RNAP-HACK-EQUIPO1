import pytest

from app import inbox, telegram_bot
from receipt.pipeline import PipelineResult
from receipt.ticket import Ticket


class FakeResponse:
    def __init__(self, payload=None, content=b""):
        self.payload = payload
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"ok": True, "result": self.payload}


@pytest.fixture
def sent(tmp_path, monkeypatch):
    monkeypatch.setattr(inbox, "INBOX_DIR", tmp_path / "inbox")
    monkeypatch.setitem(telegram_bot.state, "token", "TOKEN")
    messages = []

    def fake_post(url, data=None, timeout=None):
        if url.endswith("/sendMessage"):
            messages.append(data["text"])
            return FakeResponse({})
        if url.endswith("/getFile"):
            return FakeResponse({"file_path": "voice/file.oga"})
        return FakeResponse({})

    monkeypatch.setattr(telegram_bot.httpx, "post", fake_post)
    monkeypatch.setattr(telegram_bot.httpx, "get", lambda url, timeout=None: FakeResponse(content=b"ogg"))
    return messages


def voice_message():
    return {"update_id": 1, "message": {"chat": {"id": 77}, "voice": {"file_id": "F"},
                                         "from": {"first_name": "Ana", "last_name": "Lopez", "username": "ana"}}}


def build(result):
    return {"transcription": result.transcription, "ticket": {"cliente": result.ticket.cliente},
            "review_fields": list(result.ticket.review_fields)}


def test_voice_note_creates_inbox_item_with_telegram_name(sent, monkeypatch):
    monkeypatch.setitem(telegram_bot.state, "build_result", build)
    ticket = Ticket(None, "CAB-003", "Cable", 50, "calibre 12", "15:00", ["cliente", "medida"])
    seen = {}

    def fake_process(path, mode):
        seen["mode"] = mode
        return PipelineResult("texto", ticket, 1.0, 0.5, False)

    monkeypatch.setattr(telegram_bot.pipeline, "process_audio", fake_process)
    telegram_bot.handle_update(voice_message())
    assert sent == [telegram_bot.RECEIVED_TEXT]
    assert seen["mode"] == "solution"
    item = inbox.list_today()[0]
    assert item["customer"] == {"name": "Ana Lopez", "username": "ana", "chat_id": 77}
    assert item["result"]["ticket"]["cliente"] == "Ana Lopez"
    assert item["result"]["review_fields"] == ["medida"]
    assert inbox.audio_path(item["id"]).read_bytes() == b"ogg"


def test_processing_failure_sends_friendly_error(sent, monkeypatch):
    def boom(path, mode):
        raise RuntimeError("bad")

    monkeypatch.setattr(telegram_bot.pipeline, "process_audio", boom)
    telegram_bot.handle_update(voice_message())
    assert sent == [telegram_bot.RECEIVED_TEXT, telegram_bot.ERROR_TEXT]
    assert inbox.list_today() == []


def test_text_message_gets_help(sent):
    telegram_bot.handle_update({"update_id": 2, "message": {"chat": {"id": 5}, "text": "hola"}})
    assert sent == [telegram_bot.HELP_TEXT]


def test_send_message_never_raises(monkeypatch):
    monkeypatch.setitem(telegram_bot.state, "token", "TOKEN")

    def boom(*args, **kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(telegram_bot.httpx, "post", boom)
    assert telegram_bot.send_message(1, "hola") is False
