import json
import re

import jiwer
import numpy as np
import pandas as pd

from receipt import dataset, transcription
from receipt.config import MODES, RESULTS_DIR
from receipt.numbers import normalize_text, strip_accents
from receipt.ticket import TICKET_FIELDS, normalize_time


def word_error_rate(references, hypotheses):
    pairs = [(normalize_text(ref), normalize_text(hyp)) for ref, hyp in zip(references, hypotheses)]
    pairs = [pair for pair in pairs if pair[0]]
    if not pairs:
        return None
    return float(jiwer.wer([ref for ref, _ in pairs], [hyp for _, hyp in pairs]))


def _fold(value):
    return re.sub(r"\s+", " ", strip_accents(str(value or "")).lower()).strip()


def _as_number(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def score_fields(reference, ticket):
    return {
        "cliente": _fold(reference["cliente"]) == _fold(ticket.cliente),
        "producto_id": _fold(reference["producto_id"]) == _fold(ticket.producto_id),
        "cantidad": _as_number(reference["cantidad"]) == _as_number(ticket.cantidad),
        "medida": _fold(reference["medida"]) == _fold(ticket.medida),
        "hora_entrega": normalize_time(reference["hora_entrega"]) == normalize_time(ticket.hora_entrega),
    }


def _stats(values):
    return {"mean": round(float(np.mean(values)), 4), "p95": round(float(np.percentile(values, 95)), 4)}


def summarize(rows, mode, split, model_load_seconds, device):
    frame = pd.DataFrame(rows)
    per_field = {name: round(float(frame[f"{name}_ok"].mean()), 4) for name in TICKET_FIELDS}
    totals = frame["transcription_seconds"] + frame["extraction_seconds"]
    settings = MODES[mode]
    return {
        "mode": mode,
        "split": split,
        "whisper_model": settings["whisper"],
        "device": device,
        "extractor": settings["extractor"],
        "notes": len(frame),
        "wer": word_error_rate(frame["transcript_ref"], frame["transcript_hyp"]),
        "fields_correct": round(float(np.mean([frame[f"{n}_ok"].mean() for n in TICKET_FIELDS])), 4),
        "field_accuracy": per_field,
        "transcription_seconds": _stats(frame["transcription_seconds"]),
        "extraction_seconds": _stats(frame["extraction_seconds"]),
        "total_seconds": _stats(totals),
        "model_load_seconds": round(model_load_seconds, 4),
        "fallback_notes": int(frame["used_fallback"].sum()),
    }


def save_results(summary, rows, results_dir=RESULTS_DIR):
    results_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{summary['mode']}_{summary['split']}"
    (results_dir / f"{stem}.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(rows).to_csv(results_dir / f"{stem}_notes.csv", index=False, encoding="utf-8")


def evaluate(mode, split):
    from receipt import pipeline

    notes = dataset.load_split(split)
    model_load_seconds = pipeline.load_models(mode)
    pipeline.process_audio(notes.iloc[0]["audio_path"], mode)
    rows = []
    for _, note in notes.iterrows():
        result = pipeline.process_audio(note["audio_path"], mode)
        scores = score_fields(note, result.ticket)
        rows.append({
            "note_id": note["note_id"],
            "speaker": note["speaker"],
            "noise": note["noise"],
            "transcript_ref": note["transcript"],
            "transcript_hyp": result.transcription,
            "wer": word_error_rate([note["transcript"]], [result.transcription]),
            **{f"{name}_ok": scores[name] for name in TICKET_FIELDS},
            **{f"{name}_pred": getattr(result.ticket, name) for name in TICKET_FIELDS},
            "review_fields": " ".join(result.ticket.review_fields),
            "transcription_seconds": result.transcription_seconds,
            "extraction_seconds": result.extraction_seconds,
            "used_fallback": result.used_fallback,
        })
    device = transcription.load_model(MODES[mode]["whisper"])[2]
    summary = summarize(rows, mode, split, model_load_seconds, device)
    save_results(summary, rows)
    return summary


def comparison_table(results_dir=RESULTS_DIR):
    summaries = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(results_dir.glob("*.json"))]
    if not summaries:
        raise FileNotFoundError(f"No hay resultados en {results_dir}. Ejecuta primero: python -m receipt evaluate")
    header = ["Modo", "División", "Notas", "WER", "Campos OK"] + TICKET_FIELDS + [
        "Transcripción (s, media)", "Extracción (s, media)", "Total (s, p95)", "Carga (s)", "Con fallback", "Dispositivo"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for item in summaries:
        wer = "n/d" if item["wer"] is None else f"{item['wer']:.1%}"
        cells = [item["mode"], item["split"], item["notes"], wer, f"{item['fields_correct']:.1%}"]
        cells += [f"{item['field_accuracy'][name]:.1%}" for name in TICKET_FIELDS]
        cells += [f"{item['transcription_seconds']['mean']:.2f}", f"{item['extraction_seconds']['mean']:.2f}",
                  f"{item['total_seconds']['p95']:.2f}", f"{item['model_load_seconds']:.1f}", item["fallback_notes"], item.get("device", "n/d")]
        lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
    return "\n".join(lines)
