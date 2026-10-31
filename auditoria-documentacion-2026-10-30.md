# Auditoría de la documentación local

**Fecha de revisión:** 30/10/2026. **Alcance:** inventario y clasificación de la documentación local de `docs`, `epe-web/docs`, `epe-backend/docs` y `epe-backend-security/docs`, índices y archivos de referencia del prototipo. Se contrastaron índices, encabezados, duplicados mediante hash y diferencias concretas de manual y QA. Se revisaron los pasajes relevantes del seguimiento y contrato; no se comprobó línea por línea cada documento extenso, ni se ejecutaron pruebas, migraciones o una aplicación. Las conclusiones sobre el sistema se atribuyen a sus fuentes, no son una verificación nueva.

## Hallazgos prioritarios

| Prioridad | Hallazgo y evidencia | Consecuencia y acción recomendada |
|---|---|---|
| Alta | El [QA raíz](pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) concluye «aprobado con observaciones», mientras la [copia del frontend](../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) corrige el resultado: hubo un bypass de Calidad y el recorrido histórico no acredita el ciclo completo. | No usar la conclusión raíz como aceptación. Conservar ambas como evidencia histórica e identificar la copia frontend como corrección de esa ejecución. |
| Alta | El [seguimiento de integración](../epe-web/docs/integration-status.md) registra una confirmación funcional posterior del usuario y pruebas técnicas posteriores, pero también conserva el QA anterior pendiente. La confirmación y la ejecución histórica tienen evidencias y alcances distintos. | Para una aceptación formal, definir criterios y documentar una nueva evidencia de extremo a extremo o la aceptación explícita aplicable; no inferir que los tests técnicos sustituyen ese recorrido. |
| Alta | El [manual de administrador raíz](manuales/guia-administrador-v1.md) y el [del frontend](../epe-web/docs/manuales/guia-administrador-v1.md) discrepan en Calidad: el segundo detalla conteos MTD y requisitos de análisis. El índice del frontend declara canónicos sus manuales. | Usar el manual del frontend como punto de partida y verificar la versión instalada. Sincronizar o retirar la duplicación en una tarea controlada. |
| Alta | [API futura](api-futura.md) y el [contrato](../epe-web/docs/future-api-contract.md) describen decisiones de 2026-10-29, incluyendo autenticación y archivos pendientes; el [seguimiento](../epe-web/docs/integration-status.md) documenta avances posteriores en JWT y certificados S3. | Etiquetar esos contratos como objetivo/instantánea y contrastar por funcionalidad con código y seguimiento antes de documentar disponibilidad. |
| Media | Las dos copias de `01_reporte_especifico.md` y `02_tablas_y_relaciones.md` en raíz y `epe-web/docs/reference` son idénticas; el [README de referencia](../epe-web/docs/reference/README.md) las identifica como instantánea para generar contrato. Las guías de chofer también son idénticas. | No editar la instantánea aisladamente: seguir su procedimiento de sincronización y generación. Definir responsable de cada copia. |
| Media | `epe-backend-security/docs` comparte auditoría y datos de ejemplo con `epe-backend/docs`, pero su ER y guía de despliegue difieren. No se estableció en esta revisión cuál árbol corresponde al despliegue elegido. | Confirmar propósito y versión de ambos árboles antes de consolidar o usar sus instrucciones; no mezclar ER ni despliegue. |
| Media | El [índice original](README.md) mezcla acuerdos, SQL objetivo, resultados y referencias históricas; presenta enlaces de operación junto con propuestas. Los documentos por vista son extensos. | Usar el [centro de documentación](INDICE-DOCUMENTACION.md) por objetivo y declarar estado y procedencia en futuros documentos. |
| Media | El seguimiento contiene entradas históricas con resultados y pendientes diferentes el mismo día; en algunos casos entradas posteriores los aclaran. | Citar apartado y alcance exactos, no solo la fecha; mantener un resumen de estado con evidencia y fecha de actualización en futuras revisiones. |

## Inventario por área

| Área | Contenido | Uso recomendado |
|---|---|---|
| [Documentación central](README.md) | Acuerdos, modelo por vista, auditorías de esquema, SQL, diagramas HTML, manuales, QA y prototipo. | Base de negocio y modelo objetivo; verificar las excepciones anteriores. |
| [Frontend](../epe-web/docs/README.md) | Manuales canónicos del repositorio, QA corregido, integración, contrato/OpenAPI, arquitectura, diseño y copia de referencia. | Fuente principal de seguimiento de integración y manuales; el contrato no acredita implementación. |
| [Backend](../epe-backend/docs/README.md) | Despliegue, catálogos, ejemplos, ER y auditoría de modelo. | Operación y modelo de ese repositorio, contrastados con migraciones y entorno. |
| [Backend security](../epe-backend-security/README.md) | Otra copia de backend con documentación parcialmente distinta y cambios OpenSpec. | Referencia separada hasta determinar su relación con el backend de trabajo. |
| [Prototipo](prototipo/Campaign%20Management%20System/) | Aplicación y documentos de flujos, liquidaciones, exportación y datos demo. | Antecedente funcional; no prueba comportamiento de V1 actual. |
| `.validation`, diagramas, JSON, SQL y OpenAPI | Evidencias, generadores, artefactos y esquemas además de Markdown. | Usar según su propósito; una comprobación del modelo no demuestra el estado de una base desplegada. |
| `odd/tasks`, `openspec/changes`, instrucciones AGENTS/CLAUDE | Tareas, propuestas, verificaciones e instrucciones para agentes. | Contexto de trabajo, no requisitos aprobados automáticamente ni manuales de usuario. |

## Vacíos para futuras documentaciones

1. Identificar destinatario, propósito, responsable, versión y entorno de cada entrega.
2. Elaborar una matriz de funciones por módulo con estado, fuente, evidencia y fecha; distinguir implementado, parcial, propuesto y pendiente.
3. Resolver formalmente qué fuente mantener para cada duplicado y la función de `epe-backend-security`.
4. Acordar criterios de aceptación y registrar evidencia integral posterior a los cambios de Calidad, si se requiere acreditar el ciclo completo.
5. Documentar por separado el despliegue real, migraciones aplicadas, recuperación, permisos, integraciones y límites de cada entorno; las guías actuales no prueban su ejecución productiva.
6. Revisar los requisitos de adjuntos y cierre logístico y la validación real de S3 antes de describirlos como disponibles.

## Método de mantenimiento propuesto

Mantener un documento principal por tema y enlazarlo desde los índices; cuando una copia sea necesaria para generación o distribución, rotularla como instantánea y documentar cómo sincronizarla. Registrar fecha, responsable, fuente, alcance y estado en cada actualización. No borrar evidencias históricas ni sobrescribir resultados de pruebas; agregar correcciones vinculadas y distinguirlas de validaciones posteriores. Antes de una entrega, comprobar enlaces y contrastar sus afirmaciones con la versión y el entorno correspondientes.

## Acciones aplicadas en esta revisión

- Se creó la [base de conocimiento](INDICE-DOCUMENTACION.md#base-de-conocimiento-consolidada) con procesos, matriz de evidencia y referencia técnica.
- Se alineó la sección de Calidad del manual de administrador de la raíz con la copia del frontend y se corrigió el acceso de chofer en ambas copias conforme al formulario actual, que solicita usuario y contraseña.
- Se añadió un aviso al QA histórico de la raíz con enlace a la corrección, preservando el resultado original como antecedente.
- Se identificaron las ramas locales de ambos backends y la discrepancia de 60/65 tablas en documentos históricos; el SQL central contiene 60 sentencias `CREATE TABLE` por conteo estático.
- Quedan pendientes la revisión exhaustiva por pantalla y endpoint, la definición de propietarios documentales y cualquier validación adicional de entorno o aceptación funcional.
