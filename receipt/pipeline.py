import time
from dataclasses import dataclass, field

from receipt import catalog as catalog_module
from receipt import transcription
from receipt.audio import load_audio
from receipt.config import MODES
from receipt.extraction import llm, rules
from receipt.numbers import normalize_text
from receipt.ticket import TICKET_FIELDS, Ticket


@dataclass
class PipelineResult:
    transcription: str
    ticket: Ticket
    transcription_seconds: float
    extraction_seconds: float
    used_fallback: bool
    extra_products: list = field(default_factory=list)


def get_mode(mode):
    if mode not in MODES:
        raise ValueError(f"Modo desconocido: {mode}. Opciones: {', '.join(MODES)}")
    return MODES[mode]


def load_models(mode):
    settings = get_mode(mode)
    start = time.perf_counter()
    transcription.load_model(settings["whisper"])
    if settings["embeddings"]:
        catalog_module.load_embedder()
    return time.perf_counter() - start


def hour_is_unambiguous(normalized):
    if rules.PERIOD_PATTERN.search(normalized) or rules.NOON_PATTERN.search(normalized):
        return True
    match = rules.TIME_PATTERN.search(normalized)
    return bool(match) and int(match.group(1)) not in range(1, 13)


def build_review_fields(ticket, text, catalog, from_embedding, has_extra_products=False):
    review = set(ticket.empty_fields())
    product = catalog.by_id.get(ticket.producto_id)
    if product and catalog.siblings(product):
        heard = not from_embedding and catalog.is_unambiguous(normalize_text(text), product)
        if not heard:
            review.add("medida")
    if has_extra_products:
        review.update(["producto_id", "cantidad"])
    if ticket.hora_entrega and not hour_is_unambiguous(normalize_text(text)):
        review.add("hora_entrega")
    return [name for name in TICKET_FIELDS if name in review]


def build_result(text, mode, transcription_seconds):
    settings = get_mode(mode)
    catalog = catalog_module.load_catalog()
    start = time.perf_counter()
    if settings["extractor"] == "llm":
        ticket, used_fallback = llm.extract(text, catalog)
    else:
        ticket, used_fallback = rules.extract(text, catalog), False
    from_embedding = False
    if settings["embeddings"] and ticket.producto_id is None:
        found = catalog.match_by_embedding(text)
        if found:
            ticket = ticket.with_product(found[0])
            from_embedding = True
    extra_products = [match.product.nombre for match in catalog.find_all(normalize_text(text))
                      if match.product.id != ticket.producto_id]
    ticket.review_fields = build_review_fields(ticket, text, catalog, from_embedding, bool(extra_products))
    extraction_seconds = time.perf_counter() - start
    return PipelineResult(text, ticket, transcription_seconds, extraction_seconds, used_fallback, extra_products)


def process_audio(path, mode):
    settings = get_mode(mode)
    start = time.perf_counter()
    audio = load_audio(path)
    vocabulary = catalog_module.load_catalog().vocabulary_prompt() if settings["vocabulary_prompt"] else None
    text = transcription.transcribe(audio, settings["whisper"], vocabulary)
    return build_result(text, mode, time.perf_counter() - start)


def process_text(text, mode):
    return build_result(text, mode, 0.0)
