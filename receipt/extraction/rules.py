import re

from receipt.numbers import normalize_text, numbers_to_digits, strip_accents
from receipt.ticket import Ticket

CLIENT_TRIGGER = re.compile(r"\b(?:soy|habla|de parte de|me llamo|mi nombre es)\s+", re.IGNORECASE)
NAME_TOKEN = re.compile(r"[^\W\d_]+|[^\w\s]|\d")
NAME_STOPWORDS = {"me", "mandas", "manda", "mandame", "necesito", "necesitamos", "quiero", "quisiera",
                  "ocupo", "requiero", "para", "por", "te", "le", "y", "que", "un", "una", "uno",
                  "de", "del", "el", "la", "los", "las", "a", "en", "con", "al", "favor", "hola",
                  "buenas", "buenos", "ando", "estoy", "dame", "pasame", "traeme", "envia",
                  "enviame", "ocupamos", "pido", "queria", "vengo", "mandeme", "surteme"}
MAX_NAME_WORDS = 3
TIME_PATTERN = re.compile(
    r"\b(?:a|para)\s+las?\s+(\d{1,2})(?!\d)(?::(\d{2}))?"
    r"(?:\s+(?:(y)\s+(media|cuarto|\d{2})|(menos)\s+(cuarto|\d{1,2})))?"
    r"(?:\s+horas)?(?:\s+(?:de|en|por)\s+la\s+(manana|tarde|noche|madrugada))?")
NOON_PATTERN = re.compile(r"\bmedio\s?dia\b")
PERIOD_PATTERN = re.compile(r"\b(?:de|en|por)\s+la\s+(?:manana|tarde|noche|madrugada)\b")
QUANTITY_PATTERN = re.compile(r"(?<![\d:/.])\d+(?![\d:/])")
ARTICLE_QUANTITY = re.compile(r"\b(?:un|una|uno)\b")


def extract_client(text):
    trigger = CLIENT_TRIGGER.search(text)
    if not trigger:
        return None
    words = []
    for token in NAME_TOKEN.finditer(text[trigger.end():]):
        word = token.group()
        folded = strip_accents(word).lower()
        if not word.isalpha() or folded in NAME_STOPWORDS or numbers_to_digits(folded) != folded:
            break
        if words and words[0][0].isupper() and word[0].islower():
            break
        words.append(word)
        if len(words) == MAX_NAME_WORDS:
            break
    if not words:
        return None
    name = " ".join(words)
    return name.title() if name.islower() else name


def extract_time(normalized):
    match = TIME_PATTERN.search(normalized)
    if not match:
        noon = NOON_PATTERN.search(normalized)
        if noon:
            return "12:00", normalized[:noon.start()] + " " + normalized[noon.end():]
        return None, normalized
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    period = match.group(7)
    if period is None and 1 <= hour <= 6:
        hour += 12
    elif period in ("tarde", "noche") and hour < 12:
        hour += 12
    elif period in ("manana", "madrugada", "noche") and hour == 12:
        hour = 0
    if match.group(3):
        minute = {"media": 30, "cuarto": 15}.get(match.group(4)) or int(match.group(4))
    elif match.group(5):
        hour -= 1
        minute = 45 if match.group(6) == "cuarto" else 60 - int(match.group(6))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None, normalized
    return f"{hour:02d}:{minute:02d}", normalized[:match.start()] + " " + normalized[match.end():]


def extract_quantity(remaining):
    number = QUANTITY_PATTERN.search(remaining)
    if number:
        return int(number.group())
    return 1 if ARTICLE_QUANTITY.search(remaining) else None


def extract(text, catalog):
    normalized = normalize_text(text)
    match = catalog.find_by_synonym(normalized)
    if match:
        normalized = normalized[:match.start] + " " + normalized[match.end:]
    hora, normalized = extract_time(normalized)
    ticket = Ticket(cliente=extract_client(text), cantidad=extract_quantity(normalized), hora_entrega=hora)
    return ticket.with_product(match.product) if match else ticket
