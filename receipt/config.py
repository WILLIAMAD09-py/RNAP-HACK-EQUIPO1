from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CATALOG_CSV = DATA_DIR / "catalog.csv"
NOTES_CSV = DATA_DIR / "notes.csv"
SPLITS_CSV = DATA_DIR / "splits.csv"
AUDIO_DIR = DATA_DIR / "audio"

SEED = 42
TRAIN_RATIO = 0.60
VAL_RATIO = 0.20
TEST_RATIO = 0.20

TICKET_FIELDS = ("cliente", "producto", "cantidad", "medida", "hora_entrega")
