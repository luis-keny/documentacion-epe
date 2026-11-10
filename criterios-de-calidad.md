# Decisiones de ingeniería y calidad

Estas decisiones guían el código nuevo y los flujos que se modifiquen. La columna «Calidad relacionada» indica a qué característica de ISO/IEC 25010:2023 contribuye cada práctica. La evaluación del producto requiere pruebas y mediciones.

| Decisión | Por qué y cómo se aplica | Calidad relacionada |
|---|---|---|
| **Arquitectura por dominio** | Mantener la estructura avanzada del proyecto y asignar un responsable a cada regla. Backend modular por capas y frontend con Screaming Architecture. | Mantenibilidad |
| **Patrones con propósito** | Reutilizar los patrones adoptados en cada proyecto. Añadir uno cuando resuelva duplicación, acoplamiento o dificultad de prueba identificable. | Mantenibilidad |
| **SOLID** | Separar responsabilidades (S), extender mediante composición (O), respetar el comportamiento al sustituir implementaciones (L), acotar interfaces (I) y depender de contratos cuando se necesite sustituir colaboradores (D). | Mantenibilidad, incluida la capacidad de prueba |
| **KISS, DRY y YAGNI** | Preferir soluciones comprensibles, mantener una fuente para cada regla y crear abstracciones cuando exista una necesidad concreta. | Mantenibilidad |
| **Tipado y validación** | Tipar contratos y validar entradas externas. El backend verifica permisos, relaciones y estados antes de guardar. | Adecuación funcional y seguridad |
| **Contrato API compartido** | Sincronizar OpenAPI, backend, frontend y mock cuando cambie una operación. | Compatibilidad |
| **Integridad y concurrencia** | Usar restricciones y transacciones para datos relacionados. Probar solicitudes simultáneas y prevenir duplicados en operaciones críticas. | Fiabilidad y adecuación funcional |
| **Seguridad por defecto** | Aplicar mínimo privilegio, autorización por registro, manejo seguro de secretos y revisión de dependencias. | Seguridad |
| **Errores recuperables** | Informar qué se guardó ante un fallo parcial y definir cuándo un reintento es seguro. Registrar errores con contexto y sin secretos. | Fiabilidad |
| **Pruebas según riesgo** | Probar reglas con pruebas unitarias, persistencia con integración y recorridos críticos con E2E. Incluir rechazos, concurrencia y fallos parciales. | Adecuación funcional y fiabilidad |
| **Rendimiento medido** | Medir tiempos y volumen de datos con carga representativa antes de optimizar. Acotar consultas, peticiones y trabajo de renderizado. | Eficiencia de desempeño |
| **Accesibilidad y claridad** | Verificar teclado, foco, etiquetas, contraste, estados de carga y errores comprensibles en móvil y escritorio. | Capacidad de interacción |
| **Despliegue y recuperación** | Validar cambios en CI, versionar migraciones y ensayar actualización, restauración de respaldos y recuperación del servicio. | Fiabilidad y flexibilidad |
| **Observabilidad** | Usar comprobaciones de salud, registros y métricas para detectar fallos y explicar su causa. | Fiabilidad y mantenibilidad |
| **Prevención de daño operativo** | Identificar operaciones con consecuencias sobre personas o productos y verificar sus bloqueos. Por ejemplo, impedir el despacho de una carga pendiente de Calidad evita que salga sin la revisión requerida. | Seguridad operacional (safety) |

**Criterio de aceptación.** Indica la regla y su módulo responsable, el impacto en datos y permisos cuando aplique, y la evidencia de verificación. Registra las brechas de integración en el [seguimiento por vista](../epe-web/docs/integration-status.md) y enlaza la evidencia técnica desde la guía del flujo afectado.

- **Concurrencia.** La [prueba del cupo por variedad](../epe-web/dev/varieties-workflow.test.ts) comprueba dos solicitudes simultáneas con el mock HTTP. Para validar el bloqueo en producción, la evidencia pertinente es una prueba de integración con PostgreSQL.
- **Recuperación.** El [ensayo del 30 de octubre](../epe-web/docs/integration-status.md#verificación-de-calidad-isoiec-25010--2026-10-30--parcial) registra una restauración en PostgreSQL de QA y detalla qué se comparó. La recuperación productiva requiere evidencia de ese entorno.

Las decisiones específicas viven en las guías de [backend](../epe-backend/docs/architecture.md) y [frontend](../epe-web/docs/architecture.md). El modelo de calidad se consulta en la [publicación oficial de ISO](https://www.iso.org/standard/78176.html).
