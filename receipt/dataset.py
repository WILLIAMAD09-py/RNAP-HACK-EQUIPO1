import random

import pandas as pd

from receipt.catalog import load_catalog
from receipt.config import AUDIO_DIR, NOTES_PATH, SEED, SPLIT_RATIOS, SPLITS_PATH

NOTE_COLUMNS = ["note_id", "audio_file", "speaker", "noise", "speed", "transcript",
                "cliente", "producto_id", "cantidad", "medida", "hora_entrega"]
MAX_LISTED = 5


def _listed(items):
    shown = ", ".join(sorted(items)[:MAX_LISTED])
    return shown + (f" y {len(items) - MAX_LISTED} más" if len(items) > MAX_LISTED else "")


def load_notes(notes_path=NOTES_PATH, audio_dir=AUDIO_DIR, catalog=None, check_audio=True):
    if not notes_path.is_file():
        raise FileNotFoundError(f"No existe {notes_path}. Es el archivo con las respuestas correctas de las notas.")
    notes = pd.read_csv(notes_path, dtype=str, keep_default_na=False)
    missing_columns = [name for name in NOTE_COLUMNS if name not in notes.columns]
    if missing_columns:
        raise ValueError(f"A {notes_path.name} le faltan columnas: {', '.join(missing_columns)}")
    if notes.empty:
        raise ValueError(f"{notes_path.name} no tiene notas todavía")
    duplicated = notes.loc[notes["note_id"].duplicated(), "note_id"].tolist()
    if duplicated:
        raise ValueError(f"note_id repetido en {notes_path.name}: {_listed(duplicated)}")
    catalog = catalog or load_catalog()
    unknown = sorted(set(notes["producto_id"]) - set(catalog.by_id))
    if unknown:
        raise ValueError(f"producto_id que no existe en el catálogo: {_listed(unknown)}")
    if check_audio:
        absent = [name for name in notes["audio_file"] if not (audio_dir / name).is_file()]
        if absent:
            raise FileNotFoundError(f"Faltan {len(absent)} archivos de audio en {audio_dir}: {_listed(absent)}")
    notes["audio_path"] = [str(audio_dir / name) for name in notes["audio_file"]]
    return notes


def _interleave_by_noise(group, rng):
    queues = {}
    for noise, rows in group.groupby("noise", sort=True):
        ids = sorted(rows["note_id"])
        rng.shuffle(ids)
        queues[noise] = ids
    ordered = []
    while any(queues.values()):
        for noise in sorted(queues):
            if queues[noise]:
                ordered.append(queues[noise].pop())
    return ordered


def _assign_splits(ordered_ids):
    counts = {name: 0 for name in SPLIT_RATIOS}
    assignment = {}
    for position, note_id in enumerate(ordered_ids, start=1):
        name = max(SPLIT_RATIOS, key=lambda split: SPLIT_RATIOS[split] * position - counts[split])
        counts[name] += 1
        assignment[note_id] = name
    return assignment


def make_split(notes_path=NOTES_PATH, audio_dir=AUDIO_DIR, splits_path=SPLITS_PATH, catalog=None):
    notes = load_notes(notes_path, audio_dir, catalog)
    rng = random.Random(SEED)
    assignment = {}
    for speaker in sorted(notes["speaker"].unique()):
        group = notes[notes["speaker"] == speaker]
        assignment.update(_assign_splits(_interleave_by_noise(group, rng)))
    splits = pd.DataFrame({"note_id": notes["note_id"], "split": notes["note_id"].map(assignment)})
    splits.to_csv(splits_path, index=False)
    return splits


def load_split(split, notes_path=NOTES_PATH, audio_dir=AUDIO_DIR, splits_path=SPLITS_PATH, catalog=None):
    if split not in SPLIT_RATIOS:
        raise ValueError(f"División desconocida: {split}. Opciones: {', '.join(SPLIT_RATIOS)}")
    if not splits_path.is_file():
        raise FileNotFoundError(f"No existe {splits_path}. Ejecuta primero: python -m receipt split")
    notes = load_notes(notes_path, audio_dir, catalog)
    splits = pd.read_csv(splits_path, dtype=str, keep_default_na=False)
    outdated = sorted(set(notes["note_id"]) - set(splits["note_id"]))
    if outdated:
        raise ValueError(f"{splits_path.name} no incluye las notas {_listed(outdated)}. Ejecuta de nuevo: python -m receipt split")
    selected = splits.loc[splits["split"] == split, "note_id"]
    return notes[notes["note_id"].isin(selected)].reset_index(drop=True)
