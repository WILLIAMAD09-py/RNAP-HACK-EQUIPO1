from receipt.config import SAMPLE_RATE

LONG_FORM_SAMPLES = 30 * SAMPLE_RATE
MAX_NEW_TOKENS = 128
MAX_PROMPT_TOKENS = 120

_loaded = {}


def load_model(name):
    if name not in _loaded:
        import torch
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        processor = WhisperProcessor.from_pretrained(name)
        model = WhisperForConditionalGeneration.from_pretrained(name, dtype=dtype).to(device).eval()
        _loaded[name] = (processor, model, device, dtype)
    return _loaded[name]


def transcribe(audio, model_name, vocabulary=None):
    import torch

    processor, model, device, dtype = load_model(model_name)
    long_form = len(audio) > LONG_FORM_SAMPLES
    inputs = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt", **(
        {"truncation": False, "padding": "longest", "return_attention_mask": True} if long_form else {}))
    options = {"language": "es", "task": "transcribe", "max_new_tokens": MAX_NEW_TOKENS}
    if vocabulary:
        prompt_ids = processor.get_prompt_ids(vocabulary, return_tensors="pt")
        options["prompt_ids"] = prompt_ids[:MAX_PROMPT_TOKENS].to(device)
    if long_form:
        options["attention_mask"] = inputs.attention_mask.to(device)
        options["return_timestamps"] = True
    with torch.inference_mode():
        generated = model.generate(inputs.input_features.to(device, dtype), **options)
    return processor.batch_decode(generated, skip_special_tokens=True)[0].strip()
