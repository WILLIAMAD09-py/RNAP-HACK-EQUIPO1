# Sesión 2026-11-17: Fase 2, interfaz nueva y bot de Telegram

## Cambios y commits (todos subidos a `main`, salvo lo indicado)

- `36109ed` Modo `solution` híbrido: el LLM (qwen3:4b) da cliente, producto y medida; las reglas dan cantidad y hora. `evaluate` acepta `--whisper`, `--no-vocabulary`, `--threshold` y `--tag`.
- `ca29109` Resultados reales: solución en val y test, y barrido de parámetros en val.
- `4430570` Secciones 4 y 5 del cuaderno, con 2 gráficas en `results/figures/` y 7 errores reales.
- `4055e3a`, `441eb77` y `297cf51` Gradio reemplazado por FastAPI (`app/server.py`) y React + Tailwind + React Bits (`app/web/`), con paleta petróleo y coral, Bootstrap Icons y sin emojis. Contrato en `docs/api-contract.md`.
- `59e5443` Bot de Telegram (@rnyap_bot) y bandeja de la tienda. El token va en `.env`, ignorado por git.
- `cc20249` Panel `/tienda`: notificación con sonido, tarjeta con qué, cuánto y cuándo, audio y transcripción opcionales, alta o rechazo con respuesta predefinida, e inventario en localStorage.
- `e5d9c59`, `d07f5f8` y `d59aafa` Productos fuera de catálogo ("tornillos M4" sale tal cual). Corregida la regresión de "blog de concreto", que salía como cemento.
- `6422cc9` Decisiones del equipo: el cuaderno de Colab ya no se continúa y ya no se exige un commit por integrante.
- `4307ff7` CP3, `d7efe5a` CP4 y tag `v0.2-prototype`, subidos.
- `bb1cb59` D2 y D3 `.docx` actualizados.

## Resultados (test, 5 notas, RTX 5050)

| Modelo | WER | Campos | Tiempo/nota |
|---|---|---|---|
| Base | 18.3 % | 60 % | 4.69 s |
| Preentrenado | 12.7 % | 76 % | 11.66 s |
| Solución (CP3) | 19.8 % | 88 % | 7.61 s |

Las cifras de la solución son del código **anterior** al filtro de fuera de catálogo.

## Decisiones

- La interfaz es React + FastAPI. Gradio se puede recuperar del commit `1836719` si el docente lo exige.
- Fine-tuning: no es obligatorio. La rúbrica acepta "ajuste fino, recuperación o prompts", y usamos prompts y recuperación. Con 16 notas de entrenamiento se sobreajustaría.

## Problemas encontrados

- Ollama corría en CPU (6 a 45 s por nota). Jesús lo actualizó y ahora corre en GPU con `cuda_v13`: unos 3 s de extracción con el modelo cargado. La primera llamada tarda alrededor de 1 min.
- La corrida `offcat` de Jesús tuvo `fallback_notes = 1` porque se lanzaron val y test al mismo tiempo. No es válida; sus archivos `results/solution-offcat_*` siguen sin commit.

## Pendiente

1. **Landing rediseñada** (commit `redesign landing page`): compila, pero nadie la ha visto todavía en el navegador ni en un celular. Revisar cómo se ve y los ajustes que pida Jesús.
2. **Reevaluar en orden** con Ollama en GPU y sin el servidor corriendo: `python -m receipt evaluate --mode solution --split val --tag offcat`, luego lo mismo con `test`. Solo vale con `fallback_notes = 0`. Después actualizar PROGRESS y README con las cifras nuevas.
3. Probar el flujo completo de Telegram a `/tienda` con notas reales.
4. EA de Inglés, Act. 12: solo existe el `.pptx`. Falta el PDF con portada de 250 a 400 palabras, si no se entregó ya.
5. Fase 3: acelerar la extracción (mandar solo productos candidatos al LLM), el mapa de cross-attention de Whisper, `README.md` con cinco secciones y enlace, ensayo con notas nuevas con ruido, presentación y release `v1.0`.
6. Generar un token nuevo del bot en @BotFather con `/revoke`, porque el actual se pegó en el chat.

## Siguiente paso

Que Jesús revise la landing en http://127.0.0.1:8000. Después, reevaluar `offcat` con Ollama en GPU.
