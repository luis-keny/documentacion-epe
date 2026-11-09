# Negocio y procesos del sistema

Resumen vigente del negocio y sus actores. Describe el recorrido funcional; la disponibilidad de cada operación se mantiene en el [estado del proyecto](../estado-del-proyecto.md) y el [seguimiento por vista](../../epe-web/docs/integration-status.md).

## Propósito y actores

Agro Exportaciones F.V. organiza una operación agroexportadora alrededor de campañas: conecta abastecimiento de fruta, acuerdos con clientes, transporte, control de calidad, entrega y liquidación. El flujo visual proporciona una [vista general basada en el prototipo](flows/overview.html).

| Actor | Participación documentada |
|---|---|
| Administrador | Prepara datos, coordina campañas, clientes, proveedores y transporte; gestiona calidad, logística, facturación y liquidaciones. |
| Chofer | Consulta cargas y registra etapas del viaje, checklist y guía de salida. |
| Proveedor/productor o acopiador | Participa en una campaña y aporta fruta; el productor puede asociarse a fincas mediante entrevistas. |
| Cliente | Tiene requerimientos, contratos y entregas vinculados a la campaña. |
| Transportista | Aporta vehículos y choferes y participa mediante acuerdos y coordinaciones. |

Administrador y Chofer son los perfiles de operación de los manuales. El catálogo también incluye otros roles; eso no demuestra que tengan un portal o permisos equivalentes. Fuentes: [manual administrador](../../epe-web/docs/guides/administrator.md), [manual chofer](../../epe-web/docs/guides/driver.md), [semillas](../../epe-backend/docs/seed-data.md).

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

Este orden resume los manuales; los pasos concretos y sus condiciones se deben verificar en la versión desplegada. [Manual de administrador](../../epe-web/docs/guides/administrator.md) · [Manual de chofer](../../epe-web/docs/guides/driver.md).

## Reglas y términos útiles

- **Campaña:** agrupa la operación de una fruta y sus participantes. **Participación:** vínculo del proveedor con una campaña; las entrevistas relacionan la participación con las fincas del productor.
- **Entrega programada:** compromiso comercial; la **coordinación** identifica los recursos y origen del viaje; la **carga** registra la operación física. La V1 modela un viaje por entrega, coordinación y carga.
- **MTD:** moscas capturadas divididas entre trampas evaluadas y días de exposición. Sus requisitos operativos están en el [manual del administrador](../../epe-web/docs/guides/administrator.md).
- **Kilos reconocidos:** cantidad aceptada en planta para el proveedor, relevante para la liquidación de compra en el modelo objetivo. **Adelanto de transporte:** distinguir monto acordado, desembolsado, aplicado y disponible.
- Una guía o factura registrada en la aplicación y un pago con referencia no prueban por sí mismos emisión ante SUNAT ni operación bancaria real.

Fuentes: [reglas de API](../../epe-web/docs/api/business-rules.md), [modelo objetivo](../target-model/README.md), [estado del proyecto](../estado-del-proyecto.md) y [seguimiento por vista](../../epe-web/docs/integration-status.md). El QA fechado conserva evidencia histórica, no reglas del negocio vigentes.

## Cantidades contractuales por variedad

Cada contrato acuerda variedades de la fruta de campaña incluidas en el requerimiento del cliente. Cada entrega programa solo esas variedades, sin transferir saldo entre ellas. El backend deriva totales y valida el desglose bajo bloqueo y en una transacción. Al editar, excluye toda la entrega original y sustituye sus líneas; reducir, quitar filas o eliminar libera el consumo correspondiente si el flujo lo permite. No se puede reducir un contrato por debajo de sus entregas confirmadas.

El programa semanal muestra las entregas programadas por cliente y fecha y permite filtrar por variedad y placa. Los productores y acopiadores se pueden vincular tanto al planificar como durante la ejecución.

Por decisión del usuario, los históricos pendientes de regularización no afectan los cupos actuales. No se les inventa un reparto; se identifican con la marca de confirmación en falso. Un contrato necesita confirmar sus variedades antes de admitir nuevas entregas. Confirmar manualmente una entrega histórica la incorpora al consumo actual y exige saldo. El [contrato HTTP](../../epe-web/docs/api/README.md#desglose-de-contratos-y-entregas) define las operaciones y el [seguimiento](../../epe-web/docs/integration-status.md) distingue implementación, pruebas y despliegue.
