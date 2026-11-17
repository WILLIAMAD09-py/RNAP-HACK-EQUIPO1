import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
CATALOG_PATH = DATA_DIR / "catalog.csv"
NOTES_PATH = DATA_DIR / "notes.csv"
SPLITS_PATH = DATA_DIR / "splits.csv"
ORDERS_PATH = DATA_DIR / "orders.csv"
RESULTS_DIR = ROOT / "results"

SIMILARITY_THRESHOLD = 0.6

MODES = {
    "baseline": {
        "whisper": "openai/whisper-small",
        "extractor": "rules",
        "embeddings": False,
        "vocabulary_prompt": False,
        "threshold": SIMILARITY_THRESHOLD,
    },
    "pretrained": {
        "whisper": "openai/whisper-medium",
        "extractor": "llm",
        "embeddings": False,
        "vocabulary_prompt": False,
        "threshold": SIMILARITY_THRESHOLD,
    },
    "solution": {
        "whisper": "openai/whisper-small",
        "extractor": "hybrid",
        "embeddings": True,
        "vocabulary_prompt": True,
        "threshold": SIMILARITY_THRESHOLD,
    },
}

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = os.environ.get("RECEIPT_OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M")
OLLAMA_TIMEOUT_SECONDS = 60
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SEED = 42
SPLIT_RATIOS = {"train": 0.6, "val": 0.2, "test": 0.2}
SAMPLE_RATE = 16000
