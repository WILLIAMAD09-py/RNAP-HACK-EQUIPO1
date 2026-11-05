import json

import pandas as pd
import pytest

from receipt import evaluation
from receipt.ticket import TICKET_FIELDS, Ticket

REFERENCE = {"cliente": "Carlos Treviño", "producto_id": "CAB-003", "cantidad": "50",
             "medida": "calibre 12", "hora_entrega": "15:00"}


def test_wer_ignores_case_accents_punctuation_and_number_format():
    assert evaluation.word_error_rate(["Cincuenta metros, por favor."], ["50 metros por favor"]) == 0.0


def test_wer_counts_errors():
    assert evaluation.word_error_rate(["dos tres cuatro cinco"], ["2 3 cuatro siete"]) == pytest.approx(0.25)


def test_score_fields_all_correct():
    ticket = Ticket(cliente="carlos trevino", producto_id="CAB-003", cantidad=50,
                    medida="calibre 12", hora_entrega="15:00")
    assert all(evaluation.score_fields(REFERENCE, ticket).values())


def test_score_fields_detects_each_error():
    ticket = Ticket(cliente="Carlos", producto_id="CAB-002", cantidad=12,
                    medida="calibre 10", hora_entrega="03:00")
    assert not any(evaluation.score_fields(REFERENCE, ticket).values())


def test_hour_compares_as_hh_mm():
    reference = {**REFERENCE, "hora_entrega": "9:05"}
    assert evaluation.score_fields(reference, Ticket(hora_entrega="09:05"))["hora_entrega"]


def make_rows():
    base = {"transcript_ref": "cable del doce", "transcript_hyp": "cable del doce", "used_fallback": False}
    ok = {f"{name}_ok": True for name in TICKET_FIELDS}
    return [
        {**base, **ok, "transcription_seconds": 1.0, "extraction_seconds": 0.5},
        {**base, **ok, "cantidad_ok": False, "transcription_seconds": 3.0,
         "extraction_seconds": 0.5, "used_fallback": True},
    ]


def test_summary_and_saved_files(tmp_path):
    summary = evaluation.summarize(make_rows(), "baseline", "val", 12.3456, "cpu")
    assert summary["fields_correct"] == 0.9
    assert summary["field_accuracy"]["cantidad"] == 0.5
    assert summary["transcription_seconds"]["mean"] == 2.0
    assert summary["total_seconds"]["p95"] == pytest.approx(3.4)
    assert summary["fallback_notes"] == 1
    assert summary["model_load_seconds"] == 12.3456
    evaluation.save_results(summary, make_rows(), tmp_path)
    assert json.loads((tmp_path / "baseline_val.json").read_text(encoding="utf-8"))["notes"] == 2
    assert len(pd.read_csv(tmp_path / "baseline_val_notes.csv")) == 2


def test_comparison_table(tmp_path):
    summary = evaluation.summarize(make_rows(), "baseline", "val", 1.0, "cuda")
    evaluation.save_results(summary, make_rows(), tmp_path)
    table = evaluation.comparison_table(tmp_path)
    assert table.splitlines()[0].startswith("| Modo |")
    assert "| baseline | val | 2 |" in table
    assert "Dispositivo" in table and table.splitlines()[2].endswith("| cuda |")


def test_wer_fraction_forms_match():
    assert evaluation.word_error_rate(["tubo de tres cuartos"], ["tubo de 3 cuartos"]) == 0.0
