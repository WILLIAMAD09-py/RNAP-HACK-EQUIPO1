import re

from receipt.numbers import normalize_text, numbers_to_digits, strip_accents
from receipt.ticket import Ticket

CLIENT_TRIGGER = re.compile(r"\b(?:soy|habla|de parte del?|me llamo|mi nombre es)\s+", re.IGNORECASE)
NAME_TOKEN = re.compile(r"[^\W\d_]+|[^\w\s]|\d")
NAME_TITLES = {"ingeniero", "inge", "ing", "arquitecto", "arqui", "arq", "licenciado", "lic",
               "senor", "senora", "don", "dona", "sr", "sra"}
NAME_STOPWORDS = {"me", "mandas", "manda", "mandame", "necesito", "necesitamos", "quiero", "quisiera",
                  "ocupo", "requiero", "para", "por", "te", "le", "y", "que", "un", "una", "uno",
                  "de", "del", "el", "la", "los", "las", "a", "en", "con", "al", "favor", "hola",
                  "buenas", "buenos", "ando", "estoy", "dame", "pasame", "traeme", "envia",
                  "enviame", "ocupamos", "pido", "queria", "vengo", "mandeme", "surteme"}
MAX_NAME_WORDS = 3
TIME_PATTERN = re.compile(
    r"\b(?:a|para)\s+las?\s+(?P<hour>\d{1,2})(?!\d)"
    r"(?::(?P<colon_minutes>\d{2})|\s(?P<space_minutes>\d{2})(?!\d)"
    r"(?=\s*$|\s+(?:[ap]\s?m|horas|de|en|por|y)\b))?"
    r"(?:\s+(?:(?P<plus>y)\s+(?P<plus_amount>media|cuarto|\d{2})|(?P<minus>menos)\s+(?P<minus_amount>cuarto|\d{1,2})))?"
    r"(?:\s+horas)?"
    r"(?:\s+(?:de|en|por)\s+la\s+(?P<period>manana|tarde|noche|madrugada)|\s*(?P<meridiem>[ap])\s?m\b)?")
NOON_PATTERN = re.compile(r"\bmedio\s?dia\b")
PERIOD_PATTERN = re.compile(r"\b(?:de|en|por)\s+la\s+(?:manana|tarde|noche|madrugada)\b|\d\s?[ap]\s?m\b")
QUANTITY_PATTERN = re.compile(r"(?<![\d:/.])\d+(?![\d:/])")
ARTICLE_QUANTITY = re.compile(r"\b(?:un|una|uno)\b")


def extract_client(text):
    trigger = CLIENT_TRIGGER.search(text)
    if not trigger:
        return None
    words = []
    skipped_title = False
    for token in NAME_TOKEN.finditer(text[trigger.end():]):
        word = token.group()
        folded = strip_accents(word).lower()
        if not words and folded in NAME_TITLES:
            skipped_title = True
            continue
        if not words and skipped_title and word == ".":
            continue
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


def mask(text, start, end):
    return text[:start] + " " * (end - start) + text[end:]


def extract_time(normalized):
    match = TIME_PATTERN.search(normalized)
    if not match:
        noon = NOON_PATTERN.search(normalized)
        if noon:
            return "12:00", mask(normalized, noon.start(), noon.end())
        return None, normalized
    hour = int(match["hour"])
    minute = int(match["colon_minutes"] or match["space_minutes"] or 0)
    period = match["period"] or {"a": "manana", "p": "tarde", None: None}[match["meridiem"]]
    if period is None and 1 <= hour <= 6:
        hour += 12
    elif period in ("tarde", "noche") and hour < 12:
        hour += 12
    elif period in ("manana", "madrugada", "noche") and hour == 12:
        hour = 0
    if match["plus"]:
        minute = {"media": 30, "cuarto": 15}.get(match["plus_amount"]) or int(match["plus_amount"])
    elif match["minus"]:
        hour -= 1
        minute = 45 if match["minus_amount"] == "cuarto" else 60 - int(match["minus_amount"])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None, normalized
    return f"{hour:02d}:{minute:02d}", mask(normalized, match.start(), match.end())


def extract_quantity(remaining):
    number = QUANTITY_PATTERN.search(remaining)
    if number:
        return int(number.group())
    return 1 if ARTICLE_QUANTITY.search(remaining) else None


def extract(text, catalog):
    normalized = normalize_text(text)
    matches = catalog.find_all(normalized)
    hora, normalized = extract_time(normalized)
    if matches:
        limit = matches[1].start if len(matches) > 1 else len(normalized)
        remaining = mask(normalized[:limit], matches[0].start, matches[0].end)
    else:
        remaining = normalized
    ticket = Ticket(cliente=extract_client(text), cantidad=extract_quantity(remaining), hora_entrega=hora)
    return ticket.with_product(matches[0].product) if matches else ticket
