# Antigravity (Gemini)

Antigravity carga `AGENTS.md` junto con este archivo: ahí están los entregables, las reglas y el flujo. Aquí solo va lo específico de Gemini. No copies ni importes `AGENTS.md`, porque las reglas se suman y el contenido se duplicaría.

## Modelos por rol

| Rol | Modelo | Cómo se selecciona |
|---|---|---|
| Orquestador | Gemini 4 Argon | `agy --model gemini-4-argon-high` |
| Instalador | Gemini 3.8 Flash | Worker con `--model gemini-3.8-flash-medium` |
| Programador | Gemini 3.8 Flash | Worker con `--model gemini-3.8-flash-high` |

Confirma los IDs disponibles con `agy models`.

## Instrucciones para el orquestador

- Si la sesión principal no corre en Argon, avísale al usuario antes de empezar.
- Un subagente sin modelo definido **hereda Argon**, y aquí los workers deben correr en Flash.
- Lanza cada worker desde la terminal para fijar su modelo:

```bash
agy --model gemini-3.8-flash-high --mode accept-edits -p "<prompt de la plantilla>"
```

- Usa la plantilla de prompt de la sección 6 de `AGENTS.md` para cada worker.
- El modo no interactivo solo se ha probado con una respuesta de texto. En el primer uso, confirma que el worker puede editar archivos y ejecutar comandos.
- Revisa el diff y corre la verificación tú mismo antes de hacer commit.

## Commits

Sigue la sección 7 de `AGENTS.md`. Los commits de checkpoint (`CP1` a `CP4`) los hace una persona, y su mensaje es solo la clave.
