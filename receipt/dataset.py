from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import random

from receipt.config import NOTES_CSV, SEED, TRAIN_RATIO, VAL_RATIO, TEST_RATIO

B1_PENDING = True  # bloqueo B1: faltan las 30+ notas de voz (tarea F1.3a de persona)


@dataclass
class VoiceNote:
    audio_path: str
    transcription: str
    cliente: str
    producto: str
    cantidad: str
    medida: str
    hora_entrega: str
    synthetic: bool = False
    persona: str = ""
    ruido: str = ""
    velocidad: str = ""

    @property
    def ticket(self) -> dict[str, str]:
        return {
            "cliente": self.cliente,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "medida": self.medida,
            "hora_entrega": self.hora_entrega,
        }


def load_notes(path: Path | None = None) -> list[VoiceNote]:
    """Carga pares (audio, ticket correcto) desde data/notes.csv."""
    notes_path = path or NOTES_CSV
    notes: list[VoiceNote] = []
    if not notes_path.exists():
        return notes
    with notes_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notes.append(
                VoiceNote(
                    audio_path=row.get("audio_path", ""),
                    transcription=row.get("transcription", ""),
                    cliente=row.get("cliente", ""),
                    producto=row.get("producto", ""),
                    cantidad=row.get("cantidad", ""),
                    medida=row.get("medida", ""),
                    hora_entrega=row.get("hora_entrega", ""),
                    synthetic=row.get("synthetic", "").lower() == "true",
                    persona=row.get("persona", ""),
                    ruido=row.get("ruido", ""),
                    velocidad=row.get("velocidad", ""),
                )
            )
    return notes


def split_train_val_test(
    notes: list[VoiceNote],
    seed: int = SEED,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
) -> tuple[list[VoiceNote], list[VoiceNote], list[VoiceNote]]:
    """Divide notas en train/val/test con semilla fija (60/20/20 por defecto)."""
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError("train_ratio + val_ratio + test_ratio debe ser 1.0")

    rng = random.Random(seed)
    shuffled = list(notes)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(round(n * train_ratio))
    n_val = int(round(n * val_ratio))
    n_test = n - n_train - n_val

    train = shuffled[:n_train]
    val = shuffled[n_train : n_train + n_val]
    test = shuffled[n_train + n_val :]
    return train, val, test
