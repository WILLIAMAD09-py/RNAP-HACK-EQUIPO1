"""Extraccion de campos de ticket usando un modelo Transformer/LLM local (Ollama).

Justificacion del modelo Transformer:
- Arquitectura: Transformer decoder-only (qwen3:4b), ejecutado localmente via Ollama.
- Por que ese tamaño: 4B parametros equilibra calidad de extraccion JSON y velocidad
  en CPU/GPU de consumo (RTX 5050 Laptop, 8 GB). Modelos mas grandes (7B+) no caben
  comodamente con Whisper cargado en la misma GPU; modelos mas pequeños (1B-3B)
  pierden precisión en numeros y medidas en espanol.
- Idioma espanol: Qwen3 tiene entrenamiento multilingue que incluye espanol,
  adecuado para notas de voz de clientes en Monterrey (Mexico).
- Sin ajuste fino: se usa preentrenado con prompt estructurado, cumpliendo
  "preentrenado sin ajuste" de la Fase 1 y extendiendolo en Fase 2.
- Sin claves de API: se conecta a Ollama local en localhost:11434, sin credenciales.
- Respaldo: si Ollama no responde, se usa extraccion con reglas (rules.py) para que
  la demo nunca se caiga.
"""

from __future__ import annotations

import json
import re
from typing import Optional

import requests

from ..ticket import Ticket
from .rules import extraer_con_reglas

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:4b"


class ExtraccionTransformer:
    def __init__(self, modelo: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.modelo = modelo
        self.host = host.rstrip("/")

    def _prompt(self, transcripcion: str) -> str:
        return (
            "Eres un asistente que extrae campos de pedido de ferreteria a partir de "
            "una transcripcion de nota de voz en espanol. Devuelve SOLO un objeto JSON "
            "valido, sin texto adicional. Campos: cliente, producto, cantidad, medida, "
            "hora_entrega. Si un campo no se menciona, usa cadena vacia o null. "
            "Convierte numeros escritos (cincuenta, doce) a digitos. "
            f"Transcripcion: {transcripcion}"
        )

    def _llm_disponible(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def _extraer_con_llm(self, transcripcion: str) -> Optional[dict]:
        if not self._llm_disponible():
            return None
        payload = {
            "model": self.modelo,
            "prompt": self._prompt(transcripcion),
            "stream": False,
            "format": "json",
        }
        try:
            r = requests.post(f"{self.host}/api/generate", json=payload, timeout=60)
            if r.status_code != 200:
                return None
            texto = r.json().get("response", "")
            match = re.search(r"\{.*\}", texto, re.DOTALL)
            if not match:
                return None
            datos = json.loads(match.group(0))
            return datos
        except Exception:
            return None

    def extraer(self, transcripcion: str, catalogo) -> Ticket:
        datos = self._extraer_con_llm(transcripcion)
        if datos is None:
            return extraer_con_reglas(transcripcion, catalogo)
        ticket = Ticket(transcripcion=transcripcion)
        ticket.cliente = str(datos.get("cliente", "") or "")
        ticket.producto = str(datos.get("producto", "") or "")
        cantidad = datos.get("cantidad")
        if cantidad is not None and str(cantidad).strip() != "":
            try:
                ticket.cantidad = float(str(cantidad).replace(",", ".").strip())
            except (ValueError, TypeError):
                ticket.cantidad = None
        ticket.medida = str(datos.get("medida", "") or "")
        ticket.hora_entrega = str(datos.get("hora_entrega", "") or "")
        return ticket
