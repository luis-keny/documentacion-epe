# Negocio y procesos del sistema

**Corte documental:** 30/10/2026. Síntesis preparada a partir de los manuales V1 y las decisiones del modelo. Describe el recorrido previsto y la información registrada; no acredita que cada operación esté disponible en cualquier despliegue. Para estado y evidencia consulte [funciones y validación](02-funciones-y-estado.md).

## Propósito y actores

Agro Exportaciones F.V. organiza una operación agroexportadora alrededor de campañas: conecta abastecimiento de fruta, acuerdos con clientes, transporte, control de calidad, entrega y liquidación. El flujo visual proporciona una [vista general basada en el prototipo](../flujo-sistema.html).

| Actor | Participación documentada |
|---|---|
| Administrador | Prepara datos, coordina campañas, clientes, proveedores y transporte; gestiona calidad, logística, facturación y liquidaciones. |
| Chofer | Consulta cargas y registra etapas del viaje, checklist y guía de salida. |
| Proveedor/productor o acopiador | Participa en una campaña y aporta fruta; el productor puede asociarse a fincas mediante entrevistas. |
| Cliente | Tiene requerimientos, contratos y entregas vinculados a la campaña. |
| Transportista | Aporta vehículos y choferes y participa mediante acuerdos y coordinaciones. |

Administrador y Chofer son los perfiles de operación de los manuales. El catálogo también incluye otros roles; eso no demuestra que tengan un portal o permisos equivalentes. Fuentes: [manual administrador](../../epe-web/docs/manuales/guia-administrador-v1.md), [manual chofer](../../epe-web/docs/manuales/guia-chofer-v1.md), [catálogos](../../epe-backend/docs/default-data.md).

## Recorrido de referencia

| Etapa | Información relevante | Resultado esperado según manuales |
|---|---|---|
| 1. Preparación | Proveedores, fincas, clientes, transportistas, vehículos y choferes; catálogos de fruta y variedad. | Datos disponibles para planificar. |
| 2. Campaña | Nombre, fruta, meta, fechas, participantes y entrevistas de finca. | Campaña planificada con abastecimiento identificado. |
| 3. Comercial y transporte | Cliente, cantidades, precio, moneda, destino, entrega; acuerdo, vehículo, chofer y horarios. | Entrega coordinada y recursos asignados. |
| 4. Calidad | Conteos MTD por origen, límite aplicable y análisis de laboratorio. | Decisión de aprobación para cosecha cuando se cumplen las condiciones. |
| 5. Cosecha y carga | Cuadrilla, materiales, kilos, cajas, origen y costos; guía de traslado. | Cosecha y carga registradas para despacho. |
| 6. Logística | Eventos del viaje, recepción, kilos aceptados, checklist y guía de salida. | Cierre físico, cierre del chofer y cierre administrativo según el flujo descrito. |
| 7. Finanzas | Factura y cobros, liquidación de proveedor y transporte, referencias de pago. | Saldos y estados registrados para revisión. |
| 8. Cierre | Revisión de hitos operativos y financieros y motivo de cierre. | Campaña terminada según las condiciones aplicables. |

Este orden resume los manuales; los pasos concretos y sus condiciones se deben verificar en la versión desplegada. [Manual de administrador](../../epe-web/docs/manuales/guia-administrador-v1.md) · [Manual de chofer](../../epe-web/docs/manuales/guia-chofer-v1.md).

## Reglas y términos útiles

- **Campaña:** agrupa la operación de una fruta y sus participantes. **Participación:** vínculo del proveedor con una campaña; las entrevistas relacionan la participación con las fincas del productor.
- **Entrega programada:** compromiso comercial; la **coordinación** identifica los recursos y origen del viaje; la **carga** registra la operación física. El contrato objetivo describe una entrega, una coordinación y una carga por viaje; confirme su implementación antes de afirmarlo para un entorno.
- **MTD:** moscas capturadas divididas entre trampas evaluadas y días de exposición. El manual exige conteos completos por origen, dos tipos de análisis distintos, uno de Maduración o Materia seca, y resultados aptos. Se observaron validaciones relacionadas en [frontend](../../epe-web/src/modules/quality/components/QualityDeliveryReviewModal.tsx) y [backend](../../epe-backend/src/common/v1/v1-business.service.ts); no se ejecutó el flujo en esta revisión.
- **Kilos reconocidos:** cantidad aceptada en planta para el proveedor, relevante para la liquidación de compra en el modelo objetivo. **Adelanto de transporte:** distinguir monto acordado, desembolsado, aplicado y disponible.
- Una guía o factura registrada en la aplicación y un pago con referencia no prueban por sí mismos emisión ante SUNAT ni operación bancaria real.

Fuentes de las reglas: [contrato objetivo](../../epe-web/docs/future-api-contract.md), [acuerdos](../README.md) y [QA corregido](../../epe-web/docs/pruebas/qa-e2e-flujos-negocio-v1-2026-10-30.md). Para reglas detalladas y excepciones consulte el [reporte por vista](../agro-schema/01_reporte_especifico.md).
