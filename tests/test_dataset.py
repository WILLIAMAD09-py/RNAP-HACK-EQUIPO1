import pandas as pd
import pytest

from receipt import dataset


def write_notes(tmp_path, rows):
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir(exist_ok=True)
    for row in rows:
        (audio_dir / row["audio_file"]).write_bytes(b"x")
    notes_path = tmp_path / "notes.csv"
    pd.DataFrame(rows, columns=dataset.NOTE_COLUMNS).to_csv(notes_path, index=False)
    return notes_path, audio_dir


def make_rows(speakers=("ana", "beto"), per_speaker=10):
    noises = ["silencio", "moderado", "fuerte"]
    rows = []
    for speaker in speakers:
        for i in range(per_speaker):
            rows.append({"note_id": f"{speaker}_{i:02d}", "audio_file": f"{speaker}_{i:02d}.wav",
                         "speaker": speaker, "noise": noises[i % 3], "speed": "normal",
                         "transcript": "cable del doce", "cliente": "Ana", "producto_id": "CAB-003",
                         "cantidad": "50", "medida": "calibre 12", "hora_entrega": "15:00"})
    return rows


def test_split_is_60_20_20_per_speaker_and_deterministic(tmp_path):
    notes_path, audio_dir = write_notes(tmp_path, make_rows())
    splits_path = tmp_path / "splits.csv"
    first = dataset.make_split(notes_path, audio_dir, splits_path)
    second = dataset.make_split(notes_path, audio_dir, splits_path)
    assert first.equals(second)
    merged = first.merge(pd.read_csv(notes_path), on="note_id")
    for _, group in merged.groupby("speaker"):
        assert group["split"].value_counts().to_dict() == {"train": 6, "val": 2, "test": 2}
    assert len(set(merged.loc[merged["split"] == "test", "noise"])) >= 2


def test_small_groups_still_give_a_20_percent_test_split(tmp_path):
    rows = make_rows(speakers=("ana", "beto", "caro"), per_speaker=7) + make_rows(speakers=("dani",), per_speaker=6)
    notes_path, audio_dir = write_notes(tmp_path, rows)
    splits = dataset.make_split(notes_path, audio_dir, tmp_path / "splits.csv")
    counts = splits["split"].value_counts().to_dict()
    assert counts["train"] == 16 and counts["test"] >= 5 and counts["val"] >= 5
    merged = splits.merge(pd.read_csv(notes_path), on="note_id")
    assert merged.loc[merged["split"] == "test", "speaker"].nunique() == 4


def test_load_split_returns_only_that_split(tmp_path):
    notes_path, audio_dir = write_notes(tmp_path, make_rows())
    splits_path = tmp_path / "splits.csv"
    dataset.make_split(notes_path, audio_dir, splits_path)
    test = dataset.load_split("test", notes_path, audio_dir, splits_path)
    assert len(test) == 4
    assert test["audio_path"].str.endswith(".wav").all()


def test_load_split_without_splits_file(tmp_path):
    notes_path, audio_dir = write_notes(tmp_path, make_rows(per_speaker=2))
    with pytest.raises(FileNotFoundError, match="python -m receipt split"):
        dataset.load_split("val", notes_path, audio_dir, tmp_path / "splits.csv")


def test_missing_audio_fails_clearly(tmp_path):
    notes_path, audio_dir = write_notes(tmp_path, make_rows(per_speaker=2))
    (audio_dir / "ana_00.wav").unlink()
    with pytest.raises(FileNotFoundError, match="ana_00.wav"):
        dataset.load_notes(notes_path, audio_dir)


def test_unknown_product_fails_clearly(tmp_path):
    rows = make_rows(per_speaker=2)
    rows[0]["producto_id"] = "ZZZ-001"
    notes_path, audio_dir = write_notes(tmp_path, rows)
    with pytest.raises(ValueError, match="ZZZ-001"):
        dataset.load_notes(notes_path, audio_dir)


def test_missing_columns_fail_clearly(tmp_path):
    notes_path = tmp_path / "notes.csv"
    pd.DataFrame({"note_id": ["a"]}).to_csv(notes_path, index=False)
    with pytest.raises(ValueError, match="faltan columnas"):
        dataset.load_notes(notes_path, tmp_path)
