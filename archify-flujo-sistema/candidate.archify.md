# Agro Exportaciones: del acuerdo comercial al cierre de campaña {#agro-flujo-sistema}

Agro Exportaciones coordina campañas de compra y venta de fruta: conecta clientes, proveedores, fincas, cosecha, transporte y recepción con sus documentos, cobros y pagos. La campaña reúne el historial; cada entrega conserva su vínculo con el contrato, la carga y sus participantes.

- Los ocho módulos del administrador comparten datos y se complementan con el recorrido móvil del chofer.[](source:app)
- Exportación e Industria tienen controles distintos antes de generar las guías de una carga.[](source:calidad)[](source:exportacion)
- La venta usa el peso recibido en planta; la compra del prototipo usa los kilos cargados de cada proveedor.[](source:origenes)
- El cierre de campaña exige resolver operaciones, documentos y obligaciones financieras.[](source:cierre)

@answer scope="Prototipo local · 27/10/2026 · finalidad inferida"
@meta locale=es quality_profile=showcase style=clean
@source app title="Menú, ocho módulos y acceso por perfil" path="prototipo/Campaign Management System/src/App.tsx" lines=17:28
@source acceso title="Entrada diferenciada de administrador y chofer" path="prototipo/Campaign Management System/src/App.tsx" lines=185:205
@source campanas title="Datos generales y secciones de campaña" path="prototipo/Campaign Management System/src/modules.tsx" lines=141:241
@source fechas title="Estado de campaña según la fecha de inicio en Lima" path="prototipo/Campaign Management System/src/store.tsx" lines=667:685
@source participacion title="Proveedores, exámenes y entrevistas dentro de campaña" path="prototipo/Campaign Management System/src/modules.tsx" lines=491:630
@source certificaciones title="Certificaciones, pagos y ampliaciones de campaña" path="prototipo/Campaign Management System/src/modules.tsx" lines=667:761
@source proveedores title="Padrón de proveedores y ficha general" path="prototipo/Campaign Management System/src/modules.tsx" lines=1086:1206
@source fincas title="Finca permanente y datos agronómicos por campaña" path="prototipo/Campaign Management System/src/farms.tsx" lines=8:45
@source padron-fincas title="Fincas y certificados del proveedor" path="prototipo/Campaign Management System/src/provider-sections.tsx" lines=8:25
@source comercial title="Clientes y participaciones comerciales" path="prototipo/Campaign Management System/src/modules.tsx" lines=1214:1380
@source contratos title="Contratos del cliente y precio de venta" path="prototipo/Campaign Management System/src/modules.tsx" lines=1449:1503
@source entregas title="Programación y coordinación de entregas" path="prototipo/Campaign Management System/src/modules.tsx" lines=1506:1570
@source transporte title="Padrón, vehículos, choferes y solicitudes simuladas" path="prototipo/Campaign Management System/src/modules.tsx" lines=1611:1657
@source cotizaciones title="Requerimiento, cotizaciones y selección de transportista" path="prototipo/Campaign Management System/src/modules.tsx" lines=1706:1746
@source acuerdo-transporte title="Transportistas y acuerdo de pago por campaña" path="prototipo/Campaign Management System/src/modules.tsx" lines=246:295
@source calidad title="Navegación vigente de calidad por campaña y canal" path="prototipo/Campaign Management System/src/quality-campaign.tsx" lines=12:57
@source exportacion title="Análisis, MTD y preparación de Exportación" path="prototipo/Campaign Management System/src/export-harvest.tsx" lines=8:66
@source cosecha title="Avances, cierre de cosecha y preparación de guía" path="prototipo/Campaign Management System/src/export-harvest.tsx" lines=109:152
@source industria title="Cargas de Industria y guías por entrega" path="prototipo/Campaign Management System/src/industry-loads.tsx" lines=22:48
@source carga title="Validación de calidad y registro de la carga" path="prototipo/Campaign Management System/src/load-registration.tsx" lines=24:74
@source lista-entrega title="Coordinación requerida y prevención de duplicados" path="prototipo/Campaign Management System/src/quality-load-utils.ts" lines=3:20
@source chofer title="Asignaciones del chofer, edición y avance de despacho" path="prototipo/Campaign Management System/src/driver-mobile.tsx" lines=32:79
@source estados-despacho title="Estados e historial del despacho" path="prototipo/Campaign Management System/src/dispatch-model.ts" lines=1:23
@source checklist-chofer title="Checklist de recepción y descarte exigido al chofer" path="prototipo/Campaign Management System/src/driver-receipt-model.ts" lines=8:38
@source mapa title="Mapa de fincas y origen de ruta" path="prototipo/Campaign Management System/src/driver-farm-map.tsx" lines=9:27
@source logistica title="Secciones del administrador en Logística" path="prototipo/Campaign Management System/src/logistics-overview.tsx" lines=10:23
@source recepcion title="Recepción, descarga, jabas y documentos de cierre" path="prototipo/Campaign Management System/src/modules.tsx" lines=2646:2720
@source reglas-recepcion title="Condiciones efectivas del cierre físico y administrativo" path="prototipo/Campaign Management System/src/business-integrity.ts" lines=81:86
@source origenes title="Origen y validación de los kilos de venta y compra" path="prototipo/Campaign Management System/src/finance-flow.ts" lines=19:98
@source validacion-compra title="Reglas de liquidación: compra en PEN y kilos del proveedor" path="prototipo/Campaign Management System/src/finance-flow.ts" lines=133:159
@source ventas title="Campaña, cliente, carga, factura y cobros" path="prototipo/Campaign Management System/src/sales-campaign-module.tsx" lines=20:108
@source emision title="Factura registrada y condición previa al cobro" path="prototipo/Campaign Management System/src/sales-billing.ts" lines=3:31
@source compras title="Liquidación y pago de proveedores y transportistas" path="prototipo/Campaign Management System/src/purchase-campaign-module.tsx" lines=25:109
@source flete title="Ingreso del flete al liquidar y pago por separado" path="prototipo/Campaign Management System/src/purchase-campaign-module.tsx" lines=119:145
@source adelantos title="Adelanto real, aplicación a carga y saldo de empresa" path="prototipo/Campaign Management System/src/transport-advances.ts" lines=6:89
@source cierre title="Ocho comprobaciones y protección de campaña finalizada" path="prototipo/Campaign Management System/src/campaign-lifecycle.ts" lines=28:102
@source cierre-vista title="Revisión y confirmación explícita del cierre" path="prototipo/Campaign Management System/src/campaign-closure.tsx" lines=19:46
@source sincronizacion title="Modo local y modo de información compartida" path="prototipo/Campaign Management System/src/shared-provider.tsx" lines=6:18
@source motor title="Cola, almacenamiento local y consulta al servidor" path="prototipo/Campaign Management System/src/shared-engine.ts" lines=26:80
@source servidor title="Persistencia configurada y validaciones de servidor" path="prototipo/Campaign Management System/api/shared-state.ts" lines=1:55

## ¿Cómo leer este mapa? {#lectura}

La finalidad empresarial es una interpretación de las vistas: abastecer pedidos de fruta y mantener trazabilidad desde la finca hasta la cobranza. Los pasos y bloqueos descritos se sustentan en el código del prototipo.

@facts
| Base de análisis | `docs/prototipo/Campaign Management System/` |
| Recorridos | Administrador: ocho módulos. Chofer: campañas y cargas asignadas. |
| Lectura recomendada | Flujo general → módulo de interés → reglas de cierre y diferencias de peso. |
| Evidencia | Las referencias indican archivos y líneas revisados del prototipo local. |
| Límite | No certifica el comportamiento actual de `epe-web`, `epe-backend` ni de un entorno desplegado. |

@callout level=note title="Qué representa una flecha"
| Una flecha muestra qué resultado permite continuar. Los catálogos y la planificación pueden prepararse en paralelo. |
| Los pasos visuales de cada módulo explican su flujo interno; los diagramas ampliables muestran las conexiones principales. |

Ir a [Comercial](block:modulo-comercial), [Campaña](block:modulo-campana), [Proveedores](block:modulo-proveedores), [Transporte](block:modulo-transporte), [Exportación](block:modulo-exportacion) o [Industria](block:modulo-industria).

Continuar con [Chofer](block:modulo-chofer), [Logística](block:modulo-logistica), [Facturación](block:modulo-ventas), [Liquidación](block:modulo-compras) o [Cierre de campaña](block:cierre-campana).

## ¿Cuál es el recorrido completo del negocio? {#recorrido-general}

@diagram workflow id=flujo-general source=flujo-general.workflow.json

@steps id=pasos-generales
| sg-campana | Crear campaña | Define fruta, temporada, fechas y responsable. Los padrones aportan clientes, proveedores, fincas y transporte. | flujo-general | campana |
| sg-venta | Acordar venta | Vincula al cliente, registra contratos y divide los kilos acordados en entregas programadas. | flujo-general | demanda |
| sg-coordinar | Coordinar entrega | Asigna empresa, vehículo, chofer, proveedores, fincas, origen, destino y fechas del viaje. | flujo-general | coordinar |
| sg-cargar | Calidad y carga | Aplica los controles del canal y registra kilos y bultos reales de cada proveedor. Después prepara la guía. | flujo-general | cargar |
| sg-recibir | Viaje y recepción | El chofer informa el despacho; se registran peso en planta, descarte, descarga y documentos. | flujo-general | recibir |
| sg-vender | Facturar y cobrar | Prepara la venta con la recepción documentada y registra la factura emitida fuera del prototipo. Luego registra cobros. | flujo-general | vender |
| sg-comprar | Liquidar y pagar | Liquida a cada proveedor por su carga y al transportista por el flete. Los pagos se registran por separado. | flujo-general | comprar |
| sg-cerrar | Finalizar campaña | Revisa pendientes operativos y financieros antes de confirmar el cierre con motivo. | flujo-general | finalizar |

@callout level=note title="La compra puede avanzar antes que la venta"
| El prototipo permite liquidar al proveedor desde una carga identificada con kilos y precio válidos. La recepción documentada habilita la preparación de la venta. Los dos caminos deben conciliarse para cerrar la campaña.[](source:origenes) |

## ¿Quién usa cada vista y para qué? {#actores}

| Actor o área | Qué hace en la aplicación | Qué entrega al siguiente participante |
| --- | --- | --- |
| Administrador | Entra al lanzador y accede a los ocho módulos. | Coordinación de campaña, datos maestros y seguimiento integral. |
| Área comercial — responsabilidad inferida | Registra clientes, requerimientos, contratos y entregas. | Cantidades, precio de venta, destino y fechas comprometidas. |
| Compras y campo — responsabilidad inferida | Vincula proveedores, fincas, entrevistas, exámenes y precio de compra. | Origen identificable, disponibilidad y condiciones de abastecimiento. |
| Calidad y cosecha — responsabilidad inferida | Revisa análisis, carga, cosecha y guías según el canal. | Kilos y bultos reales asociados a cada proveedor y entrega. |
| Chofer | Consulta sus asignaciones, llena carga y confirma etapas del despacho. | Historial del viaje, peso informado en planta y descarte. |
| Logística y finanzas — responsabilidades inferidas | Completan recepción y cierres; registran facturas, liquidaciones y movimientos. | Respaldo documental, saldos y condiciones para finalizar. |

Los perfiles de entrada observados son Administrador y Chofer. Las áreas anteriores explican responsabilidades del negocio; no representan roles adicionales implementados.[](source:acceso)[](source:chofer)

## 01 · Gestión Comercial: ¿cómo se convierte un pedido en entregas? {#modulo-comercial}

Su propósito es fijar qué necesita el cliente y convertir esa demanda en compromisos que la operación pueda ejecutar.[](source:comercial)[](source:contratos)

@steps id=flujo-comercial
| mc-cliente | Clientes | Busca, registra o edita la empresa y su contacto. Abre su ficha para consultar sus campañas. |
| mc-participacion | Participación en campaña | Elige campaña, variedades, kilos solicitados, ficha técnica, destino y ventana de entrega. |
| mc-contrato | Contratos | Adjunta el contrato y registra kilos, moneda, condiciones y precio de venta por kilogramo. |
| mc-programa | Entregas programadas | Divide cada contrato en viajes con fecha, kilos y destino. Puede distribuir kilos por variedad. |
| mc-ejecucion | Entregas en campaña | Continúa en Gestión de Campaña cuando esté En Proceso y completa quién transporta y de qué fincas sale la fruta. |

| Vista o formulario | Entrada principal | Resultado y condición para avanzar |
| --- | --- | --- |
| Clientes / Contratos | Padrón de clientes y campañas. | Permite localizar la relación comercial y sus documentos. |
| Participación comercial | Cliente y campaña existentes. | El prototipo abre la participación existente si ya está registrada para ese cliente y campaña. |
| Registrar contrato | Archivo y cantidad positiva. | Guarda el acuerdo; el precio puede quedar pendiente y bloqueará la preparación de la venta. |
| Programar entrega | Contrato con kilos acordados. | Registra fecha, cantidad y destino; valida el reparto frente al contrato. |
| Entrega con carga | Carga ya registrada. | Se consulta su detalle; la programación deja de editarse desde ese formulario. |

La programación comercial define el compromiso. La coordinación operativa añade los recursos que lo harán posible.[](source:entregas)

## 02 · Gestión de Campaña: ¿qué une toda la operación? {#modulo-campana}

La campaña es el contenedor de una temporada de trabajo. Reúne oferta, demanda, certificaciones, entregas, transporte y resultados.[](source:campanas)

@steps id=flujo-campana
| mp-registro | Datos generales | Registra nombre, temporada, frutas, fechas, responsable, requerimiento comercial y lineamientos. |
| mp-oferta | Proveedores | Vincula Productor o Acopiador, estima kilos y registra el precio de compra, evaluación y fincas pertinentes. |
| mp-revision | Exámenes y entrevista | Consulta resultados y documentos; para productores registra entrevista y datos agronómicos de finca en campaña. |
| mp-certificar | Certificaciones | Registra la certificación, sus fechas, costo, documento, ampliaciones y pagos asociados. |
| mp-demanda | Clientes y programa semanal | Consulta acuerdos y programación; agrupa las entregas para planificar el abastecimiento. |
| mp-recursos | Transportistas y Entregas | En campaña En Proceso vincula transportistas, acuerda el pago y completa los recursos de cada entrega. |
| mp-final | Revisión de cierre | Reúne los pendientes y exige confirmación con motivo antes de dejar el historial en consulta. |

| Estado o vista | Cómo funciona | Finalidad |
| --- | --- | --- |
| Planificado | Se preparan datos, proveedores, certificaciones, clientes y programa semanal. | Alinear la oferta de fruta con lo que se venderá. |
| En Proceso | Se deriva de la fecha de inicio, usando la fecha de Lima, si la campaña no está Finalizado. | Habilitar coordinación y ejecución operativa. |
| Datos generales | Muestra resumen e indicadores de campaña y acceso a revisar el cierre. | Detectar diferencias y pendientes entre módulos. |
| Finalizado | El cierre es explícito y el historial operativo y financiero queda protegido. | Conservar la trazabilidad de lo ejecutado y conciliado. |

La fecha prevista de fin no finaliza automáticamente la campaña. El inicio sí influye en el estado calculado por el prototipo.[](source:fechas)[](source:cierre-vista)

## 03 · Gestión de Proveedores: ¿cómo se identifica el origen de la fruta? {#modulo-proveedores}

Este módulo mantiene el padrón que las campañas reutilizan. Una finca identifica un origen físico; sus datos agronómicos pueden variar entre campañas.[](source:proveedores)[](source:fincas)

@steps id=flujo-proveedores
| pp-padron | Proveedor | Registra o consulta identidad, contacto, ubicación y personas vinculadas. |
| pp-finca | Fincas | Crea o edita nombre, códigos, ubicación, coordenadas, hectáreas, fruta y variedad del predio. |
| pp-certificado | Certificados | Adjunta certificados del proveedor con su fecha de revisión. |
| pp-vincular | Participación en campaña | Desde Gestión de Campaña vincula al proveedor, sus condiciones de compra y su evaluación. |
| pp-entrevista | Entrevista de finca | Reutiliza una finca o registra otra; guarda datos agronómicos en el contexto de la campaña. |
| pp-origen | Origen de una entrega | Selecciona proveedor y fincas al coordinar; esos vínculos acompañan carga, guías y liquidación. |

| Información | Dónde se mantiene | Para qué se reutiliza |
| --- | --- | --- |
| Identidad, contacto y personas vinculadas | Ficha general del proveedor. | Identificar al participante y a la persona seleccionada en la liquidación. |
| Ubicación y características de finca | Padrón de fincas del proveedor. | Reconocer el punto de recojo y el origen de fruta. |
| Riego, densidad y aplicaciones | Finca y campaña, mediante datos agronómicos. | Conservar el contexto de la entrevista de esa temporada. |
| Exámenes, estimado y precio de compra | Participación en campaña. | Evaluar al proveedor y disponer del precio usado en la liquidación. |
| Certificado del proveedor | Certificados de su ficha. | Respaldar su documentación; es distinto de una certificación gestionada por campaña. |

La entrevista de campaña se ofrece al Productor. El listado de participación también contempla Acopiador.[](source:participacion)[](source:padron-fincas)[](source:certificaciones)

## 04 · Gestión de Transporte: ¿cómo se pasa del padrón al viaje asignado? {#modulo-transporte}

Mantiene la oferta de transporte y permite comparar cotizaciones. La asignación final del viaje se concreta al coordinar la entrega en la campaña.[](source:transporte)[](source:entregas)

@steps id=flujo-transporte
| mt-empresa | Transportistas | Registra empresas o independientes y sus datos de contacto e identificación. |
| mt-recursos | Vehículos y Choferes | Asocia camiones y conductores con su empresa. Estos recursos se seleccionan en la entrega. |
| mt-solicitud | Requerimientos y cotizaciones | Selecciona transportistas y registra una solicitud para la campaña. |
| mt-comparar | Cotizaciones y selección | Registra respuestas, compara sus condiciones y deja indicada la selección. |
| mt-acuerdo | Acuerdo de pago | En Campaña → Transportistas define total contratado, modalidad, adelanto acordado y fecha. |
| mt-asignacion | Coordinación de entrega | En Campaña → Entregas asigna empresa, camión, chofer, origen y periodo del viaje. |
| mt-flete | Flete de cada carga | El importe se ingresa al liquidar el transporte de esa carga; luego se registran pagos o aplicaciones de adelanto. |

| Vista | Qué resuelve | Qué requiere después |
| --- | --- | --- |
| Transportistas | Padrón y selección para solicitudes. | Vehículos y choferes válidos de la empresa. |
| Vehículos / Choferes | Disponibilidad de recursos identificados. | Vincularlos a una entrega de la campaña. |
| Requerimiento / Cotizaciones / Selección | Comparación de ofertas. | Completar acuerdo y coordinación del viaje. |
| Acuerdo de pago en campaña | Presupuesto y condiciones de la empresa. | Registrar por separado un adelanto efectivamente entregado, si corresponde. |
| Liquidar transportista | Flete y gastos de una carga concreta. | Registrar el pago o aplicar un adelanto disponible. |

@callout level=note title="Solicitud y dinero tienen efectos distintos"
| El envío de solicitudes de cotización es simulado: el prototipo informa que no envió correos reales. Acordar un adelanto tampoco registra un desembolso.[](source:transporte)[](source:adelantos) |

## 05A · Cosecha y Control de Calidad: ¿cómo funciona Exportación? {#modulo-exportacion}

La navegación vigente parte de la campaña y ofrece Análisis y revisión, Cargas por entrega y Guías de remisión. La operación de una carga también contempla preparación, avances y cierre de cosecha.[](source:calidad)[](source:cosecha)

@diagram workflow id=flujo-exportacion source=flujo-exportacion.workflow.json

@callout level=note title="Cosecha y carga se contrastan durante el proceso"
| El registro de la carga puede capturarse antes del cierre de cosecha. Al cerrar o preparar la guía se contrasta la carga con los avances; el diagrama muestra el recorrido completo de cosecha.[](source:cosecha) |

@steps id=detalle-exportacion
| ex-revisar | Análisis y MTD | Por productor y finca registra muestreo, resultado y documento. Debe existir un análisis de madurez o materia seca y otro de distinto tipo. | flujo-exportacion | analisis |
| ex-apta | ¿Revisión completa? | El MTD debe tener valor válido, captura y ser como máximo 0.5; un valor mayor bloquea la cosecha. Es una regla del prototipo. | flujo-exportacion | apta |
| ex-preparar | Preparar cosecha | Vincula la entrega y registra responsable de cuadrilla, transporte, cuadrilla, llegada y capacitación confirmados. | flujo-exportacion | preparar |
| ex-avances | Registrar avances | Registra productor, finca, fecha, kilos cosechados, jabas, responsable y evidencia. | flujo-exportacion | registrar |
| ex-conciliar | Conciliar carga | Los kilos totales y por proveedor de la carga deben coincidir con los avances para cerrar y preparar la guía. | flujo-exportacion | datos-carga |
| ex-cerrar | Cerrar cosecha | Exige revisión, organización, avances, fecha de término, informe final y confirmación de cosecha completada. | flujo-exportacion | cerrar-cosecha |
| ex-guia | Preparar guía | Reutiliza la entrega, transporte, kilos y bultos. La revisión de análisis y MTD debe seguir vigente. | flujo-exportacion | guia |

Una carga rechazada no habilita cosecha ni generación de guía. Los recibos y solicitudes de personal o movilidad son respaldo documental del flujo.[](source:exportacion)[](source:cosecha)

## 05B · Cosecha y Control de Calidad: ¿qué cambia en Industria? {#modulo-industria}

Industria usa Cargas por entrega y Guías de remisión. La decisión de conformidad se toma sobre cada entrega; no recorre los análisis de Exportación.[](source:calidad)[](source:industria)

@steps id=flujo-industria
| in-campana | Seleccionar campaña | Abre Industria y elige una campaña disponible. Para registrar cargas debe estar En Proceso. |
| in-entrega | Seleccionar entrega coordinada | Reutiliza contrato, cliente, empresa, camión, chofer, proveedores y fincas ya asignados. |
| in-calidad | Evaluar conformidad | Si No cumple, guarda el rechazo para esa entrega y detiene su carga normal. Si cumple, continúa con el registro. |
| in-carga | Registrar carga | Por proveedor registra variedad, kilos y bultos cargados y vacíos. Incluye fecha, responsable, gastos y viáticos. |
| in-validar | Validar cantidades | Requiere kilos positivos, bultos enteros y una entrega sin otra carga registrada. Los kilos no pueden superar lo programado. |
| in-guia | Guías de remisión | Completa y genera las guías usando los datos reales de la carga y el vínculo de la entrega. |
| in-logistica | Continuar el despacho | El viaje y la recepción conservan la misma identidad de carga. |

| Dato de carga | Por qué se captura | Qué vista lo reutiliza |
| --- | --- | --- |
| Proveedor, fincas y variedad | Identificar el origen y a quién corresponde cada cantidad. | Guías, recepción y liquidación de compra. |
| Kilos por proveedor | Evitar atribuir el peso total del camión a cada participante. | Liquidación individual de proveedor. |
| Jabas, bines o mallas | Describir los bultos y su distribución. | Guías y control de jabas. |
| Gastos y viáticos | Documentar cuadrilla, anotadores, movilidad e insumos según el formulario. | Inversión de carga y gastos de transporte. |
| Decisión de calidad | Distinguir carga conforme de entrega rechazada. | Listado de cargas e historial de rechazo. |

La entrega queda reservada incluso cuando su carga está pendiente o fue rechazada. El rechazo no se interpreta como permiso para duplicar el registro.[](source:lista-entrega)[](source:carga)

## 06A · Logística y Despacho: ¿qué hace el chofer en el móvil? {#modulo-chofer}

El chofer entra a sus campañas y cargas asignadas. Consulta cliente, recojo, destino y vehículo; puede abrir el mapa de las fincas y una ruta de recojo.[](source:chofer)[](source:mapa)

@diagram workflow id=flujo-chofer source=flujo-chofer.workflow.json

@steps id=detalle-chofer
| ch-elegir | Elegir carga | Solo aparecen entregas vinculadas con su empresa y su identidad de chofer. | flujo-chofer | mis-cargas |
| ch-cargar | En carga | Llena o edita datos de carga cuando la coordinación está completa y la carga sigue habilitada. | flujo-chofer | en-carga |
| ch-salir | Salida | Confirma salida de la finca; el sistema registra una etapa del historial. | flujo-chofer | salida |
| ch-camino | En camino | Confirma el avance del viaje desde el móvil. | flujo-chofer | camino |
| ch-llegar | Llegada | Confirma llegada y habilita la captura del checklist de recepción. | flujo-chofer | llegada |
| ch-check | ¿Checklist completo? | Debe confirmar recepción con peso válido y descarte informado. Con descarte positivo se exige evidencia. | flujo-chofer | checklist |
| ch-final | Cierre | Finaliza su despacho cuando el checklist lo permite. No equivale al cierre administrativo de la recepción. | flujo-chofer | cierre-chofer |

La edición de carga se bloquea si ya tiene guía generada, avanzó del estado En carga, fue rechazada o su campaña dejó de estar En Proceso.[](source:chofer)

@callout level=note title="Seguimiento manual y documentos posteriores"
| Los estados se confirman con botones; el mapa no demuestra rastreo continuo del camión. El cierre del chofer comprueba recepción y descarte. La guía de salida puede adjuntarse en Llegada o Cierre.[](source:chofer)[](source:checklist-chofer) |

## 06B · Logística y Despacho: ¿cómo completa el administrador la recepción? {#modulo-logistica}

La vista administrativa consolida la carga y el historial del chofer. Completa los datos de planta y los respaldos necesarios para los cierres de la entrega.[](source:logistica)[](source:recepcion)

@steps id=flujo-logistica
| lg-seleccionar | Seleccionar entrega | Localiza la campaña y carga; consulta empresa, chofer, vehículo y estado informado del despacho. |
| lg-compras | Compras de la carga | Revisa el desglose de proveedores, cantidades, documentos y estado de verificación. |
| lg-recepcion | Recepción y calidad | Registra o completa peso en planta, resultado, informe de recepción, descarga y descarte. |
| lg-jabas | Jabas y salida | Concilia jabas entregadas y devueltas, constancia, pendientes y salida del vehículo. |
| lg-documentos | Documentos y cierre | Adjunta o consulta guía de fruta, detalle de compras, recepción, descarte, jabas y guía de salida firmada. |
| lg-fisico | Cierre físico | Valida peso positivo, resultado y respaldo de recepción, guía de fruta e inicio y término válidos de descarga. |
| lg-admin | Cierre administrativo | Exige el cierre físico y la guía de salida firmada. Conserva la entrega como parte del historial de campaña. |

| Cierre o comprobación | Qué comprueba realmente el prototipo | Qué significa |
| --- | --- | --- |
| Checklist del chofer | Confirmación de recepción y de descarte, con sus validaciones. | El chofer puede terminar su despacho. |
| Cierre físico | Peso, resultado, respaldo, guía de fruta y descarga válida. | La recepción tiene sus requisitos físicos registrados. |
| Cierre administrativo | Requisitos físicos, cierre físico previo y guía de salida firmada. | La entrega completa el cierre administrativo. |
| Lista visual de documentos | También muestra llegada, compras, jabas y respaldos. | Ayuda a revisar pendientes; los bloqueos efectivos se describen en las filas anteriores. |

Cerrar una entrega no finaliza la campaña ni registra pagos o cobros. La factura tampoco sustituye un informe de recepción que falta.[](source:reglas-recepcion)[](source:recepcion)[](source:cierre-vista)

## 07 · Facturación y cobros: ¿cómo se convierte la recepción en una cuenta cobrada? {#modulo-ventas}

El recorrido es Campaña → Cliente → Carga → Preparación de factura → Factura registrada → Cobros. Una carga puede aparecer antes de estar lista para facturar.[](source:ventas)

@diagram workflow id=flujo-financiero source=flujo-financiero.workflow.json

@steps id=detalle-ventas
| vt-origen | ¿Origen completo? | Requiere contrato y entrega identificados, precio, carga, guía y recepción con peso, resultado y respaldo. | flujo-financiero | valida-venta |
| vt-preparar | Preparar factura | Usa el peso recibido y el precio del contrato. Genera la referencia interna LV y deja pendiente la factura emitida. | flujo-financiero | preparar-venta |
| vt-emitir | Emitir fuera | La emisión y validación ante SUNAT se realizan fuera del prototipo. | flujo-financiero | emitir-fuera |
| vt-registrar | Registrar factura | Registra número, fecha y documento de la factura emitida; confirma que verificó sus datos. | flujo-financiero | factura-real |
| vt-cobrar | Registrar cobro | Añade fecha, monto, medio y respaldo. Solo se habilita con factura registrada y fecha coherente. | flujo-financiero | cobrar |
| vt-saldo | Conciliar saldo | Consulta historial y compara el total del documento con los cobros registrados. | flujo-financiero | saldar |

| Vista | Qué muestra o permite | Bloqueo relevante |
| --- | --- | --- |
| Campañas | Campañas elegibles y cantidad de cargas. | Debe existir la operación de origen. |
| Clientes de campaña | Contratos, cargas, total facturado, cobrado y saldo. | Los importes se presentan por moneda. |
| Detalle de carga | Peso cargado, recibido, preparación, factura y progreso de cobro. | Si falta un dato, dirige a completarlo en el módulo responsable. |
| Registrar factura emitida | Número, fecha, vencimiento, documento y confirmación de revisión. | Una preparación LV no cuenta como factura emitida. |
| Historial de cobros | Abonos y saldo del documento. | No se cobra antes de registrar la factura ni con fecha anterior a su emisión. |

Las nuevas ventas del prototipo preparan todo el peso recibido de un viaje en un documento. Los documentos históricos conservan sus cantidades y movimientos.[](source:validacion-compra)[](source:emision)

## 08 · Liquidación de Compra: ¿cómo se calcula y paga a proveedores y transporte? {#modulo-compras}

El recorrido es Campaña → Carga → Proveedor o Transportista → Liquidación → Pago. Guardar el documento deja una obligación pendiente; registrar dinero es otra acción.[](source:compras)[](source:flete)

@steps id=flujo-compra-proveedor
| cp-carga | Seleccionar proveedor de la carga | Abre campaña y carga; cada proveedor conserva su desglose de kilos y precio acordado. |
| cp-pendiente | Completar pendientes | Resuelve kilos faltantes, precio de compra, vínculo del origen o documentos históricos sin desglose seguro. |
| cp-liquidar | Liquidar proveedor | Usa los kilos cosechados y cargados de ese proveedor por el precio de compra de campaña. El prototipo exige PEN. |
| cp-persona | Persona de la liquidación | Selecciona la identidad correspondiente y revisa el control UIT ofrecido por el prototipo. |
| cp-documento | Guardar liquidación | Registra el documento LC; no genera un pago automático. |
| cp-pagar | Registrar pago | Desde Por pagar registra pago total o abono con fecha, monto, medio y respaldo según corresponda. |
| cp-conciliar | Pagado e historial | La vista Pagados permite consultar liquidaciones saldadas y sus movimientos. |

@steps id=flujo-compra-transporte
| ct-acuerdo | Revisar acuerdo de empresa | El total contratado y sus condiciones vienen de Gestión de Campaña → Transportistas. |
| ct-adelanto | Registrar adelanto real | Si existe modalidad de adelanto, registra el desembolso efectivo. El importe acordado por sí solo no crea saldo utilizable. |
| ct-carga | Liquidar transportista por carga | Ingresa el flete y los gastos. Sin detalle manual, la función usa movilidad e insumos de la carga como gastos automáticos. |
| ct-documento | Guardar liquidación LT | Crea el documento pendiente; no aplica adelantos ni registra pagos al guardar. |
| ct-aplicar | Aplicar adelanto | En una acción separada asigna dinero ya entregado a una carga; no es un nuevo desembolso. |
| ct-pagar | Registrar pago posterior | Registra un pago o abono por el saldo pendiente de la carga y revisa el saldo de la empresa en campaña. |
| ct-conciliar | Conciliar empresa y cargas | Revisa flete pendiente de liquidar, adelanto disponible, pagos y saldo final. |

| Concepto | Base observada en el prototipo | Interpretación |
| --- | --- | --- |
| Compra a proveedor | Kilos propios cargados × precio de compra de campaña. | No hereda el total del camión si hay varios proveedores. |
| Venta al cliente | Peso recibido en planta × precio de venta del contrato, con ajustes del documento si se registran. | La diferencia frente a lo cargado debe permanecer visible. |
| Liquidación de transporte | Flete de la carga + gastos reembolsables. | Flete, gastos y pagos son conceptos distintos. |
| Saldo de carga de transporte | Total de su liquidación − adelanto aplicado − pagos posteriores. | Una aplicación cubre saldo con dinero que ya se entregó. |
| Saldo de empresa | Flete autorizado + gastos liquidados − dinero efectivamente pagado. | Las aplicaciones de adelanto se excluyen del dinero nuevo. |

@callout level=warning title="Alcance del control UIT y de los pagos"
| El control UIT es una ayuda interna del prototipo y depende de las identidades, importes y conversiones que tenga registrados. Esta página no valida obligaciones tributarias. |
| Los formularios registran movimientos y comprobantes; no se observa una integración bancaria que transfiera dinero. |

Los documentos con movimientos conservan su historial y no se editan libremente. Los cálculos de adelanto evitan aplicarlo dos veces o superar el saldo de la carga.[](source:validacion-compra)[](source:adelantos)

## ¿Cuándo puede finalizar una campaña? {#cierre-campana}

La operación termina cuando se completan los cierres físicos y se concilian las obligaciones. Desde Datos generales se revisan los pendientes y se confirma el cierre con un motivo de al menos diez caracteres.[](source:cierre)[](source:cierre-vista)

| Comprobación de cierre | Qué debe estar resuelto | Dónde completar pendientes |
| --- | --- | --- |
| Contratos y viajes | Kilos contratados programados y entregas con recepción cerrada. | Comercial → Contratos / Entregas; Campaña → Entregas. |
| Despachos del chofer | Todos los servicios alcanzan el estado Cierre. | Vista móvil del chofer. |
| Recepciones y documentación | Una recepción por carga, peso, resultado, reporte, guía, descarga y cierres físico y administrativo. | Logística y Despacho. |
| Operaciones de cosecha | Las operaciones activas tienen recepción cerrada; Exportación también tiene cierre de cosecha. | Calidad / Cosecha y Logística. |
| Facturas por viaje | Recepciones cubiertas por sus documentos y facturas realmente registradas. | Facturación y cobros. |
| Compras y transporte | Cada carga tiene la liquidación del transportista y la de cada proveedor participante. | Liquidación de Compra. |
| Cobros | Facturas sin diferencias entre total y cobros registrados. | Historial de cobros de cada factura. |
| Pagos y certificaciones | Pagos, certificaciones, fletes y adelantos conciliados; sin obligaciones pendientes. | Liquidación de Compra y Certificaciones de campaña. |

@steps id=flujo-cierre
| cc-revisar | Revisar cierre de campaña | Abre la lista derivada de pendientes desde Datos generales. |
| cc-resolver | Resolver en el origen | Completa operaciones, documentos o movimientos en sus módulos. Guarda esos cambios antes de pedir el cierre. |
| cc-motivo | Registrar motivo | Explica cómo concluyó la campaña con al menos diez caracteres. |
| cc-confirmar | Confirmar cierre | El servidor vuelve a validar los pendientes; registra fecha y motivo si el cierre procede. |
| cc-historial | Consultar historial finalizado | Conserva datos y movimientos. El cierre no inventa pesos ni pone saldos a cero. |

## ¿Cómo se comunican las vistas y qué depende del entorno? {#datos-compartidos}

Las pantallas reutilizan los mismos registros mediante el almacén de la aplicación. Un cambio de carga o despacho aparece en otros módulos a través de ese estado común.[](source:sincronizacion)[](source:motor)

@steps id=flujo-datos
| dt-accion | Acción en una vista | El usuario guarda un proveedor, carga, documento o movimiento. La interfaz aplica las validaciones correspondientes. |
| dt-estado | Estado compartido de la aplicación | Los módulos leen las colecciones comunes y sus vínculos; no crean otra carga por mostrarla en una pestaña distinta. |
| dt-entorno | Persistencia según el modo | En desarrollo se usa modo local con almacenamiento del navegador. En modo compartido se consulta la API y se envían cambios al servidor. |
| dt-validar | Validación y conservación | La API valida integridad, origen financiero, permisos de chofer y condiciones de cierre antes de conservar los cambios. |
| dt-refrescar | Actualización de otras vistas | El motor recupera el estado compartido y mantiene una cola de cambios pendientes en el navegador. |

| Capacidad | Evidencia del prototipo | Cómo interpretar la página |
| --- | --- | --- |
| Almacenamiento compartido | La API selecciona Supabase cuando está configurado; en la otra rama usa Vercel Blob. | No se afirma qué proveedor está activo en un despliegue concreto. |
| Entrada de demostración | Selección de perfil sin contraseña; existe generación de enlace privado de chofer en modo compartido. | No describe el acceso de la aplicación definitiva. |
| Facturación electrónica | Registro de un comprobante ya emitido externamente. | No implica emisión o validación automática ante SUNAT. |
| Cotizaciones | El envío se informa como simulado. | No implica correo real al transportista. |
| Mapa de finca | Usa coordenadas de finca y permite elegir un punto de origen para la ruta. | No implica GPS continuo ni evidencia de la posición real del camión. |

La API compartida y su persistencia se describen a partir de sus ramas de código, sin consultar infraestructura ni modificar datos del prototipo.[](source:servidor)

## ¿Qué conviene distinguir para entender el sistema sin confusiones? {#distinciones}

| Conceptos que se parecen | Diferencia funcional |
| --- | --- |
| Requerimiento y contrato | El requerimiento expresa la demanda del cliente; el contrato fija una cantidad y sus condiciones comerciales. |
| Entrega programada y carga | La entrega define un compromiso; la carga registra fruta y bultos reales con sus proveedores. |
| Campaña y entrega | Una campaña contiene múltiples compromisos y cargas. Cerrar una entrega no finaliza toda la campaña. |
| Padrón y participación | El padrón conserva datos reutilizables; la participación añade evaluación, estimado y condiciones de esa campaña. |
| Finca y entrevista | La finca identifica el predio; la entrevista incorpora el contexto agronómico de una campaña. |
| Peso cargado y recibido | Son mediciones distintas. En este prototipo alimentan la compra y la venta, respectivamente. |
| Preparación LV y factura emitida | La primera prepara la venta; la segunda registra el comprobante externo y habilita cobros. |
| Liquidación y pago | La liquidación calcula y documenta una obligación; el pago registra que se entregó dinero. |
| Adelanto acordado, pagado y aplicado | Son condición del acuerdo, desembolso real y asignación a una carga, respectivamente. |
| Cierre del chofer, recepción y campaña | Son hitos diferentes, con sus propias validaciones. |

@callout level=note title="Fidelidad al prototipo y supuestos"
| La finalidad empresarial y la distribución de responsabilidades entre áreas son inferencias explicativas autorizadas por la solicitud. Los perfiles y nombres de vistas proceden del código. |
| Se siguieron los componentes conectados al menú vigente. Hay funciones heredadas y un componente Pagos que no figura entre las ocho opciones del lanzador. No se presenta como un noveno módulo disponible.[](source:app) |
| Las reglas aquí descritas corresponden al prototipo local. Otros documentos de diseño pueden proponer distintas cantidades, cardinalidades o bases de liquidación. |

## Ejemplo de lectura: ¿qué ocurre con un pedido de fruta? {#ejemplo}

El ejemplo es narrativo y no representa una operación real. No necesita cantidades para mostrar las dependencias.

@steps id=caso-pedido
| ej-demanda | El cliente pide fruta | Comercial registra el requerimiento, adjunta el contrato y programa una entrega. |
| ej-abasto | Se identifica el abastecimiento | Campaña vincula proveedores y fincas y registra el precio de compra. Transporte aporta empresa, camión y chofer. |
| ej-coordina | Se completa la entrega | La campaña En Proceso conecta esos recursos con el compromiso comercial. |
| ej-control | Se revisa la fruta | Exportación exige sus análisis y MTD; Industria registra conformidad de la entrega. |
| ej-carga | Se registra la carga real | Kilos, variedad y bultos quedan desglosados por proveedor. Se preparan sus guías. |
| ej-viaje | El chofer completa el despacho | Informa salida, trayecto y llegada; registra recepción y descarte antes de cerrar. |
| ej-planta | Se completa la recepción | Logística verifica peso y documentos, registra descarga y completa los cierres de la entrega. |
| ej-finanzas | Se concilian ambas partes | Se paga la compra y el transporte; se registra la factura al cliente y sus cobros. |
| ej-cierre | Se finaliza la campaña | El administrador confirma que no queden pendientes y conserva el historial cerrado. |
