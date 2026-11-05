from __future__ import annotations

import pandas as pd

from .config import CATALOG_CSV
from .ticket import Ticket
from .transcription import transcribir_archivo
from .extraction.rules import extraer_con_reglas

DEFAULT_MODE = "baseline"
MODE_PREENTRENADO = "preentrenado"


def _cargar_catalogo():
    df = pd.read_csv(CATALOG_CSV)
    return df.to_dict("records")


def _extraer_transformer(texto, catalogo):
    from .extraction.transformer import ExtraccionTransformer
    return ExtraccionTransformer().extraer(texto, catalogo)


def audio_a_ticket(ruta_audio, modo=DEFAULT_MODE):
    texto = transcribir_archivo(ruta_audio)
    catalogo = _cargar_catalogo()
    if modo == DEFAULT_MODE:
        campos = extraer_con_reglas(texto, catalogo)
    else:
        try:
            campos = _extraer_transformer(texto, catalogo)
        except Exception:
            campos = extraer_con_reglas(texto, catalogo)
    ticket = Ticket(
        cliente="",
        producto=campos.get("producto"),
        cantidad=campos.get("cantidad"),
        medida=campos.get("medida"),
        hora_entrega="",
        transcripcion=texto,
    )
    return ticket


run = audio_a_ticket
