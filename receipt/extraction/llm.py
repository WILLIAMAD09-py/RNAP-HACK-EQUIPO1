from __future__ import annotations

import json
from typing import Optional

import requests

from ..ticket import Ticket

MODELO_DEFECTO = "qwen3:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_EXTRAER = """Eres un asistente que extrae los campos de un pedido de ferreteria a partir de una transcripcion de nota de voz en espanol.

Transcripcion:
{transcripcion}

Devuelve unicamente un objeto JSON con estas claves:
- cliente: nombre del cliente (string o vacio)
- producto: nombre del producto tal como se dijo (string o vacio)
- cantidad: numero (entero, decimal o null)
- medida: unidad o medida (string o vacio)
- hora_entrega: hora en formato HH:MM (string o vacio)

Si un dato no se dijo, dejalo vacio o null. No inventes campos. Devuelve solo el JSON, sin texto adicional."""


class ExtractoresLLM:
    def __init__(self, modelo: str = MODELO_DEFECTO, url: str = OLLAMA_URL):
        self.modelo = modelo
        self.url = url

    def extraer(self, transcripcion: str, catalogo=None) -> Ticket:
        prompt = PROMPT_EXTRAER.format(transcripcion=transcripcion)
        respuesta = self._consultar_llm(prompt)
        datos = self._parsear_json(respuesta)
        return Ticket(
            cliente=str(datos.get("cliente") or ""),
            producto=str(datos.get("producto") or ""),
            cantidad=self._numero(datos.get("cantidad")),
            medida=str(datos.get("medida") or ""),
            hora_entrega=str(datos.get("hora_entrega") or ""),
            transcripcion=transcripcion,
        )

    def _consultar_llm(self, prompt: str) -> str:
        try:
            respuesta = requests.post(
                self.url,
                json={"model": self.modelo, "prompt": prompt, "stream": False},
                timeout=60,
            )
            respuesta.raise_for_status()
            return str(respuesta.json().get("response", ""))
        except Exception:
            return ""

    @staticmethod
    def _parsear_json(texto: str) -> dict:
        try:
            inicio = texto.find("{")
            fin = texto.rfind("}")
            if inicio != -1 and fin != -1 and fin > inicio:
                return json.loads(texto[inicio:fin + 1])
        except Exception:
            pass
        return {}

    @staticmethod
    def _numero(valor) -> Optional[float]:
        if valor is None or valor == "":
            return None
        try:
            return float(valor)
        except Exception:
            return None


def extraer_con_llm(
    transcripcion: str, catalogo=None, modelo: str = MODELO_DEFECTO
) -> Ticket:
    return ExtractoresLLM(modelo=modelo).extraer(transcripcion, catalogo)
