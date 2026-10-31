# Referencia técnica y fuentes de datos

**Corte documental:** 30/10/2026. Descripción del contenido local consultado; para cada despliegue verifique versión, configuración y migraciones.

## Componentes

| Componente | Función | Fuentes |
|---|---|---|
| `epe-web` | Interfaz web React/TypeScript, organizada por módulos funcionales; integra API y vistas. | [README](../../epe-web/README.md) · [arquitectura](../../epe-web/docs/architecture-and-solid.md) · [diseño](../../epe-web/docs/ui-and-design-system.md) |
| `epe-backend` | API NestJS/TypeScript con TypeORM y PostgreSQL, autenticación y módulos de negocio. | [README](../../epe-backend/README.md) · [ER](../../epe-backend/docs/er-diagram.md) |
| `epe-backend-security` | Otro checkout del backend; al revisar estaba en `feature/auth-security`, mientras `epe-backend` estaba en `master`. | [README](../../epe-backend-security/README.md). Confirmar su destino antes de usar sus guías o mezclar cambios. |
| `docs` | Acuerdos, modelo objetivo, SQL de revisión, diagramas, manuales y antecedentes. | [Índice original](../README.md) · [auditoría](../auditoria-documentacion-2026-10-30.md) |

La [guía on-premise](../../epe-backend/docs/guia-on-premise-despliegue-backend.md) describe frontend → proxy HTTPS → NestJS → PostgreSQL, con S3 privado y un flujo de despliegue mediante runner. Es una guía propuesta para ese entorno, no evidencia de que ya esté instalado. El README del backend admite Node 22 o superior; la guía de ese despliegue especifica Node 24. Aplicar el requisito del entorno correspondiente.

## Contrato, implementación y modelo

1. El [contrato HTTP](../../epe-web/docs/future-api-contract.md) y el [OpenAPI](../../epe-web/docs/future-api.openapi.json) documentan el objetivo V1 y sus convenciones. Su nombre «futuro» refleja su origen; no demuestra por sí solo el estado de implementación.
2. El [seguimiento de integración](../../epe-web/docs/integration-status.md), el código y las pruebas son fuentes complementarias para conocer la implementación local y sus límites. El README del frontend contiene una tabla de integración que puede ser anterior; no usarla aislada como estado actual.
3. El [SQL objetivo central](../agro-schema/03_schema_total.sql) se documenta como instalación nueva, no migración para una base con datos. La lectura estática de esta revisión encontró 60 sentencias `CREATE TABLE`; las auditorías incluyen cifras históricas contradictorias de 60 y 65, por lo que no debe citarse otra cifra sin identificar versión y método.
4. El backend tiene [SQL y migraciones](../../epe-backend/src/database/) propios y un [ER](../../epe-backend/docs/er-diagram.md). El modelo objetivo y una base efectivamente desplegada deben compararse por separado.
5. El SQL objetivo histórico difiere de la evolución posterior: el backend contiene una migración de `archivo` y otra de conteos MTD. El seguimiento limita la evidencia de S3; no confundir presencia de código o tabla con funcionamiento externo comprobado.

## Operación y seguridad

El backend documenta autenticación JWT, configuración CORS, secretos y cuentas iniciales en su [README](../../epe-backend/README.md); la configuración efectiva depende del entorno. Los [catálogos](../../epe-backend/docs/default-data.md) son datos de referencia, no una actualización normativa automática. Las instrucciones de instalación, migración, respaldo y recuperación deben verificarse antes de aplicarse a una instancia real.

## Trazabilidad para nuevas documentaciones

Para cada afirmación registre: **tema, fuente y enlace, fecha de la evidencia, entorno/versión, estado y limitación**. Use decisiones acordadas para describir el objetivo; código y pruebas para implementación local; y evidencia específica del entorno para afirmar despliegue. Documente contradicciones y responsable de resolverlas. Evite reproducir credenciales o datos personales en las entregas.
