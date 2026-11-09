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

Los adjuntos de campaña y otros formularios verifican metadatos y objeto real en S3 antes de mostrarse verdes; faltantes/inconsistencias se muestran en rojo. El [flujo backend](../epe-backend/docs/backend-flow.md#41-servicio-general-de-documentos-y-vínculos-en-s3-apidocumentos) y el [contrato de disponibilidad](../epe-web/docs/api/business-rules.md#disponibilidad-de-adjuntos) describen la comprobación puntual y los errores de verificación. La implementación local no acredita el estado de un despliegue productivo.

| Si necesitas… | Consulta… |
|---|---|
| Entender actores, términos o el recorrido general | [business/processes.md](business/processes.md); contrasta acciones concretas con los manuales de `epe-web` y el estado de integración. |
| Revisar el modelo propuesto | [target-model/README.md](target-model/README.md), que conduce al diccionario, relaciones, SQL y límites frente al backend. |
| Ver el estado de una vista | [integration-status.md](../epe-web/docs/integration-status.md). |
| Modificar vistas, reglas de negocio y simulación de manera coordinada | [Flujo de cambios y comunicación al desarrollador](../epe-web/docs/development.md#cambios-de-vistas-reglas-de-negocio-y-mock). |
| Revisar qué datos necesita cada vista y qué actualiza cada escritura | [Optimización implementada](../epe-web/docs/integration-status.md#optimización-de-peticiones-por-vista--2026-11-05--implementada-en-desarrollo-y-revisada) y [diseño de referencia](../epe-web/docs/integration-status.md#plan-de-consumo-api-por-vista--2026-11-05--referencia-de-diseño). |
| Investigar una decisión o evidencia pasada | [history/README.md](history/README.md); no usar sus conclusiones como estado actual. |
| Entender cómo arranca y responde el backend, o el flujo de documentos en S3 | [flujo del backend](../epe-backend/docs/backend-flow.md). |
| Revisar variables S3, imágenes y Compose de backend/web | [diagnóstico de despliegue](../epe-backend/docs/diagnostico-s3-despliegue.md). |
| Cambiar contrato API o persistencia | [contrato frontend](../epe-web/docs/api/README.md), OpenAPI generado y entidades/migraciones backend. |
| Integrar el nombre libre del responsable de campaña | [Contrato y ejemplo](../epe-web/docs/api/README.md#responsable-libre-de-campaña) y [estado de integración](../epe-web/docs/integration-status.md#responsable-libre-de-campaña--2026-11-08--parcial). |
| Guardar y consultar el documento de un chofer | [Contrato HTTP](../epe-web/docs/api/README.md#documento-del-chofer) y [migración](../epe-backend/docs/database.md#documento-del-chofer). |
| Cambiar diagramas de proceso | [fuentes Archify](business/flows/candidate.archify.md) y archivos `*.workflow.json` de esa carpeta. |

Los contratos y entregas guardan variedades y cantidades mediante una escritura atómica. Consulte el [contrato y compatibilidad HTTP](../epe-web/docs/api/README.md#desglose-de-contratos-y-entregas) y el [estado de integración](../epe-web/docs/integration-status.md#variedades-en-contratos-y-entregas--2026-11-05--completo-en-desarrollo-despliegue-pendiente).

El [portal compartido del chofer](business/processes.md#portal-compartido-del-chofer) reúne las entregas coordinadas y permite registrar sus cargas y etapas de despacho.
