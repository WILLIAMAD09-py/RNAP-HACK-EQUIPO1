import threading

import pytest

from app import inbox


@pytest.fixture(autouse=True)
def inbox_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(inbox, "INBOX_DIR", tmp_path / "inbox")


def test_create_get_and_status():
    item = inbox.create({"name": "Pedro", "username": None, "chat_id": 1}, {"ticket": {}}, "abc123")
    assert item["status"] == "pending"
    assert item["audio_url"] == "/api/inbox/abc123/audio"
    assert inbox.get("abc123")["customer"]["name"] == "Pedro"
    assert inbox.get("missing") is None
    assert inbox.set_status("abc123", "accepted")["status"] == "accepted"
    assert inbox.set_status("missing", "accepted") is None


def test_list_today_newest_first_and_filter():
    inbox.create({}, {}, "a")
    inbox.create({}, {}, "b")
    inbox.set_status("a", "rejected")
    assert [item["id"] for item in inbox.list_today()] == ["b", "a"]
    assert [item["id"] for item in inbox.list_today("pending")] == ["b"]


def test_old_items_are_not_listed():
    inbox.create({}, {}, "old")
    items = inbox.read_items()
    items[0]["received_at"] = "2020-01-01T00:00:00"
    inbox.write_items(items)
    assert inbox.list_today() == []


def test_concurrent_creates_keep_every_item():
    threads = [threading.Thread(target=inbox.create, args=({}, {})) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(inbox.read_items()) == 20
