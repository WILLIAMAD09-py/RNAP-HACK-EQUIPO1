# Progress Log

## CP3 - 2026-11-17

- What we have done:
  - Built the Transformer solution (`--mode solution`): Whisper small with the catalog vocabulary as initial prompt, qwen3:4b for client, product and size, regex rules for quantity and time, and multilingual sentence embeddings to match the product when the language model finds none.
  - Evaluated it on the same 5 test notes on the RTX 5050 GPU, with no fallback:

    | Model | WER | Fields correct | Time per note (mean) |
    |---|---|---|---|
    | Baseline: Whisper small + regex rules | 18.3% | 60.0% | 4.69 s |
    | Pre-trained: Whisper medium + qwen3:4b | 12.7% | 76.0% | 11.66 s |
    | Solution: hybrid | 19.8% | 88.0% | 7.61 s |

  - Measured the effect of each parameter on validation: Whisper base, small and medium, with and without the vocabulary prompt, and similarity thresholds 0.4, 0.6 and 0.8.
  - Wrote sections 4 and 5 of the notebook with two charts and seven real error cases.
  - Replaced the Gradio interface with a FastAPI backend (`app/server.py`) and a React + Tailwind interface (`app/web/`). It works end to end with real voice notes in about 7 s.

- What we haven't done yet:
  - The test set has only 5 notes, so one error moves the score by 20 points.
  - The language model takes about 6 of the 7 seconds per note.
  - Check the interface with the microphone in the browser.

- Next step:
  - CP4: test the interface with live recordings and publish it. Phase 3: make extraction faster and add the cross-attention map.

- Who did what:
  - Jesús: hybrid solution, evaluation, notebook sections 4 and 5, new interface, with AI coding agents.
  - Carlos: commit with his changes in this phase.

---

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
