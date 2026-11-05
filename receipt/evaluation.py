from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from receipt.config import NOTES_CSV, TICKET_FIELDS
from receipt.dataset import VoiceNote, load_notes, split_train_val_test
from receipt.ticket import Ticket

RESULTADOS_DIR = Path(__file__).resolve().parents[1] / "results"
ARCHIVO_METRICAS = RESULTADOS_DIR / "metrics_cp2.json"

MODELO_BASE = "Whisper small + reglas (base)"
MODELO_PREENTRENADO = "Whisper grande + LLM (preentrenado)"

MODO_BASE = "baseline"
MODO_PREENTRENADO = "preentrenado"


def _normalizar(texto) -> str:
    return " ".join(str(texto).lower().strip().split())


def _es_numerico(valor) -> bool:
    try:
        float(str(valor).replace(",", "."))
        return True
    except Exception:
        return False


def _numeros_iguales(predicho, correcto) -> bool:
    try:
        return abs(
            float(str(predicho).replace(",", "."))
            - float(str(correcto).replace(",", "."))
        ) < 1e-9
    except Exception:
        return False


def _distancia_levenshtein(palabras_a: list[str], palabras_b: list[str]) -> int:
    filas = len(palabras_a) + 1
    columnas = len(palabras_b) + 1
    anterior = list(range(columnas))
    for i in range(1, filas):
        actual = [i] + [0] * (columnas - 1)
        for j in range(1, columnas):
            costo = 0 if palabras_a[i - 1] == palabras_b[j - 1] else 1
            actual[j] = min(
                actual[j - 1] + 1,
                anterior[j] + 1,
                anterior[j - 1] + costo,
            )
        anterior = actual
    return anterior[-1]


def wer(referencia: str, hipotesi: str) -> float:
    ref = _normalizar(referencia)
    hyp = _normalizar(hipotesi)
    palabras_ref = ref.split()
    palabras_hyp = hyp.split()
    if not palabras_ref:
        return 0.0 if not palabras_hyp else 1.0
    return _distancia_levenshtein(palabras_ref, palabras_hyp) / len(palabras_ref)


def campos_correctos(predicho: Ticket, correcto) -> dict:
    resultado = {}
    for campo in TICKET_FIELDS:
        valor_p = getattr(predicho, campo, None)
        valor_c = correcto.get(campo) if isinstance(correcto, dict) else getattr(correcto, campo, None)
        if valor_c is None or valor_c == "":
            resultado[campo] = valor_p is None or valor_p == ""
        elif valor_p is None or valor_p == "":
            resultado[campo] = False
        elif _es_numerico(valor_c):
            resultado[campo] = _numeros_iguales(valor_p, valor_c)
        else:
            resultado[campo] = _normalizar(valor_p) == _normalizar(valor_c)
    return resultado


def porcentaje_campos(predicho: Ticket, correcto) -> float:
    aciertos = campos_correctos(predicho, correcto)
    if not aciertos:
        return 0.0
    return 100.0 * sum(aciertos.values()) / len(aciertos)


def medir_tiempo(func, *args, **kwargs):
    inicio = time.perf_counter()
    resultado = func(*args, **kwargs)
    return resultado, time.perf_counter() - inicio


def _nota_a_ticket(nota: VoiceNote) -> Ticket:
    cantidad = None
    if nota.cantidad not in (None, ""):
        try:
            cantidad = float(nota.cantidad)
        except Exception:
            cantidad = None
    return Ticket(
        cliente=nota.cliente,
        producto=nota.producto,
        cantidad=cantidad,
        medida=nota.medida,
        hora_entrega=nota.hora_entrega,
        transcripcion=nota.transcription,
    )


def notas_de_prueba_con_audio() -> list[VoiceNote]:
    notas = load_notes()
    return [nota for nota in notas if nota.audio_path and Path(nota.audio_path).exists()]


def _guardar_metricas(metricas: dict) -> None:
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    with ARCHIVO_METRICAS.open("w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)


def _imprimir_tabla(filas: list[dict]) -> None:
    encabezado = f"{'Modelo':<38} {'WER':<8} {'% Campos correctos':<22} {'Tiempo (segundos)'}"
    print(encabezado)
    print("-" * len(encabezado))
    for fila in filas:
        print(
            f"{fila['modelo']:<38} {fila['wer']:<8} {fila['campos']:<22} {fila['tiempo']}"
        )


def _conclusion(filas: list[dict]) -> str:
    if not filas:
        return (
            "Conclusión: no se ejecutaron modelos. Falta grabar las notas de voz (bloqueo B1). "
            "No hay WER, porcentaje de campos correctos ni tiempos reales que reportar."
        )
    base = filas[0]
    texto = (
        f"Conclusión: el modelo base ({base['modelo']}) obtuvo WER {base['wer']} y "
        f"{base['campos']} de campos correctos en {base['tiempo']} segundos."
    )
    if len(filas) > 1:
        pre = filas[1]
        texto += (
            f" El modelo preentrenado ({pre['modelo']}) obtuvo WER {pre['wer']} y "
            f"{pre['campos']} de campos correctos en {pre['tiempo']} segundos."
        )
    return texto


def comparar_modelos(
    notas: Optional[list[VoiceNote]] = None,
    split: str = "test",
    limite_notas: Optional[int] = None,
) -> dict:
    if notas is None:
        todas = load_notes()
        try:
            _, _, prueba = split_train_val_test(todas)
        except ValueError:
            prueba = list(todas)
    else:
        prueba = list(notas)
    if limite_notas is not None:
        prueba = prueba[:limite_notas]

    prueba = [n for n in prueba if n.audio_path and Path(n.audio_path).exists()]

    if not prueba:
        mensaje = (
            "BLOQUEO B1: no hay notas de prueba con archivo de audio real. "
            "No se pueden medir WER, porcentaje de campos correctos ni tiempos de procesamiento."
        )
        print(mensaje)
        metricas = {
            "b1_pendiente": True,
            "mensaje": mensaje,
            "notas_evaluadas": 0,
            "modelos": {},
        }
        _guardar_metricas(metricas)
        _imprimir_tabla([])
        print(_conclusion([]))
        return metricas

    try:
        from receipt.pipeline import audio_a_ticket, DEFAULT_MODE, MODE_PREENTRENADO
    except ImportError as error:
        mensaje = f"No se puede usar el pipeline de modelo: {error}"
        print(mensaje)
        metricas = {
            "b1_pendiente": False,
            "error": mensaje,
            "notas_evaluadas": len(prueba),
            "modelos": {},
        }
        _guardar_metricas(metricas)
        _imprimir_tabla([])
        print(_conclusion([]))
        return metricas

    filas = []
    for nombre, modo in (
        (MODELO_BASE, MODO_BASE),
        (MODELO_PREENTRENADO, MODO_PREENTRENADO),
    ):
        suma_wer = 0.0
        n_wer = 0
        aciertos = {campo: 0 for campo in TICKET_FIELDS}
        tiempo_total = 0.0
        for nota in prueba:
            def evaluar(m=modo, ruta=nota.audio_path):
                return audio_a_ticket(ruta, m)
            ticket, segundos = medir_tiempo(evaluar)
            tiempo_total += segundos
            if nota.transcription and ticket is not None and ticket.transcripcion:
                suma_wer += wer(nota.transcription, ticket.transcripcion)
                n_wer += 1
            correcto = _nota_a_ticket(nota)
            if ticket is not None:
                for campo, ok in campos_correctos(ticket, correcto).items():
                    if ok:
                        aciertos[campo] += 1
        n = len(prueba)
        total_campos = n * len(TICKET_FIELDS)
        filas.append(
            {
                "modelo": nombre,
                "wer": round(suma_wer / n_wer, 4) if n_wer else None,
                "campos": (
                    f"{100.0 * sum(aciertos.values()) / total_campos:.1f}%"
                    if total_campos
                    else "0.0%"
                ),
                "tiempo": round(tiempo_total, 3),
                "tiempo_promedio_s": round(tiempo_total / n, 4) if n else None,
            }
        )

    _imprimir_tabla(filas)
    print(_conclusion(filas))
    metricas = {
        "b1_pendiente": False,
        "notas_evaluadas": len(prueba),
        "split": split,
        "modelos": filas,
        "conclusion": _conclusion(filas),
    }
    _guardar_metricas(metricas)
    return metricas
