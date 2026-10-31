# APIs futuras: guía para implementar backend y consumo frontend

Contrato preparado el **2026-10-29** a partir de los acuerdos y el SQL objetivo de esta carpeta. La implementación HTTP se versiona como `/v1`; no equivale a endpoints ya disponibles en `epe-backend`.

La entrega completa se conserva con el frontend para que OpenAPI, mocks y clientes puedan verificarse juntos:

- **[Guía del contrato y de implementación](../epe-web/docs/future-api-contract.md)**: arquitectura backend, reglas por flujo, consumo frontend, discrepancias con las pantallas actuales, migraciones y criterios de aceptación.
- **[OpenAPI 3.1](../epe-web/docs/future-api.openapi.json)**: cuerpos de entrada/salida, rutas, métodos, tipos, errores y filtros.
- **[Catálogo de endpoints](../epe-web/docs/future-api-endpoints.md)**: 57 recursos de consulta/escritura y 117 rutas, con sus padres y tablas.
- **[Datos ficticios futuros](../epe-web/json/future/)**: escenario coherente con documentos textuales, borradores, recepción reconocida, varias facturas, pagos y adelantos.

El agente backend debe leer primero la guía y usar OpenAPI junto al [SQL objetivo](agro-schema/03_schema_total.sql). El SQL de instalación nueva no se ejecuta como migración sobre la base actual: hay que preparar migraciones incrementales. Las decisiones de almacenamiento documental y autenticación que siguen pendientes permanecen señaladas; no se crea una tabla de sesiones ni se inventa una subida de archivos.

En `epe-web`, los servicios futuros están en `src/modules/*/api/future.api.ts`, sus DTOs en `future.dto.ts` y las acciones de emisión/cierre en `future-actions.api.ts`. Se consumen con `VITE_API_BASE_URL=/mock-api/` y `pnpm dev`. Los servicios actuales sin versión y las pantallas existentes conservan su comportamiento hasta migrarlas explícitamente; no hay fallback de errores reales a datos ficticios.

Verificación y mantenimiento, desde `epe-web`: `pnpm contract:check`, `pnpm test`, `pnpm build`. `pnpm contract:generate` regenera el contrato y los clientes desde el SQL objetivo y las decisiones HTTP del generador; no modifica ni implementa el backend.
