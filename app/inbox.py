import json
import threading
import uuid
from datetime import datetime

from receipt import config

INBOX_DIR = config.DATA_DIR / "inbox"
lock = threading.RLock()


def inbox_file():
    return INBOX_DIR / "inbox.json"


def read_items():
    path = inbox_file()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def write_items(items):
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    temp = inbox_file().with_suffix(".tmp")
    temp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(inbox_file())


def new_id():
    return uuid.uuid4().hex[:6]


def create(customer, result, item_id=None, source="telegram"):
    item_id = item_id or new_id()
    item = {"id": item_id, "received_at": datetime.now().isoformat(timespec="seconds"), "source": source,
            "customer": customer, "status": "pending", "audio_url": f"/api/inbox/{item_id}/audio",
            "result": result}
    with lock:
        items = read_items()
        items.append(item)
        write_items(items)
    return item


def list_today(status=None):
    today = datetime.now().date().isoformat()
    with lock:
        items = read_items()
    items = [item for item in items if item["received_at"].startswith(today)]
    if status:
        items = [item for item in items if item["status"] == status]
    return list(reversed(items))


def get(item_id):
    with lock:
        return next((item for item in read_items() if item["id"] == item_id), None)


def set_status(item_id, status):
    with lock:
        items = read_items()
        for item in items:
            if item["id"] == item_id:
                item["status"] = status
                write_items(items)
                return item
    return None


def audio_path(item_id):
    return INBOX_DIR / f"{item_id}.ogg"
