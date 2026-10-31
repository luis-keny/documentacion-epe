# Funciones, estado y evidencia

**Corte documental:** 30/10/2026. Esta matriz identifica fuentes y límites; «documentado» o «hay código» no equivale a probado en producción. La evidencia histórica pertenece al entorno y fecha indicados en cada fuente.

| Área | Alcance encontrado | Estado y evidencia | Fuente principal |
|---|---|---|---|
| Acceso | Selección de perfil y autenticación con usuario y contraseña; JWT para API privada. | Código de formulario y cliente presente; el seguimiento reporta pruebas de autenticación locales. Validar configuración y permisos del despliegue. | [Formulario](../../epe-web/src/modules/auth/components/FormControl.tsx) · [seguimiento](../../epe-web/docs/integration-status.md) |
| Proveedores y campañas | Maestros, fincas, participación, entrevistas y campañas. | Funciones descritas y operaciones recorridas en QA histórico; el nivel de conexión depende de vista y entorno. | [Manual](../../epe-web/docs/manuales/guia-administrador-v1.md) · [seguimiento](../../epe-web/docs/integration-status.md) |
| Comercial y transporte | Clientes, acuerdos, entregas, transportistas, vehículos, choferes y coordinación. | El recorrido histórico registró operaciones; consultar seguimiento para integración y límites específicos. | [QA corregido](../../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) |
| Calidad y cosecha | MTD, análisis, aprobación, cosecha y carga. | Código frontend y backend contiene validaciones de conteos; la ejecución histórica pasó por un bypass y no acredita aceptación integral. El seguimiento registra pruebas técnicas posteriores y confirmación funcional del usuario, con alcance distinto. | [Seguimiento](../../epe-web/docs/integration-status.md) · [QA corregido](../../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) |
| Logística y chofer | Seguimiento de viaje, recepción, checklist y cierres. | Persistencia observada en el QA histórico para las operaciones recorridas; no acredita expediente documental completo. | [Manual chofer](../../epe-web/docs/manuales/guia-chofer-v1.md) · [QA corregido](../../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) |
| Facturación y liquidaciones | Facturas, cobros y pagos a proveedor y transporte. | Registros y estados observados en QA local; no se acreditaron servicios externos bancarios ni SUNAT. | [QA corregido](../../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md) |
| Archivos | Flujo específico de certificados de proveedor; otros adjuntos aún limitados. | Código de almacenamiento y migración presentes; seguimiento reporta denegación de permisos S3 en su prueba. No afirmar carga real exitosa sin nueva evidencia. | [Seguimiento S3](../../epe-web/docs/integration-status.md) · [servicio](../../epe-backend/src/archivo/services/archivo.service.ts) |
| Base de datos | SQL objetivo, migraciones y catálogos. | El seguimiento reporta instalación y migración MTD en QA aislada; no demuestra la cadena completa ni una base productiva. | [Catálogos](../../epe-backend/docs/default-data.md) · [seguimiento](../../epe-web/docs/integration-status.md) |

## Lectura de resultados que parecen contradictorios

El informe E2E original llegó a un estado final y observó persistencia, pero una revisión posterior detectó que Calidad no había aprobado correctamente. La copia corregida invalida esa ejecución como aceptación integral. El seguimiento agrega después una confirmación funcional del usuario y resultados de pruebas técnicas, sin aportar en ese apartado una nueva ejecución E2E detallada equivalente. Son evidencias diferentes: atribuya cada conclusión a su fuente y alcance.

El seguimiento más reciente documenta builds y pruebas aprobados en una revisión posterior a la incidencia local de Vite, e instalación de la migración MTD en una base QA aislada. No se debe presentar el fallo anterior ni su pendiente como estado actual sin ese contexto; tampoco interpretar los resultados posteriores como validación completa de producción.

## Pendientes de documentación y aceptación

- Acordar si se necesita una nueva evidencia detallada del ciclo completo tras las correcciones de Calidad y qué criterios de aceptación se aplican.
- Definir la política de documentos requeridos para cierre logístico y comprobar adjuntos en el entorno previsto.
- Validar permisos y flujo real S3 cuando corresponda; distinguir certificados de una gestión general de archivos.
- Completar la documentación de operación real: entorno, versión desplegada, respaldo/restauración, monitoreo y responsables.
- Elaborar una matriz por pantalla y endpoint si se necesita afirmar disponibilidad exhaustiva; esta síntesis no es esa matriz.
