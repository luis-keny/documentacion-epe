# Documentación transversal

Esta carpeta conserva el contexto compartido del producto: procesos, modelo objetivo y evidencia. Este README es el mapa para personas y agentes; no hace falta leerlo para solicitudes ajenas a estos temas. La documentación de implementación vive en los índices de [epe-web](../epe-web/docs/README.md) y [epe-backend](../epe-backend/docs/README.md). Las reglas editoriales están en [AGENTS.md](AGENTS.md).

## Fuentes de verdad

| Tema | Fuente canónica | Alcance |
|---|---|---|
| Negocio/prototipo | [Procesos](business/processes.md) y [flujo visual](business/flows/overview.html) | Útil para reglas, términos y recorridos compartidos; el prototipo es antecedente, no implementación vigente. |
| Estado general | [Estado del proyecto](estado-del-proyecto.md) | Resumen coordinado; el detalle por vista permanece en frontend. |
| Estado de integración | [Registro frontend](../epe-web/docs/integration-status.md) | Estado por vista y evidencia reciente. |
| Contrato generado | [Fuente SQL y proceso](../epe-web/docs/api/README.md) y OpenAPI generado | Contrato consumido; su copia runtime vive en backend. |
| Esquema implementado | Entidades y migraciones del [backend](../epe-backend/src/database/) | Estructura programada; no acredita el estado de una base desplegada. |
| Modelo objetivo | [Entrada al modelo](target-model/README.md) | Útil al revisar tablas y relaciones propuestas; está separado del esquema implementado. |
| Históricos | [Historial](history/README.md) | Útil para rastrear evidencia y decisiones fechadas; no describe el estado vigente. |

`docs/prototipo/` no está presente en este checkout. Se conservan intactas sus referencias existentes; no se reconstruye ni se mueve el material inicial. Los agentes pueden usar este mapa cuando una solicitud afecte estas fuentes; no es lectura obligatoria para tareas ajenas a ellas.

## Rutas de consulta

| Si necesitas… | Consulta… |
|---|---|
| Entender actores, términos o el recorrido general | [business/processes.md](business/processes.md); contrasta acciones concretas con los manuales de `epe-web` y el estado de integración. |
| Revisar el modelo propuesto | [target-model/README.md](target-model/README.md), que conduce al diccionario, relaciones, SQL y límites frente al backend. |
| Ver el estado de una vista | [integration-status.md](../epe-web/docs/integration-status.md). |
| Investigar una decisión o evidencia pasada | [history/README.md](history/README.md); no usar sus conclusiones como estado actual. |
| Cambiar contrato API o persistencia | [contrato frontend](../epe-web/docs/api/README.md), OpenAPI generado y entidades/migraciones backend. |
| Cambiar diagramas de proceso | [fuentes Archify](business/flows/candidate.archify.md) y archivos `*.workflow.json` de esa carpeta. |
