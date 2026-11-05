# App

Gradio interface for Receipt. It only calls `receipt.pipeline`, with no order logic of its own.

The interface must:

- Record with the microphone or upload an audio file
- Show the transcript and an editable ticket
- Highlight the fields that need confirmation
- Add the confirmed order to the day's list
