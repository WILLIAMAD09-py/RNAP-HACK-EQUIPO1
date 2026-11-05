import re
import unicodedata

UNITS = {"un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
         "seis": 6, "siete": 7, "ocho": 8, "nueve": 9}
SMALL = {"cero": 0, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
         "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13,
         "catorce": 14, "quince": 15, "dieciseis": 16, "diecisiete": 17, "dieciocho": 18,
         "diecinueve": 19, "veintiun": 21, "veintiuno": 21, "veintiuna": 21,
         "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
         "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29}
TENS = {"veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60,
        "setenta": 70, "ochenta": 80, "noventa": 90}
HUNDREDS = {"cien": 100, "ciento": 100}
HUNDREDS.update({"doscientos": 200, "doscientas": 200, "trescientos": 300, "trescientas": 300,
                 "cuatrocientos": 400, "cuatrocientas": 400, "quinientos": 500,
                 "quinientas": 500, "seiscientos": 600, "seiscientas": 600,
                 "setecientos": 700, "setecientas": 700, "ochocientos": 800,
                 "ochocientas": 800, "novecientos": 900, "novecientas": 900})
FRACTION_WORDS = {"cuarto", "cuartos", "octavo", "octavos", "medios", "tercios",
                  "dieciseisavos", "quintos"}
MAX_PHRASE_WORDS = 8


def strip_accents(text):
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _below_thousand(tokens, start):
    index = start
    value = 0
    if index < len(tokens) and tokens[index] in HUNDREDS:
        value += HUNDREDS[tokens[index]]
        index += 1
    if index < len(tokens):
        token = tokens[index]
        if token in SMALL:
            value += SMALL[token]
            index += 1
        elif token in TENS:
            value += TENS[token]
            index += 1
            if index + 1 < len(tokens) and tokens[index] == "y" and tokens[index + 1] in UNITS:
                value += UNITS[tokens[index + 1]]
                index += 2
    return (value, index) if index > start else None


def _parse_number(tokens):
    first = _below_thousand(tokens, 0)
    if first and first[1] < len(tokens) and tokens[first[1]] == "mil":
        value, index = first[0] * 1000, first[1] + 1
    elif tokens and tokens[0] == "mil":
        value, index = 1000, 1
    else:
        return first
    rest = _below_thousand(tokens, index)
    if rest:
        value += rest[0]
        index = rest[1]
    return value, index


def _word_positions(pieces, start):
    positions = [start]
    while len(positions) < MAX_PHRASE_WORDS:
        gap, nxt = positions[-1] + 1, positions[-1] + 2
        if nxt < len(pieces) and re.fullmatch(r"\s+", pieces[gap]) and re.fullmatch(r"\w+", pieces[nxt]):
            positions.append(nxt)
        else:
            break
    return positions


def numbers_to_digits(text):
    pieces = re.findall(r"\w+|\W+", text)
    output = []
    index = 0
    while index < len(pieces):
        if not re.fullmatch(r"\w+", pieces[index]):
            output.append(pieces[index])
            index += 1
            continue
        positions = _word_positions(pieces, index)
        tokens = [strip_accents(pieces[position]).lower() for position in positions]
        parsed = _parse_number(tokens)
        if parsed:
            value, count = parsed
            following = tokens[count] if count < len(tokens) else None
            if following not in FRACTION_WORDS:
                output.append(str(value))
                index = positions[count - 1] + 1
                continue
        output.append(pieces[index])
        index += 1
    return "".join(output)


def normalize_text(text):
    text = numbers_to_digits(strip_accents(text.lower()))
    text = re.sub(r"[^\w\s:/]", " ", text)
    text = re.sub(r"(?<!\d)[:/]|[:/](?!\d)", " ", text)
    return canonical_fractions(re.sub(r"\s+", " ", text).strip())


FRACTION_DENOMINATORS = {"cuarto": 4, "cuartos": 4, "octavo": 8, "octavos": 8}
FRACTION_PATTERN = re.compile(r"\b(\d+|[a-z]+) (cuartos?|octavos?)\b")
HALF_PATTERN = re.compile(r"(?<!\by )\b(?:media|medio(?! dia\b))\b")


def _fraction(match):
    word = match.group(1)
    numerator = word if word.isdigit() else UNITS.get(word) or SMALL.get(word)
    if numerator is None:
        return match.group(0)
    return f"{numerator}/{FRACTION_DENOMINATORS[match.group(2)]}"


def canonical_fractions(text):
    return HALF_PATTERN.sub("1/2", FRACTION_PATTERN.sub(_fraction, text))
