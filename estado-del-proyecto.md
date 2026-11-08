# Estado del proyecto

**Actualizado:** 05/11/2026. Resumen coordinado de la documentación de `epe-web` y `epe-backend`.

## Estado vigente

| Área | Estado | Fuente de detalle |
|---|---|---|
| Backend y API | **Completado**, según confirmación del usuario. | [Backend](../epe-backend/README.md) · [documentación backend](../epe-backend/docs/README.md) |
| Interfaz frontend | **Visualmente completa**, según confirmación del usuario; admite modificaciones solicitadas siguiendo el flujo de cambios. | [Arquitectura frontend](../epe-web/docs/architecture.md) · [sistema visual](../epe-web/docs/design-system.md) |
| Integración de vistas con API | El detalle se mantiene en el registro vivo por vista; sus entradas antiguas son historial. | [Estado de integración](../epe-web/docs/integration-status.md) |
| Contrato API | OpenAPI V1 se genera desde el SQL fuente de contrato del frontend; su salida y la copia de ejecución del backend están sincronizadas. Controllers y migraciones definen la implementación. | [Fuente y reglas](../epe-web/docs/api/README.md) · [OpenAPI frontend](../epe-web/docs/api/openapi.json) · [copia backend](../epe-backend/src/common/v1/contract/api-v1.openapi.json) |
| Modelo objetivo | Se conserva separado de entidades y migraciones implementadas. | [Entrada del modelo](target-model/README.md) · [ER backend](../epe-backend/docs/er-diagram.md) |

La finalización del backend y de la parte visual se registra por confirmación del usuario. Este resumen no afirma por sí solo la validación de un despliegue productivo.

Los cambios solicitados se coordinan entre vistas, reglas de negocio y datos simulados mediante el [flujo de cambios](../epe-web/docs/development.md#cambios-de-vistas-reglas-de-negocio-y-mock). Cada entrega debe distinguir lo implementado con API real de lo simulado y explicar brevemente las implicaciones para el desarrollador. Esta revisión de instrucciones no modifica funcionalidades ni datos.

La [optimización de peticiones por vista](../epe-web/docs/integration-status.md#optimización-de-peticiones-por-vista--2026-11-05--implementada-en-desarrollo-y-revisada) sustituye las recargas globales tras guardar por integración de respuestas confirmadas y cargas del ámbito activo. Campañas arranca con dos GET y el alta sin documento usa un POST sin lecturas adicionales en las pruebas locales. Se conserva el histórico que necesitan UIT/adelantos y los indicadores actuales. El [diseño de referencia](../epe-web/docs/integration-status.md#plan-de-consumo-api-por-vista--2026-11-05--referencia-de-diseño) cubre las 48 rutas con pantalla; las lecturas agregadas nuevas siguen siendo opcionales. No hubo cambios visuales, de esquema ni de contrato backend. La discrepancia decimal del generador quedó resuelta y las copias OpenAPI siguen idénticas. La validación es local; no acredita un despliegue productivo.

## Fuentes vigentes y su propósito

- [README compartido](README.md): rutas de consulta para personas y agentes, sin lectura obligatoria para solicitudes ajenas al tema.
- [Seguimiento frontend](../epe-web/docs/integration-status.md): implementación e integración por vista; única fuente detallada de ese estado.
- [Índice backend](../epe-backend/docs/README.md): API, modelo, catálogos y operación backend. El [flujo del backend](../epe-backend/docs/backend-flow.md) documenta el arranque, peticiones y almacenamiento en S3.
- [Índice frontend](../epe-web/docs/README.md): arquitectura, sistema visual, manuales y contrato consumido.
- [Fuente de generación y OpenAPI compartido](../epe-web/docs/api/README.md): SQL de contrato, salida del generador y copia runtime backend.

## Versiones con vida útil

Los documentos fechados son evidencia o cortes de modelo, no instrucciones de implementación. Según la regla de 90 días en [AGENTS.md](AGENTS.md), vencen:

- **25/01/2027:** comparación backend–modelo revisada el 27/10/2026.
- **27/01/2027:** fuentes del modelo objetivo y acuerdos revisados el 29/10/2026.
- **28/01/2027:** QA y auditoría documental del 30/10/2026.

El historial de integración frontend también vence 90 días después de cada entrada. Renueva solo lo que siga respaldando una decisión vigente.

Los contratos y entregas ya tienen persistencia transaccional por variedad en desarrollo, con saldos independientes y edición sin doble descuento. La migración se verificó solo en PostgreSQL dedicado de pruebas; su despliegue sigue pendiente. Los históricos no confirmados se identifican y no afectan los cupos actuales, según la decisión del usuario. Consulte el [seguimiento de integración](../epe-web/docs/integration-status.md#variedades-en-contratos-y-entregas--2026-11-05--completo-en-desarrollo-despliegue-pendiente).
