# RNAP Hack 2026 — Equipo 1: plan de trabajo para agentes

Fuente única de verdad del proyecto. La leen OpenCode y Antigravity de forma nativa, y Claude Code mediante `CLAUDE.md`. Todo cambio de entregables, flujo o reglas se hace **aquí**. `CLAUDE.md` y `GEMINI.md` solo guardan lo específico de cada herramienta.

**Forma de trabajo: aplicación en Python normal.** Primero el flujo completo por línea de comandos en `receipt/`, y después la interfaz en `app/`, que solo llama a `receipt.pipeline`. No se desarrolla en cuadernos.

## 1. Producto

**Receipt** es nuestro producto para el **Reto 3: From Voice Note to Order.** El cliente es **Ferretería Los Nogales** (empresa ficticia), que entrega en obras del área de Monterrey. Sus clientes piden por notas de voz de WhatsApp, el personal las captura a mano y se equivoca en cantidades y medidas: una vez pidieron cable del 12 y mandaron 50 metros del 10.

**Reto:** convertir una nota de voz en español en un ticket de pedido.

**Campos del ticket:** nombre del cliente, producto, cantidad, medida y hora de entrega.

**Qué se construye:** una interfaz en **Gradio** donde el usuario graba con el micrófono o sube un audio. Muestra la transcripción y un **ticket editable**, y un botón de confirmar agrega el pedido a la lista del día.

**Prueba del juez:** graba una nota de voz nueva en vivo, en el salón y con ruido de fondo.

**Criterios del juez:**

- Resultados: campos correctos en sus notas de voz.
- Robustez: ruido, habla rápida y voces distintas.
- Velocidad: segundos desde que termina el audio hasta que aparece el ticket.
- Claridad: el usuario puede corregir un campo antes de confirmar.

**Métricas:** WER (`jiwer` o `evaluate`) y % de campos correctos, más el tiempo de cada modelo.

**Integrantes:** William, Jack, Carlos y Jesús.

Fuentes del curso, en la raíz del repo: `RNAP_Hack_2026_Challenge_Tracks.docx`, `RNAP_Hack_2026_Instrucciones_Redes_Neuronales.docx`, `RNAP_Hack_2026_Guia_GitHub.docx` y `RNAP_Hack_2026_English_Instructions.docx`. Si este archivo y un `.docx` se contradicen, manda el `.docx`.

### Bloqueos abiertos

| # | Bloqueo | Qué detiene |
|---|---|---|
| B1 | **No hay audio.** El brief exige que el equipo grabe 30+ notas de voz con voces, velocidades y ruido distintos, cada una con su ticket correcto | WER, Whisper y toda evaluación real |
| B2 | `notebooks/entrenamiento.ipynb` es JSON inválido y no abre. Se reemplaza por el reporte de la sección 3.1 | Secciones 1 a 3 del reporte |

El catálogo `data/catalog.csv` ya cumple: 42 productos, dentro del rango de 30 a 50.

## 2. Reglas del curso que ningún agente puede romper

1. **Solo cuenta lo que se sube en horario de clase.** El docente revisa la hora de cada push en Activity.
2. **Cada integrante hace al menos un commit propio en cada fase.** Un agente nunca falsifica autoría (`--author`, cambiar `user.name`).
3. **Commit de checkpoint:** su mensaje es solo la clave (`CP1`, `CP2`, `CP3`, `CP4`), sin cuerpo y sin trailers. Lo hace una persona.
4. **Cientos de líneas entre checkpoints sin avance visible en clase se revisan con el equipo.** Preferir commits pequeños.
5. **Lo subido después de un checkpoint queda fuera de esa fase.** Lo subido después de `v1.0` queda fuera de la Fase 3.
6. **Las claves de API nunca van al repo.** Se guardan en Secretos de Colab y en los secretos del servicio de publicación.
7. **Los datos pesados no van al repo.** En `data/` va una muestra pequeña o el enlace a la fuente.
8. **Todo el código vive en `receipt/` y `app/`.** Cada integrante trabaja en su parte y sube cambios pequeños. El cuaderno `notebooks/entrenamiento.ipynb` es solo el reporte.
9. **`README.md` y `PROGRESS.md` van en inglés.** El cuaderno va en español.
10. **No inventar resultados.** Toda cifra en cuaderno, README, reportes o presentación sale de una ejecución real y debe coincidir con el repo.
11. **Cualquier integrante debe poder explicar el modelo, el código y la atención.** El juez elige a quién preguntar, así que todo lo que hace un agente se le explica al equipo.
12. **División limpia:** train, validación y prueba se separan antes de entrenar. El conjunto de prueba se usa solo para las métricas finales.
13. **Datos públicos y gratuitos o creados por el equipo.** Los datos sintéticos se etiquetan como sintéticos.
14. **Mantenerlo pequeño.** Un flujo que funciona de principio a fin vale más que varias funciones a medias.

## 3. Entregables

Se dividen por materia, luego por fase, y cada fase en paquetes de trabajo. `Pts` es el valor en el instrumento de evaluación. Responsable: **Agente**, **Persona** o **Ambos**.

### 3.1 Redes Neuronales: reporte `notebooks/entrenamiento.ipynb`

El curso exige este archivo y vale 25 puntos en el PIA, así que **no se borra**. Ya no es donde se programa: lleva el texto de las secciones y muestra resultados leídos de `results/`, llamando al código de `receipt/`.

| Sección | Contenido | Fase |
|---|---|---|
| 1. Problema y datos | Reto, fuente, tamaño, división train/val/test | 1 |
| 2. Representación del texto | Tokenización y representación usadas, y por qué | 1 |
| 3. Modelo base y preentrenado sin ajuste | Configuración, resultados y tabla con métrica y tiempo | 1 |
| 4. Solución con Transformer | Modelo y justificación, configuración, parámetros clave y su efecto | 2 |
| 5. Evaluación y errores | 2+ métricas en prueba con tablas y gráficas, 5+ errores con causa | 2 |
| 6. Comparación final y límites | Tabla final base vs. Transformer, elemento de atención, límites | 3 |

### 3.2 Fase 1: Línea base (2.5 %, se revisa CP2, lista de cotejo)

| ID | Paquete | Pts | Responsable |
|---|---|---|---|
| F1.0 | Paquete `receipt/`, pruebas y `requirements.txt` | — | Agente |
| F1.1 | `PROGRESS.md` describe el problema y la métrica principal | 10 | Ambos |
| F1.2 | Justificar la representación del modelo base (reglas con expresiones regulares) | 10 | Ambos |
| F1.3a | Grabar las notas de voz y escribir su ticket correcto | — | Persona |
| F1.3b | Cargar los datos y dividir en train/val/test **antes** de evaluar | 10 | Agente |
| F1.4 | Modelo base de principio a fin: Whisper pequeño + reglas con regex | 10 | Agente |
| F1.5 | Whisper de mayor tamaño + extracción con modelo de lenguaje, sin ajuste, sobre las **mismas** notas de prueba | 10 | Agente |
| F1.6 | WER y % de campos correctos por modelo, en prueba | 10 | Agente |
| F1.7 | Tiempo de procesamiento de cada modelo | 10 | Agente |
| F1.8 | Tabla comparativa y conclusión breve, secciones 1 a 3 | 10 | Ambos |
| F1.9 | CP1 y CP2 en horario, con `PROGRESS.md` al día | 10 | Persona |
| F1.10 | Un commit propio de cada integrante | 10 | Persona |
| F1.11 | Cada integrante sube a NEXUS el ZIP del commit CP2 con comprobante | — | Persona |

### 3.3 Fase 2: Prototipo (5 %, se revisa CP4, rúbrica)

| ID | Paquete | Pts | Responsable |
|---|---|---|---|
| F2.1 | Solución con Transformer que corre completa y con elección justificada | 20 | Agente |
| F2.2 | Evaluación en prueba: mismas métricas, tabla, gráfica y comparación con la base | 20 | Agente |
| F2.3 | Configuración documentada con el **efecto observado** de cada parámetro | 15 | Ambos |
| F2.4 | 5+ casos de error con causa propuesta, secciones 4 y 5 | 10 | Ambos |
| — | **Subir CP3** al terminar lo anterior | — | Persona |
| F2.5 | Interfaz v1 en Gradio conectada al modelo: audio, transcripción y ticket | 20 | Agente |
| F2.6 | CP3 y CP4 en horario, `PROGRESS.md` al día, commits de cada integrante | 15 | Persona |
| F2.7 | Cada integrante sube a NEXUS el ZIP del commit CP4 con comprobante | — | Persona |

### 3.4 Fase 3: PIA Producto (10 %, se revisa `v1.0`, rúbrica)

| ID | Paquete | Pts | Responsable |
|---|---|---|---|
| F3.1 | Prueba del juez: campos correctos en notas nuevas y respuesta en pocos segundos | 30 | Agente |
| F3.2 | Cuaderno completo: sección 6 y secciones 1 a 5 al día | 25 | Ambos |
| F3.3 | Interfaz publicada o en laptop, estable, usable sin ayuda, con respaldo probado | 20 | Agente |
| F3.4 | Enlace de la interfaz en `README.md` | — | Agente |
| F3.5 | Todos responden preguntas sorpresa y explican la atención | 15 | Persona |
| F3.6 | Cuatro checkpoints, `v1.0` a tiempo, commits de cada integrante por fase | 10 | Persona |
| F3.7 | Marcar `v1.0` como Release antes de presentar | — | Persona |
| F3.8 | Cada integrante sube a NEXUS el ZIP de `v1.0` con comprobante | — | Persona |

Formato de la demo: dentro de los 20 minutos del equipo, el juez usa la interfaz 5 minutos con entradas ocultas y luego hace preguntas sorpresa.

### 3.5 Inglés

Todo lo escrito se entrega en PDF con portada en NEXUS, y la redacción ocurre en la clase de Inglés. El equipo decidió usar IA, aunque el brief solo la menciona para escribir código. Los agentes pueden proponer borradores y revisar con datos reales, pero cada persona debe entender lo que entrega y poder decirlo sin leer.

| ID | Entregable | Valor | Modo | Contenido |
|---|---|---|---|---|
| I1 | D2 · Act. 10 Grammar in Your Brief | 2.5 % | Equipo | Tabla con una oración del brief por estructura y qué expresa. Se intercambia con otro equipo |
| I2 | D3 · Act. 11 Developer Reflection | 2.5 % | **Individual** | 100 a 150 palabras en tres párrafos: experiencias reales, presente ideal, reflexión pasada sobre una decisión de la Fase 1 |
| I3 | EA · Act. 12 Troubleshooting Report | 5 % | Equipo | 250 a 400 palabras con datos reales, más Audit Status oral de 2 minutos |
| I4 | PIA · Act. 13 Product Presentation | PIA | Equipo | 10 min de presentación, 5 de demo, 5 de preguntas. Todos hablan, 4+ estructuras gramaticales |
| I5 | PIA · `README.md` | 15 pts de I4 | Equipo | Cinco secciones. También cumple el enlace de F3.4 |

**I1, oraciones del brief del Reto 3:**

| Estructura | Oración | Qué expresa |
|---|---|---|
| Present Perfect | For years, clients have sent their orders as WhatsApp voice notes. | Real experience |
| Second Conditional | If the store read its voice notes automatically, the staff would prepare the order while the client is still on the way. | Present imagination |
| Perfect Conditional | If someone had confirmed the size, the store wouldn't have lost that sale. | Past hypothesis |

**I3, secciones y rúbrica:**

| Sección | Requisito | Pts |
|---|---|---|
| 1. Audit Status | 4+ oraciones en Present Perfect, con tabla o gráfica de métricas | 20 |
| 2. Immediate Solutions | 2+ mejoras con efecto esperado, en Second Conditional | 20 |
| 3. Root Cause Analysis | 2+ decisiones pasadas y qué habría pasado, en Perfect Conditional | 20 |
| Contenido técnico | Datos reales que coinciden con el repo, con tabla o gráfica | 15 |
| Gramática y vocabulario | dataset, baseline, accuracy, fine-tuning bien usados | 15 |
| Entrega y exposición | PDF con portada, 250 a 400 palabras, 2 min con fluidez | 10 |

**I4, diapositivas:** título · cliente y problema · producto · cómo funciona · demo en vivo · resultados · qué aprendimos y qué sigue.

**I4, rúbrica:** contexto 15 · estructuras 20 · solución y demo 20 · fluidez 20 · README 15 · colaboración e innovación 10.

**I5, secciones:** nombre y descripción de una línea · problema y a quién afecta · cómo funciona · resultados con métricas · qué aprendimos y qué haríamos con más tiempo.

### 3.6 Dependencias entre entregables

```text
F1.3a notas de voz ──> F1.3b ──> F1.4 + F1.5 ──> F1.6-F1.8 ──> CP2
                                                    │
                                                    ├──> I2 (decisión de la Fase 1)
                                                    v
                  F2.1 ──> F2.2 ──> F2.4 ──> CP3 ──> F2.5 ──> CP4
                                     │
                                     └──> I3 (métricas y errores reales)
                                                       v
                  F3.1 + F3.2 + F3.3 ──> I5 ──> v1.0 ──> I4

I1 no depende de nada: ya se puede entregar.
```

## 4. Plan técnico

Hipótesis de trabajo. Toda elección de modelo se decide midiendo, no por suposición.

**Datos.** Grabar al menos 40 notas, 10 por integrante, para que el conjunto de prueba no quede demasiado chico con el mínimo de 30.

- Cada nota lleva su audio, transcripción correcta y ticket correcto, escritos **antes** de ver la salida del modelo.
- Variar voz, velocidad y ruido, e incluir formas reales de hablar: "cable del doce", "cincuenta metros", "para las tres".
- División sugerida 60/20/20, equilibrada por persona y por nivel de ruido.
- El audio se guarda fuera del repo. En `data/` va el enlace, una muestra pequeña y el archivo de respuestas.
- El texto sintético de Jack sirve para desarrollar reglas, etiquetado como sintético, pero **no sustituye** al audio ni permite medir WER.

**Fase 1.**

- Base: `openai/whisper-small` o `whisper-base` + regex para números, unidades y productos.
- Preentrenado: un Whisper más grande + modelo de lenguaje con prompt que devuelve el ticket en JSON.
- Forzar idioma español. Normalizar igual ambos textos antes de calcular WER: minúsculas, sin puntuación y números en un solo formato.
- Definir por escrito qué cuenta como campo correcto. Por ejemplo, `50` y `cincuenta` valen lo mismo.
- Medir el tiempo de transcripción y de extracción por nota.

**Fase 2.** La solución encadena tres pasos:

1. **Transcripción** con el tamaño de Whisper que mejor equilibre WER y velocidad, probando dar el vocabulario del catálogo como prompt inicial.
2. **Extracción** con un modelo de lenguaje que devuelve JSON con los cinco campos.
3. **Emparejamiento con el catálogo** usando sentence embeddings (por ejemplo `paraphrase-multilingual-MiniLM-L12-v2`), para convertir "cable del doce" en `CAB-003`.

Los parámetros que se documentan con su efecto son tamaño de Whisper, prompt inicial, prompt de extracción y umbral de similitud. Si el modelo de lenguaje falla o no hay red, se usa el regex como respaldo para que la demo nunca se caiga.

**Fase 3.** La atención se explica con Whisper, un Transformer encoder-decoder: un mapa de cross-attention que muestra a qué parte del audio atiende el decoder al escribir una palabra como "doce", en un acierto y en un error. Antes de la demo se ensaya con notas nuevas, con ruido y grabadas por alguien de fuera del equipo.

**Lo que lo hace distinto:** ataca el error real de la ferretería. El ticket **marca en amarillo los campos dudosos**, sobre todo medida y cantidad, y pide confirmarlos antes de agregar el pedido. Si el producto existe en varias medidas y no se entendió cuál, muestra las opciones del catálogo. Eso cumple el criterio de claridad y da la "idea propia del equipo" que pide I4.

**Interfaz y publicación:**

- Gradio con micrófono y carga de audio, transcripción, ticket editable, botón de confirmar y lista del día.
- Durante clase se puede compartir con `share=True` de Gradio.
- Versión final en Hugging Face Spaces (CPU gratuita) o en la laptop del equipo. Se elige midiendo la velocidad, y el otro queda de respaldo.
- El micrófono del navegador exige HTTPS o `localhost`, así que se prueba en el mismo modo en que se va a presentar.
- Los modelos se cargan una sola vez al iniciar, nunca en cada petición.

**Entorno:** Python 3.11 en `.venv/`. El código funciona en CPU, usa GPU si existe, fija semillas y no usa rutas absolutas. El audio se decodifica con PyAV, sin depender de `ffmpeg`.

**GPU:** todo entrenamiento, ajuste fino o evaluación pesada corre en la **RTX 5050 Laptop (8 GB)** de Jesús. Antes de empezar, confirmar que `torch.cuda.is_available()` es `True` y que el dispositivo es esa GPU. Si no lo es, detenerse y avisar: nunca entrenar en CPU sin decirlo. Esta GPU necesita PyTorch con CUDA 12.8 (`cu128`). Si la memoria no alcanza, bajar el tamaño de lote antes de cambiar de modelo.

**Estructura:**

```text
receipt/           lógica de la aplicación, sin interfaz
  config.py        rutas, modos y modelos
  ticket.py        ticket y sus campos
  audio.py         carga de audio
  numbers.py       números en español
  catalog.py       catálogo y emparejamiento
  transcription.py Whisper
  extraction/      rules.py (base) y llm.py (Transformer)
  pipeline.py      audio a ticket
  dataset.py       notas de voz y división
  evaluation.py    WER, campos y tiempos
  orders.py        lista de pedidos confirmados
app/               interfaz Gradio
tests/             pruebas sin modelos ni red
results/           métricas de cada corrida
```

**Comandos:**

```bash
python -m receipt process <audio> --mode baseline
python -m receipt split
python -m receipt evaluate --mode baseline --split val
python -m receipt compare
```

## 5. Flujo por paquete de trabajo

1. **Sincronizar:** `git pull --rebase`. Los compañeros también suben desde el navegador.
2. **Elegir** el siguiente paquete desbloqueado de la sección 3 y leer su criterio en el `.docx`.
3. **Planear:** el orquestador define archivos, criterio de terminado y modelo.
4. **Delegar** con la plantilla de la sección 6. Instalación al instalador, código al programador.
5. **Resultados primero:** el worker reporta cifras de una corrida rápida con pocas notas antes de la evaluación completa.
6. **Revisar:** el orquestador compara el diff contra la rúbrica y corre la verificación. Si falla, regresa observaciones concretas al worker.
7. **Commit** del cambio significativo (sección 7).
8. **Bitácora:** actualizar la entrada del checkpoint en `PROGRESS.md`.
9. **Explicar:** dejar en el reporte, en lenguaje simple, qué se hizo y por qué, para que el equipo pueda defenderlo.

Verificación mínima antes de dar algo por terminado:

- `python -m pytest -q` pasa completo.
- El flujo corre de principio a fin con un audio real.
- Las cifras del reporte coinciden con `results/`.
- No hay secretos ni datos pesados en el diff.

Cambios mínimos sobre lo que ya funciona. No reescribir. Se evalúa en validación mientras se desarrolla, y el conjunto de prueba se usa solo para las métricas finales.

**Comentarios:** no escribir comentarios ni docstrings en el código, salvo que algo no se entienda sin ellos. Usar nombres descriptivos.

## 6. Orquestación de agentes

| Rol | Hace | No hace |
|---|---|---|
| **Orquestador** | Planea, divide, delega, revisa, integra y hace commits | Escribir el código directamente |
| **Instalador** | Entorno, dependencias, descargas, verificación de imports | Cambiar código del proyecto |
| **Programador** | Código, interfaz, corridas y métricas | Commits, push, cambiar el alcance |

**Modelos por herramienta:**

- **Claude Code:** ver `CLAUDE.md`.
- **Antigravity:** ver `GEMINI.md`.
- **OpenCode:** los agentes corren en el modelo que el usuario tenga seleccionado. No fijar `model` por agente ni crear configuración por rol. El orquestador lanza los subagentes con la herramienta Task y estos heredan su modelo.

**Reglas de delegación:**

- Los subagentes no ven la conversación: cada prompt debe valerse por sí mismo.
- Una tarea por agente, con archivos explícitos. Dos agentes nunca editan el mismo archivo.
- Paralelizar solo lo independiente.
- El orquestador verifica por sí mismo: el reporte de un worker no es prueba.
- Tras dos intentos fallidos sobre lo mismo, el orquestador cambia de enfoque o pregunta al equipo.

**Plantilla de prompt (usar completa):**

```text
<rol>Quién eres y tu única responsabilidad.</rol>
<contexto>
Proyecto en una línea, paquete de trabajo (ID), qué existe y por qué importa.
Lee AGENTS.md secciones 2 y 4 antes de empezar.
</contexto>
<tarea>Un solo resultado, en una o dos oraciones.</tarea>
<archivos>
Puedes editar: rutas exactas.
Solo lectura: rutas exactas.
No toques nada más.
</archivos>
<restricciones>
Reglas aplicables. Sin claves en código. Sin commits ni push.
No inventes cifras: si algo no corre, repórtalo.
Si falta información, detente y pregunta; no supongas.
</restricciones>
<terminado>
Criterios verificables, con el comando que los comprueba.
Ejemplo: `python -m receipt compare` imprime WER y % de campos para ambos modelos.
</terminado>
<reporte>
Devuelve: archivos cambiados, comandos ejecutados con su resultado real,
cifras obtenidas, lo que quedó sin hacer y dudas. Máximo 200 palabras.
</reporte>
```

**Instalador, además:** usar entorno virtual `.venv/`, fijar versiones que funcionaron en `requirements.txt`, comprobar cada import y reportar la versión de cada paquete. No instalar nada global.

**Programador, además:** reutilizar el código existente, fijar semillas, sin comentarios innecesarios, hacer primero una corrida rápida con una muestra y reportar las cifras antes de la ejecución completa.

## 7. Control de versiones

**Cambio significativo = commit inmediato.** Es significativo cualquier unidad terminada y verificada: un paso nuevo del pipeline, un cambio en la división de datos, una métrica o resultado nuevo, una sección del cuaderno, una función de la interfaz, una dependencia nueva o una decisión de diseño. No lo es un experimento a medias, un cambio de formato ni código que no corre.

**Cómo hacer commit:**

- Mensaje corto en inglés que describe el cambio, como pide la guía: `add regex baseline`, `fix data split`.
- Debajo del título va un cuerpo que le cuente al equipo **qué se hizo**: qué cambió, cómo usarlo y si alguien debe hacer algo después. Así todos pueden seguir el avance en GitHub sin preguntar.
- Antes de hacer push, revisar que cada commit que se va a subir lleve ese mensaje. La única excepción son los commits de checkpoint, que llevan solo su clave.
- Agregar archivos por nombre. Nunca `git add -A` ni `git add .`.
- Un cambio lógico por commit. Si el diff pasa de unas 150 líneas de código, dividirlo.
- Prohibido `--force`, reescribir historia ya subida y `--no-verify`.

**Commit y push son cosas distintas:**

- **Commit:** automático tras cada cambio significativo.
- **Push:** solo cuando una persona confirme que están en horario de clase. Fuera de clase, los commits se quedan locales y se suben en la siguiente clase.

**Ramas:** `main` es la rama integrada y la que evalúa el docente. Lo riesgoso va en `exp/<tema>` y se integra antes del checkpoint.

**Versiones:**

| Marca | Cuándo | Qué representa |
|---|---|---|
| Commit `CP1` | Fase 1 | Repositorio creado |
| Commit `CP2` + tag `v0.1-baseline` | Fase 1 | Línea base completa |
| Commit `CP3` | Fase 2 | Solución Transformer evaluada |
| Commit `CP4` + tag `v0.2-prototype` | Fase 2 | Interfaz v1 conectada |
| Release `v1.0` | Fase 3 | Producto final. Nada se sube después |

**Procedimiento de checkpoint**, entre 10 y 15 minutos antes de terminar la clase:

1. Cada integrante guarda su trabajo en GitHub.
2. El responsable actualiza el reporte y sube la interfaz si cambió.
3. Se agrega la entrada al **inicio** de `PROGRESS.md`, en inglés:

```markdown
## CP2 - YYYY-MM-DD
- What we have done:
- What we haven't done yet:
- Next step:
- Who did what:
```

4. Una persona hace el commit final con mensaje exacto `CP2`, sin nada más.
5. Se confirma en la página del repo que aparece con la hora correcta.

## 8. Research

**Estado: no hay research previo.** No se encontró nada en el repo, en sesiones anteriores de los agentes ni en otras carpetas. Lo único disponible son las "Possible approaches" del brief.

Todo hallazgo se guarda en `docs/research/<tema>.md` con fuente y fecha de consulta, y se revisa aquí antes de investigar de nuevo.

Pendiente:

1. Latencia y WER de cada tamaño de Whisper en español, en CPU y en GPU.
2. Qué modelo de lenguaje usar para extraer JSON: API gratuita o local con Ollama, comparando costo, velocidad y disponibilidad en la demo.
3. Cómo extraer los mapas de cross-attention de Whisper.
4. Cómo mejorar la robustez ante ruido sin reentrenar.
5. Límites actuales de Hugging Face Spaces para audio y modelos de este tamaño.

## 9. Decisiones pendientes del equipo

- [ ] Definir responsable del repositorio y responsable del cuaderno.
- [ ] Repartir la grabación de las notas de voz.
- [ ] Elegir el modelo de lenguaje para la extracción. Por ahora, `qwen3:4b` local con Ollama.
