# Progress Log

## CP2 - 2026-11-08

- What we have done:
  - Problem: Ferretería Los Nogales receives orders as Spanish voice notes and types them by hand, with mistakes in quantities and sizes. Receipt turns a voice note into an order ticket with customer, product, quantity, size and delivery time.
  - Main metrics: WER for the transcript and percentage of correct ticket fields, plus processing time for each model.
  - Created the team repository for Receipt (Track 3: Voice Note to Order) and wrote the receipt/ application (audio, Whisper, rules and language model extraction, catalog matching, pipeline, dataset split, evaluation) with 82 unit tests.
  - Added data/catalog.csv with 42 products.
  - Recorded 30 voice notes (Jack, Jesús, William, Carlos). Three were exact copies and were left out, so data/notes.csv has 27 notes with their correct ticket.
  - Split the notes into 16 train, 6 validation and 5 test before any evaluation (seed 42).
  - Evaluated both models on the same 5 test notes on an RTX 5050 GPU:

    | Model | WER | Fields correct | Time per note (mean) |
    |---|---|---|---|
    | Baseline: Whisper small + regex rules | 18.3% | 60.0% | 4.69 s |
    | Pre-trained: Whisper medium + qwen3:4b, no fine-tuning | 12.7% | 76.0% | 11.66 s |

  - Wrote sections 1, 2 and 3 of notebooks/entrenamiento.ipynb with the comparison table and a short conclusion.

- What we haven't done yet:
  - Check the reference transcripts by ear: they are a draft from whisper-large-v3, a model we do not evaluate.
  - Record 3 more voice notes to reach the minimum of 30.
  - The test set has only 5 notes, so the numbers are preliminary.

- Next step:
  - Phase 2: build the Transformer solution, using the language model for product and size and the rules for time and quantity, then the Gradio interface.

- Who did what:
  - Jack: first repository structure, catalog and synthetic notebook.
  - Jesús: receipt/ application, answer key, split and evaluation.
  - William and Carlos: recorded their voice notes.
  - Everyone recorded voice notes. The team should complete this list before CP2.

---
