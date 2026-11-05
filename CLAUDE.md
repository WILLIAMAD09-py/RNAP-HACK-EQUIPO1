@AGENTS.md

# Claude Code

`AGENTS.md`, importado arriba, contiene los entregables, las reglas y el flujo. Aquí solo va lo específico de Claude Code. No dupliques contenido de ese archivo.

## Modelos por rol

| Rol | Modelo | Cómo se selecciona |
|---|---|---|
| Orquestador | Claude Opus 5.5 | Sesión principal: `claude --model opus` o `/model opus` |
| Instalador | Claude Haiku 5.5 | Agent tool con `model: "haiku"` |
| Programador | Claude Sonnet 5.5 | Agent tool con `model: "sonnet"` |

## Instrucciones para el orquestador

- Si la sesión principal no corre en Opus, avísale al usuario antes de empezar.
- Pasa siempre `model` de forma explícita al lanzar un agente. El parámetro por llamada tiene prioridad sobre la configuración del agente.
- Usa la plantilla de prompt de la sección 6 de `AGENTS.md` para cada agente.
- Lanza en un mismo mensaje los agentes que sean independientes.
- Para seguir con un worker que ya tiene contexto, envíale un mensaje en vez de lanzar uno nuevo.
- Revisa el diff y corre la verificación tú mismo antes de hacer commit.

## Commits

Sigue la sección 7 de `AGENTS.md`. Los commits de checkpoint (`CP1` a `CP4`) los hace una persona, y su mensaje es solo la clave, sin trailers de coautoría.

## Límite de mensajes por sesión

Lleva la cuenta de los mensajes del usuario en la conversación. Al llegar a 20:

1. Genera `docs/sesiones/YYYY-MM-DD-<tema>.md` con lo que se hizo en la sesión: cambios y commits, decisiones, problemas, lo que quedó pendiente y el siguiente paso.
2. Haz commit de ese archivo.
3. Dile al usuario que ya llegó a 20 mensajes y que inicie una conversación nueva para ahorrar tokens, indicando la ruta del archivo.

Al iniciar una sesión, lee el archivo más reciente de `docs/sesiones/` para retomar el trabajo.
