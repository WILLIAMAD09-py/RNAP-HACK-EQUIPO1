# App

Gradio interface for Receipt. It only calls `receipt.pipeline`, with no order logic of its own.

The interface must:

- Record with the microphone or upload an audio file
- Show the transcript and an editable ticket
- Highlight the fields that need confirmation
- Add the confirmed order to the day's list

## Run

```bash
python -m app.app            # http://127.0.0.1:7860
python -m app.app --share    # public Gradio link
```

All three modes (`baseline`, `pretrained`, `solution`) are loaded once at startup. `solution` is the default.
