import re

_NUMBERS_ES = {
    "cero": 0, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "dieciséis": 16, "diecisiete": 17, "dieciocho": 18,
    "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintiun": 21,
    "veintidos": 22, "veintidós": 22, "veintitres": 23, "veintitrés": 23,
    "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26, "veintiséis": 26,
    "veintisiete": 27, "veintiocho": 28, "veintinueve": 29, "treinta": 30,
    "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70,
    "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100,
}


def _normalize(s):
    return re.sub(r"\s+", " ", str(s).lower().strip())


def _parse_number(text):
    text = _normalize(text)
    m = re.search(r"\b(\d{1,3})\b", text)
    if m:
        return int(m.group(1))
    for word in re.findall(r"\b[a-záéíóúñ]+\b", text):
        if word in _NUMBERS_ES:
            return _NUMBERS_ES[word]
    return None


def extract(text, catalog):
    text_norm = _normalize(text)
    producto = None
    medida = None
    unidad = None
    best_score = 0
    for row in catalog:
        sinos = str(row.get("sinonimos", ""))
        for sinonimo in sinos.split("|"):
            sinonimo = _normalize(sinonimo)
            if sinonimo and sinonimo in text_norm:
                score = len(sinonimo)
                if score > best_score:
                    best_score = score
                    producto = row.get("id")
                    medida = row.get("medida")
                    unidad = row.get("unidad")
    cantidad = _parse_number(text_norm)
    return {
        "producto": producto,
        "cantidad": cantidad,
        "medida": medida,
        "unidad": unidad,
    }


extraer_con_reglas = extract
