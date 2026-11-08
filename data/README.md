# Datos

- `catalog.csv`: catálogo de 42 productos inventado por el equipo.
- `notes.csv`: respuestas correctas de cada nota de voz. Sí va al repo.
- `audio/`: notas de voz grabadas por el equipo. **No va al repo**, se comparte por enlace.

**Enlace al audio:** _pendiente_

Todas las notas son grabadas por el equipo y sus pedidos son actuados, no de clientes reales.

## Cómo grabar las notas de voz

Meta: **10 notas por persona, 40 en total**. El mínimo del brief son 30.

Cada nota es un pedido de **un solo producto** y debe decir los cinco datos:

> "Hola, soy Carlos Treviño, me mandas cincuenta metros de cable del doce para las tres de la tarde, por favor."

1. Elige un producto de `catalog.csv` y dilo como lo diría un cliente, usando sus sinónimos: "cable del doce", "tubo de media", "bulto de cemento".
2. Inventa el nombre del cliente, la cantidad y la hora.
3. Graba en WhatsApp o en la grabadora del celular. Sirve cualquier formato.
4. Nombra el archivo con tu nombre y número: `jesus_01.ogg`, `jack_02.m4a`.

### Reparte tus 10 notas así

| Ruido | Notas | Dónde |
|---|---|---|
| `silencio` | 3 | Lugar callado |
| `moderado` | 4 | Salón con gente hablando |
| `fuerte` | 3 | Pasillo, música o ventilador cerca |

Combina también la velocidad: 3 `lenta`, 4 `normal` y 3 `rapida`.

Varía el orden de los datos y la forma de hablar. No leas la misma frase. El juez grabará en el salón con ruido, así que las notas con ruido son las más valiosas.

## Cómo llenar `notes.csv`

Una fila por nota. Escríbela **antes** de correr el modelo, con lo que realmente se dijo.

| Columna | Qué poner | Ejemplo |
|---|---|---|
| `note_id` | Nombre del archivo sin extensión | `jesus_01` |
| `audio_file` | Nombre del archivo | `jesus_01.ogg` |
| `speaker` | Quién habla | `jesus` |
| `noise` | `silencio`, `moderado` o `fuerte` | `moderado` |
| `speed` | `lenta`, `normal` o `rapida` | `normal` |
| `transcript` | Texto exacto de lo dicho, sin corregirlo | `hola soy carlos treviño...` |
| `cliente` | Nombre del cliente | `Carlos Treviño` |
| `producto_id` | `id` en `catalog.csv` | `CAB-003` |
| `cantidad` | Solo el número | `50` |
| `medida` | Columna `medida` de `catalog.csv` | `calibre 12` |
| `hora_entrega` | Formato de 24 horas | `15:00` |

Si un dato no se dijo, deja esa columna vacía. Si un texto lleva coma, ponlo entre comillas dobles.

## Cómo se armó el `notes.csv` actual

- 30 audios grabados por el equipo: jack 01-08, jesus 01-07, william 01-08, carlos 01-07.
- `jack_05`, `william_04` y `carlos_03` son copias idénticas de `jack_04`, `william_01` y `carlos_02`. Se dejaron fuera para que una misma nota no quede en train y en prueba a la vez, así que hay **27 notas**. Faltan 3 notas nuevas para llegar al mínimo de 30.
- `transcript` es un **borrador** hecho con `openai/whisper-large-v3`, un modelo que no se evalúa, con unas pocas correcciones de ortografía. Falta que el equipo lo revise escuchando cada audio.
- Si la nota pide varios productos, el ticket correcto es el **primer producto mencionado**, con su cantidad.
- `cliente` va sin título: "el ingeniero Carlos Ruiz" se anota como `Carlos Ruiz` y "el maestro Beto" como `Beto`.
- `noise` y `speed` son estimaciones automáticas: el ruido sale del nivel de fondo del audio y la velocidad de las palabras por segundo. Falta que el equipo las confirme.
