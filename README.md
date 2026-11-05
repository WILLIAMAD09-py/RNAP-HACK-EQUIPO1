# Receipt — RNAP Hack 2026, Team 1

## Name and one-line description

**Receipt** turns a Spanish voice note from a hardware-store customer into an order ticket with five fields: customer, product, quantity, measure and delivery time. Built for Ferretería Los Nogales (a fictional store) as Track 3, "From Voice Note to Order".

## The problem and who has it

Ferretería Los Nogales delivers to construction sites around Monterrey. Its customers send orders as WhatsApp voice notes, and the staff types them by hand. They make mistakes in quantities and measures: once a customer asked for 12-gauge cable and received 50 meters of 10-gauge. Receipt reads the note automatically, shows an editable ticket, and flags the uncertain fields so a person confirms them before the order is added to the day's list.

## How it works

1. **Transcription:** Whisper (via `transformers`), forced to Spanish.
2. **Extraction:** regex rules (baseline) or a local language model through Ollama (`qwen3:4b-instruct-2507-q4_K_M`).
3. **Catalog matching:** product and measure come from `data/catalog.csv` (42 products). The `solution` mode adds a catalog-vocabulary prompt for Whisper and sentence-embedding matching.
4. **Review:** empty or doubtful fields are listed in `review_fields`. If Ollama is down, the rules are used and the result is marked as a fallback.

Modes: `baseline` (Whisper small + rules), `pretrained` (Whisper medium + language model), `solution` (Whisper small + language model + embeddings + vocabulary prompt).

### Install and run

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
ollama pull qwen3:4b-instruct-2507-q4_K_M                  # only for pretrained and solution

python -m receipt text "Soy Ana, 50 metros de cable del doce para las tres de la tarde" --mode baseline
python -m receipt process data/audio/<file>.ogg --mode baseline
python -m receipt split
python -m receipt evaluate --mode baseline --split val
python -m receipt compare
python -m pytest -q
```

Set `RECEIPT_OLLAMA_MODEL` to use a different Ollama model. Audio files are not stored in the repo.

## Repository structure

```
.
├── README.md
├── PROGRESS.md              # Checkpoint log
├── notebooks/
│   └── entrenamiento.ipynb  # Course report (reads results/, no logic of its own)
├── receipt/                 # Application logic: audio, Whisper, extraction, pipeline, evaluation
├── app/                     # Gradio interface
├── tests/                   # Unit tests (no models, network or GPU)
├── results/                 # Metrics of each evaluation run
├── data/                    # Catalog, answer key (notes.csv) and splits; audio is not committed
└── requirements.txt
```

## Results

Pending. No numbers yet: they will come from real runs saved in `results/`.

## What we have learned and what we would do next

Pending.

## Checkpoints

- **CP1 & CP2** — Thursday, November 5, 2026 — Baseline phase (2.5%)
- **CP3 & CP4** — Thursday, November 12, 2026 — Prototype phase (5%)
- **v1.0** — Thursday, November 19, 2026 — Product phase (10%)

## License

MIT
