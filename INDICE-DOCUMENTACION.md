# Centro de documentación del proyecto

Índice único de consulta para la documentación del proyecto. Cada fuente debe leerse según su alcance y fecha: los manuales e integración describen V1, el modelo agro describe el objetivo acordado y el prototipo es una referencia histórica. Consulte la [auditoría documental](auditoria-documentacion-2026-10-30.md) para antecedentes y la [revisión vigente de documentos y avance](estado-documentacion-y-avance.md) para estados actuales.

## Base de conocimiento consolidada

1. [Negocio y procesos](base-conocimiento/01-negocio-y-procesos.md): actores, recorrido, conceptos y reglas.
2. [Funciones, estado y evidencia](base-conocimiento/02-funciones-y-estado.md): matriz por área, resultados y pendientes.
3. [Referencia técnica](base-conocimiento/03-referencia-tecnica.md): componentes, modelo, contratos, despliegue y trazabilidad.

## Comience según su objetivo

| Necesidad | Lectura recomendada | Precaución |
|---|---|---|
| Entender el negocio | [Flujo visual](flujo-sistema.html) → [manual de administrador](../epe-web/docs/manuales/guia-administrador-v1.md) → [manual de chofer](../epe-web/docs/manuales/guia-chofer-v1.md) | El flujo visual usa el prototipo como referencia; confirme el comportamiento actual. |
| Documentar funciones y operación | Manuales anteriores → [estado de integración](../epe-web/docs/integration-status.md) → [QA histórico](../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) | La prueba histórica no acredita por sí sola el ciclo completo; hay confirmación posterior del usuario con distinto alcance de evidencia. |
| Documentar datos y reglas | [Acuerdos y modelo](README.md) → [reporte por vista](agro-schema/01_reporte_especifico.md) → [tablas y relaciones](agro-schema/02_tablas_y_relaciones.md) → [ER del backend](../epe-backend/docs/er-diagram.md) | El modelo objetivo y el backend implementado pueden diferir. |
| Documentar API e integración | [Estado por vista](../epe-web/docs/integration-status.md) → contrato OpenAPI V1 usado por los DTOs del frontend ([spec](../epe-web/docs/future-api.openapi.json), [reglas](../epe-web/docs/future-api-contract.md)) → Swagger del backend en `/api/docs` | El nombre `future-api` es histórico: la especificación sigue alimentando el cliente; su generación no acredita por sí sola despliegue ni paridad total. |
| Instalar u operar el backend | [README del backend](../epe-backend/README.md) → [despliegue on-premise](../epe-backend/docs/guia-on-premise-despliegue-backend.md) → [catálogos](../epe-backend/docs/default-data.md) | Verifique entorno, migraciones, credenciales y respaldo antes de ejecutar instrucciones. |
| Documentar frontend | [Arquitectura](../epe-web/docs/architecture-and-solid.md) → [sistema visual](../epe-web/docs/ui-and-design-system.md) → [estado de integración](../epe-web/docs/integration-status.md) | Las reglas de diseño y arquitectura no sustituyen una revisión del código actual. |

## Información base para futuras entregas

- **Actores:** Administrador y Chofer son los perfiles de operación descritos en los manuales; existen otros roles en los catálogos, sin que ello implique pantallas disponibles para ellos.
- **Recorrido de referencia:** preparación de datos, campaña y proveedores, acuerdos comerciales y transporte, calidad y cosecha, carga y despacho, facturación y liquidación, y cierre. Consulte los manuales y el flujo visual para las condiciones de cada paso.
- **Estado y evidencia:** el [seguimiento de integración](../epe-web/docs/integration-status.md) reúne resultados por fecha y alcance; el [informe QA](../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) conserva la ejecución histórica y su corrección. No presentar un resultado local como certificación productiva.
- **Modelo:** el SQL de [revisión](agro-schema/03_schema_total.sql) es para instalación nueva; el backend mantiene su propio SQL y migraciones. No extrapolar automáticamente una propuesta al entorno instalado.
- **Adjuntos e integraciones:** el seguimiento distingue la implementación parcial de certificados y la validación S3 pendiente; no asumir una plataforma general de archivos ni emisión real ante SUNAT.

## Criterio de lectura y mantenimiento

Para comportamiento actual, contraste código, configuración y pruebas con el estado de integración; para decisiones de negocio, identifique la fecha y el alcance de cada acuerdo. Trate el prototipo, las instantáneas y las auditorías anteriores como contexto. Al redactar, registre fuente, fecha, entorno, estado (implementado, propuesto, pendiente o histórico) y evidencia; señale las contradicciones en vez de elegir una versión sin comprobarla.

Los índices locales de [frontend](../epe-web/docs/README.md) y [backend](../epe-backend/docs/README.md) detallan sus documentos. Este archivo es la entrada central; [README](README.md) solo resume la estructura y deriva aquí.
