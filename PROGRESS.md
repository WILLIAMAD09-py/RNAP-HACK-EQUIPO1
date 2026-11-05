# Progress Log

## CP2 - 2026-11-05

- What we have done:
  - Problem: Ferretería Los Nogales receives orders as Spanish voice notes and types them by hand, with mistakes in quantities and sizes. Receipt turns a voice note into an order ticket with customer, product, quantity, size and delivery time.
  - Main metrics: WER for the transcript and percentage of correct ticket fields, plus processing time for each model.
  - Created the team repository for Receipt (Track 3: Voice Note to Order)
  - Set up repository structure (README.md, PROGRESS.md, notebooks/, app/, data/, requirements.txt)
  - Wrote receipt/ application logic (config, ticket, audio, numbers, catalog, transcription, extraction/rules+llm, pipeline, dataset, evaluation, orders)
  - Added data/catalog.csv with 42 products
  - Wrote notebooks/entrenamiento.ipynb sections 1, 2, and 3 (based on synthetic data from catalog)
  - Updated requirements.txt (added jiwer, av)

- What we haven't done yet:
  - Load and split real voice/audio data into train / validation / test (data/notes.csv has only the header)
  - Run Whisper small + regex baseline on real audio
  - Run larger Whisper + LLM extraction (pre-trained, no fine-tuning)
  - Generate results/ with WER, % of correct fields, and processing time

- Next step:
  - Complete F1.3b-F1.8 (load/split data, baseline and pre-trained model, WER and % campos correctos, tiempo, comparison table), then commit CP2 and push in class schedule

- Who did what:
  - To be defined by team members; each integrante needs at least one own commit in this phase (F1.10)

---