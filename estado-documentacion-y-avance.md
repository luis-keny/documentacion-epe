# Estado de documentación e implementación

**Revisión estática:** 03/11/2026. Se contrastaron documentos y código local de `epe-web`, `epe-backend` y `epe-backend-security`. No se inició un entorno desplegado ni se ejecutaron pruebas en esta revisión. «Implementado» significa que hay código/rutas locales; no certifica el entorno productivo.

## Estado de implementación

| Área | Estado observado | Qué falta o qué limita la conclusión |
|---|---|---|
| API backend V1 | **Implementada en código para los flujos principales.** Hay controladores para autenticación, campañas, proveedores/participaciones, calidad/cosecha/cargas/guías, clientes, facturación, liquidaciones, logística y transporte. Swagger está configurado en `/api/docs`. | No comprobé aquí qué versión está desplegada ni la paridad de la base productiva. Una lista de controladores no acredita que todos los requisitos de negocio estén cerrados. |
| Frontend conectado a V1 | **Implementación amplia y activa.** Las pantallas importan clientes y DTOs generados desde `future.api`/OpenAPI. El seguimiento del 02/11 reporta pruebas HTTP, compilación, pruebas manuales en Brave y flujos V1 completos en desarrollo para Facturación/Cobros, Liquidación, Logística y guías. | La evidencia es local/de desarrollo. No equivale a aceptación productiva ni a una auditoría funcional nueva de todas las rutas. |
| Calidad y cosecha | **Implementadas en desarrollo** con análisis, MTD, cargas y guías conectadas a comandos V1; el seguimiento registra correcciones y pruebas. | Debe leerse junto con la evidencia y sus límites de entorno. El QA histórico del 30/10 tuvo un bypass y no sirve por sí solo como aceptación integral. |
| Proveedores, clientes y transporte | **Parcial por pantalla.** Existen CRUD y endpoints, además de pantallas conectadas; parte de las operaciones secundarias o adjuntos conserva límites. | El seguimiento marca parcial la ficha de cliente dentro de campaña, la cotización de transportista y algunas páginas de vehículos/choferes. La persistencia del archivo de cotización está pendiente. |
| Cierre de acuerdo de transporte | **Pendiente de definición funcional.** La V1 persiste pagos reales y no un cierre administrativo manual del saldo. | Definir si se solicita un pago real o un estado administrativo adicional antes de implementar el botón. |
| Archivos | **Parcial.** Hay almacenamiento local y código de servicio S3; Facturación/Logística usan rutas locales de archivo en desarrollo. | El seguimiento registra denegación de permisos AWS para escritura S3 y no verifica almacenamiento persistente en el backend desplegado. No hay emisión SUNAT: la factura se registra después de emitirse externamente. |
| Despliegue y operación | **Documentados, no verificados en esta revisión.** Hay guía on-premise, migraciones, semillas y configuración de seguridad. | Confirmar versión, migraciones aplicadas, variables, respaldo/restauración, monitoreo y permisos en el servidor real. |
| Modelo `docs/agro-schema` | **Modelo objetivo/documental**, separado de las entidades y migraciones TypeORM que ejecuta el backend. | No tratar el SQL central como estado desplegado ni como fuente de verdad de la API actual. La comparación estática vigente parte del backend y sus migraciones. |

### Sobre «API futura»

Se eliminó `docs/api-futura.md`, que solo reenviaba a otros documentos y describía el backend como trabajo futuro. **No se eliminaron** `epe-web/docs/future-api.openapi.json`, `future-api-contract.md`, `future-api-endpoints.md` ni los módulos TypeScript `future.api.ts`: hoy el generador `pnpm contract:generate` crea DTOs desde ese OpenAPI y las pantallas V1 importan esos clientes. `future-api` es un nombre heredado; el conjunto sirve de contrato técnico activo del frontend. El backend publica su Swagger generado en `/api/docs`. Antes de retirar o renombrar esos artefactos hay que migrar el generador y sus consumidores, y verificar equivalencia contra el backend.

## Inventario de documentos centrales

### Entrada, negocio y operación

| Archivo | Objetivo | Estado/uso |
|---|---|---|
| [README.md](README.md) | Entrada corta a la estructura documental. | Vigente; deriva al índice. |
| [INDICE-DOCUMENTACION.md](INDICE-DOCUMENTACION.md) | Encontrar fuentes por objetivo y entender su alcance. | Vigente; revisar sus enlaces al cambiar fuentes. |
| [auditoria-documentacion-2026-10-30.md](auditoria-documentacion-2026-10-30.md) | Registrar duplicados, contradicciones y método de mantenimiento detectados en octubre. | Histórica; la fila de API se actualizó para reflejar la eliminación y la dependencia vigente. |
| [base-conocimiento/01-negocio-y-procesos.md](base-conocimiento/01-negocio-y-procesos.md) | Actores, proceso y reglas principales. | Resumen de negocio; algunas fuentes asociadas describen modelo/contrato, no despliegue. |
| [base-conocimiento/02-funciones-y-estado.md](base-conocimiento/02-funciones-y-estado.md) | Matriz resumida de funciones y evidencia. | Corte 30/10; conservar como instantánea y consultar este estado para avances posteriores. |
| [base-conocimiento/03-referencia-tecnica.md](base-conocimiento/03-referencia-tecnica.md) | Componentes, modelo, contratos y fuentes técnicas. | Útil como mapa; actualizar cuando cambie el entorno o el contrato. |
| `manuales/guia-usuario-v1.md` | Índice de los manuales de usuario. | Copia central; manuales de `epe-web/docs/manuales/` son la ruta de mantenimiento indicada por su README. |
| `manuales/guia-administrador-v1.md` | Operación del perfil administrador. | Copia histórica; comprobar contra frontend vigente antes de entregar. |
| `manuales/guia-chofer-v1.md` | Operación del perfil chofer. | Copia histórica; comprobar contra frontend vigente antes de entregar. |
| `pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md` | Evidencia de un recorrido E2E fechado. | Histórica; la revisión correctiva detectó un bypass de calidad. No usar como aceptación integral. |

### Modelo agro y datos

| Archivo | Objetivo | Estado/uso |
|---|---|---|
| `agro-schema/01_reporte_especifico.md` | Explicar el modelo por vista, relaciones y reglas del objetivo. | Propuesta/objetivo funcional; no equivale a API o BD desplegada. |
| `agro-schema/02_tablas_y_relaciones.md` | Mostrar tablas, relaciones y recortes Mermaid por vista. | Derivado del modelo objetivo. |
| `agro-schema/03_schema_total.sql` | Instalar el esquema objetivo en una base nueva para revisión. | No es migración incremental ni evidencia de una instalación productiva. |
| `agro-schema/04_datos_iniciales.sql` | Sembrar catálogos iniciales del modelo objetivo. | Útil junto al SQL objetivo; no es semilla para datos operativos productivos. |
| `agro-schema/auditoria-bd-actual-vs-planificada.md` | Comparar estructura del backend con el modelo propuesto. | Referencia histórica de brechas; confirmar contra las migraciones más recientes. |
| `agro-schema/auditoria-tablas-propuestas-vs-prototipo.md` | Justificar propuestas de tablas frente a los flujos del prototipo. | Decisiones/modelo objetivo; no certifica implementación. |
| `agro-schema/auditoria-tablas-propuestas.json` | Datos estructurados de las propuestas auditadas. | Artefacto de análisis, relacionado con la auditoría Markdown. |
| `agro-schema/referencias/AGRO_SIMPLIFICADO.dbml` | Conservar el DBML inicial recibido. | Fuente histórica inmutable; no es el esquema actual. |
| `agro-schema/diagramas/esquema-agro.html` | Presentar el ER general del modelo objetivo. | Visualización derivada. |
| `agro-schema/diagramas/esquema-agro-vistas.html` | Navegar diagramas del modelo por vista. | Visualización derivada. |
| `agro-schema/diagramas/schema-global.erd.json` y `views/*.erd.json` | Guardar los datos ER que alimentan diagramas globales/por vista. | Artefactos de diagramación; regenerar solo desde sus fuentes acordadas. |
| `agro-schema/diagramas/candidate.archify.md` | Especificación fuente de los diagramas de esquema. | Fuente de generación, no manual de producto. |
| `agro-schema/diagramas/build_view_diagrams.py`, `audit_panel.py`, `update_summary_diagrams.py` | Generar/actualizar vistas y paneles de diagramas. | Herramientas; no son evidencia de estado de BD. |
| `agro-schema/.validation/` | Guardar generadores, modelos, consultas y resultados de revisión del esquema. | Evidencia local del modelo (PGlite/estática); no prueba el backend o una BD desplegada. `node_modules`, `__pycache__` y logs son auxiliares generados, no documentación de referencia. |

### Flujos y visualizaciones

| Archivo | Objetivo | Estado/uso |
|---|---|---|
| `flujo-sistema.html` | Explicar visualmente el flujo general basado en el prototipo. | Referencia funcional, no guía del comportamiento conectado actual. |
| `flujo-sistema.delivery.json` | Registrar la entrega del artefacto HTML. | Metadato de generación. |
| `flujo-sistema.finalize.json` y `flujo-sistema.finalize-summary.json` | Guardar resultado y resumen de validación de la generación. | Evidencia de generación; el receipt indica que la revisión en navegador no se ejecutó. |
| `archify-flujo-sistema/candidate.archify.md` | Definir la fuente del flujo visual. | Documento fuente del generador; contiene referencias al prototipo. |
| `archify-flujo-sistema/flujo-general.workflow.json` | Datos del flujo general. | Artefacto fuente/derivado del diagrama. |
| `archify-flujo-sistema/flujo-chofer.workflow.json` | Datos del flujo de chofer. | Artefacto fuente/derivado del diagrama. |
| `archify-flujo-sistema/flujo-exportacion.workflow.json` | Datos del flujo de exportación. | Artefacto fuente/derivado del diagrama. |
| `archify-flujo-sistema/flujo-financiero.workflow.json` | Datos del flujo financiero. | Artefacto fuente/derivado del diagrama. |
| `archify-flujo-sistema/review-3/*` | Conservar el receipt y el resumen de la revisión final vigente. | Evidencia de generación; navegador no revisado según el receipt. `review-2` fue eliminada por obsoleta. |
| `archify-flujo-sistema/preview-*.png` | Mostrar capturas de vistas previas de los diagramas. | Material visual auxiliar, no capturas de la app ni evidencia de producción. |

### Prototipo

| Ruta | Objetivo | Estado/uso |
|---|---|---|
| `prototipo/` | Conservar el prototipo y su proyecto completo como referencia de diseño y flujo. | Se mantiene intacto según instrucción del usuario. No tomarlo como prueba del estado del frontend V1. |

## Documentación de proyectos que debe leerse junto a este inventario

- `epe-web/docs/integration-status.md`: fuente más reciente de implementación por vista; su cabecera llega al 02/11/2026. Tiene un historial largo y sus tablas antiguas no deben prevalecer sobre las entradas superiores más recientes.
- `epe-web/README.md`: instrucciones de desarrollo, pero conserva secciones de estado anteriores y referencias `future-api`; necesita alinearse con el seguimiento actual.
- `epe-backend/docs/README.md`, `default-data.md`, `er-diagram.md`, `datos-ejemplo.md` y `guia-on-premise-despliegue-backend.md`: operación, esquema, semillas y despliegue. Son documentación local; la guía no prueba que el servidor productivo ejecute esa versión.
- `epe-backend-security/docs/`: documentación de otra variante/checkout. No mezclarla con `epe-backend` hasta confirmar cuál es el destino de despliegue; sus guías difieren en almacenamiento documental.

## Pendientes documentales

1. Actualizar el estado y la tabla de módulos del `epe-web/README.md` con los avances del 02/11 y retirar los estados antiguos que contradigan el seguimiento actual.
2. Comparar el OpenAPI que genera clientes con el Swagger real del backend, documentar diferencias y decidir si se renombra el conjunto `future-api` sin interrumpir `contract:generate`.
3. Confirmar cuál backend (`epe-backend` o `epe-backend-security`) es el destino operativo y registrar versión, migraciones y evidencia productiva.
4. Mantener manuales centrales solo si se actualizarán junto a los canónicos del frontend; si no, marcarlos como copias históricas para evitar ediciones divergentes.
5. Excluir del control documental los artefactos generados sin valor de referencia (`__pycache__`, `node_modules`, logs); conservar resultados de validación citados como evidencia.
