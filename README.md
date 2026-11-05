# RNAP Hack 2026 — Receipt

## Track 3: Voice Note to Order

A voice assistant that transcribes customer voice notes and extracts order fields using Whisper small + regex rules (baseline) and Whisper large + LLM extraction (pre-trained model), evaluated by WER and percentage of correct fields.

## Repository structure

```
.
├── README.md                # Product description in English
├── PROGRESS.md              # Checkpoint log in English
├── notebooks/
│   └── entrenamiento.ipynb  # Main notebook (technical report)
├── app/                     # Interface code (free technology)
├── requirements.txt         # Project dependencies
└── data/                    # Small audio samples or link to data source
```

## Checkpoints

- **CP1 & CP2** — Thursday, November 5, 2026 — Baseline phase (2.5%)
- **CP3 & CP4** — Thursday, November 12, 2026 — Prototype phase (5%)
- **v1.0** — Thursday, November 19, 2026 — Product phase (10%)

## License

MIT