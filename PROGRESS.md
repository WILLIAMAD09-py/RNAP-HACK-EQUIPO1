# Progress Log

## CP2 - 2026-11-05

### What we have done:
- Problem: Ferretería Los Nogales receives orders as Spanish voice notes and types them by hand, with mistakes in quantities and sizes. Receipt turns a voice note into an order ticket with customer, product, quantity, size and delivery time.
- Main metrics: WER for the transcript and percentage of correct ticket fields, plus processing time for each model.
- Built the Python application in receipt/: audio loading, Whisper transcription, rule baseline, language model extraction, catalog matching, data split and evaluation, with unit tests. It has only been checked with synthetic text-to-speech audio, so there are no project results yet.
- Created the team repository for Receipt (Track 3: Voice Note to Order)
- Set up repository structure (README.md, PROGRESS.md, notebooks/, app/, data/, requirements.txt)
- Defined Reto 3: Voice Note to Order

### What we haven't done yet:
- Load and split voice/audio data into train / validation / test
- Train Whisper small + regex baseline model
- Apply larger Whisper + LLM extraction (pre-trained, no fine-tuning)
- Write sections 1, 2, and 3 of the training notebook
- Fill the comparison table with WER and % of correct fields

### Next step:
- Load audio data, split it, train baseline and pre-trained model, and complete sections 1-3 of notebooks/entrenamiento.ipynb

### Who did what:
- To be defined by team members

---