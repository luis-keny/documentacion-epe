# Auditoría aplicada al esquema agroexportador

**Decisiones incorporadas al SQL objetivo — 29/10/2026.**

> **Trazabilidad del modelo, no estado de implementación.** Revisar para retiro o renovación el **27/01/2027**; las decisiones y el estado backend vigentes están en sus índices actuales.

Se revisaron 46 propuestas originales: cinco se retiraron o consolidaron y quedan **41 propuestas vigentes**, junto a 19 tablas actuales: **60 tablas y 124 FK**. Se conserva norma con datos iniciales y guia_x_norma para selecciones reales. Estos cambios están incorporados al SQL y los HTML de revisión; no se ha modificado una base desplegada ni la aplicación.

[Revisar HTML por vistas](diagramas/esquema-agro-vistas.html#auditoria) · [SQL total](03_schema_total.sql) · [Datos iniciales reejecutables](04_datos_iniciales.sql) · [Evidencias JSON](auditoria-tablas-propuestas.json)

## Simplificaciones y retiro de sesiones confirmado

| Tabla | Decisión aplicada |
|---|---|
| `sesion_usuario` | Retirada del objetivo. No se conserva una cabecera/acuerdo/puente sin función independiente. |
| `campana_x_fruta_derivada` | Retirada del objetivo. No se conserva una cabecera/acuerdo/puente sin función independiente. |
| `participacion_proveedor_campana` | Consolidada en campania_x_proveedores. No se conserva una cabecera/acuerdo/puente sin función independiente. |
| `participacion_proveedor_x_fruta_derivada` | Retirada del objetivo. No se conserva una cabecera/acuerdo/puente sin función independiente. |
| `acuerdo_compra` | Retirada del objetivo. No se conserva una cabecera/acuerdo/puente sin función independiente. |
| `norma` | Conservada como catálogo relacionado, con cinco códigos iniciales SQL. |
| `guia_x_norma` | Conservada para las normas seleccionadas de cada guía; no recibe filas del seed. |

La participación única es campania_x_proveedores.cxp_id. Certificados y cargas ya la referencian; la FK compuesta conserva coherencia de campaña/proveedor. cantidad_proveedor, tipo_proveedor, estado, created_at, precio y observaciones mantienen la información equivalente sin duplicarla. El tipo de fruta sigue la regla del proveedor y las etapas se obtienen de examen/entrevista. No se añaden filas de variedades derivadas de la campaña; sí permanecen las selecciones reales de proveedor/cliente y distribución de kilos por variedad.

## Catálogos iniciales y opciones constantes

El SQL total ya carga dos perfiles, cinco normas, cinco frutas, 17 variedades y dos parámetros anuales tomados del prototipo. 04_datos_iniciales.sql permite repetir la carga sin duplicar registros ni sobrescribir configuración existente. Los importes UIT proceden del código y requieren revisión antes de operación; no se acredita vigencia normativa.

| Selector o parámetro | Persistencia | Decisión |
|---|---|---|
| Moneda | Campo moneda en cada transacción; no hay tabla moneda propuesta. | Opciones fijas por contexto. Compra y acuerdo de transporte: PEN según decisión vigente. Ventas/certificados conservan la moneda elegida entre las opciones permitidas. El prototipo aún ofrece otras monedas en transporte: alinear la UI y sus validaciones, sin cambiar solo la etiqueta de un importe. |
| Perfiles | rol o enum; usuario mantiene el perfil real. | Administrador y Chofer pueden ser seed. No se necesita CRUD de roles para este prototipo; la autorización sí debe comprobarse en backend. |
| Normas y tipos de certificado | Códigos/tipos validados y snapshots del documento. | norma permanece como tabla con cinco códigos iniciales. guia_x_norma guarda selecciones reales; tipo_certificacion es un campo validado con opciones fijas, independiente del catálogo de normas. Se conserva la frase emitida. |
| Frutas y variedades | fruta/fruta_derivada son tablas actuales; relaciones de selección cuando corresponda. | FRUIT_CATALOG puede alimentar seed de los catálogos existentes. No hardcodear IDs numéricos ni copiar todas las variedades a cada campaña. La UI multifruta contradice el acuerdo de una fruta por campaña. |
| UIT anual y umbral | Configuración por año y snapshot de los valores aplicados. | Puede mantenerse seed/configuración controlada sin CRUD. No es una constante eterna ni se completa un año ausente con cero. Esta auditoría observa código; no valida vigencia normativa de sus importes. |
| Tipos de examen, etapas y estados | Código/enum/CHECK; resultados e historial por operación. | Opciones fijas del prototipo sin una tabla de catálogo por selector. El estado inicial no sustituye un evento o resultado real. |
| Métodos de pago y conceptos de viático | Código/texto validado en el movimiento o gasto. | Listas fijas sin catálogos nuevos. Mantener importes, evidencias y aplicaciones: un concepto fijo no vuelve fijo al movimiento. |

## Cómo se guarda guia_x_norma

1. El selector consulta norma y presenta los códigos iniciales; no se necesita CRUD del catálogo.
2. Al guardar una guía en borrador, el servicio resuelve los códigos elegidos a norma_id y sincroniza solo sus filas de guia_x_norma en la misma transacción. UNIQUE (guia_remision_id, norma_id) impide duplicados.
3. Una selección vacía deja cero filas. No se asigna NOP ni todas las normas por defecto; un código desconocido se rechaza.
4. contenido.standardCodes refleja esa selección y standardText conserva el texto histórico. Al emitir se congela el documento; cambiar el catálogo después no reescribe sus frases.
5. El SQL aporta catálogo, FK y unicidad; la sincronización del formulario, los permisos y el bloqueo de guías emitidas corresponden al servicio aún por implementar.

## Alcance de la evidencia

Auditoría estática del código local, contrastada con las fichas V01–V62. No prueba ejecución ni persistencia normalizada del backend.

Las fichas Vxx identifican usos documentados, no CRUD independiente. La auditoría no ejecutó un nuevo recorrido manual de las 62 vistas. Los editores actuales de cotización y kilos por variedad justifican conservar sus tablas. disponibilidad text y tipo_certificacion guardan sus opciones/datos sin catálogos nuevos.

## Dictamen de las 41 propuestas vigentes

| Tabla | Interfaz | Dictamen |
|---|---|---|
| [`persona`](#persona) | Modal de personas vinculadas y selector de liquidación | Conservar por función visible |
| [`rol`](#rol) | Acceso por perfil; sin administración de roles | Conservar con seed/configuración |
| [`usuario`](#usuario) | Identidad de acceso; sin CRUD de cuentas de negocio | Conservar por función técnica |
| [`parametro_uit`](#parametro-uit) | Panel de consulta anual; valores en constantes del código | Conservar con seed/configuración |
| [`proveedor_x_persona`](#proveedor-x-persona) | Agregar persona vinculada, vínculo y selección para liquidar | Conservar por función visible |
| [`proveedor_x_fruta_derivada`](#proveedor-x-fruta-derivada) | Formulario del proveedor con variedades | Conservar por función visible |
| [`norma`](#norma) | Selectores fijos de certificación y códigos de guía | Conservar con seed/configuración |
| [`certificado_campana_x_proveedor`](#certificado-campana-x-proveedor) | Selección de productores cubiertos en certificado | Conservar por función visible |
| [`ampliacion_certificado_campana`](#ampliacion-certificado-campana) | Modal de ampliación del certificado | Conservar por función visible |
| [`pago_certificado_campana`](#pago-certificado-campana) | Modal de pago del certificado | Conservar por función visible |
| [`cliente_negocio_campana_x_fruta_derivada`](#cliente-negocio-campana-x-fruta-derivada) | Selección múltiple de variedades del requerimiento | Conservar por función visible |
| [`contrato_venta`](#contrato-venta) | Formulario de contrato por requerimiento | Conservar por función visible |
| [`entrega_programada`](#entrega-programada) | Programación y edición de entrega | Conservar por función visible |
| [`entrega_x_fruta_derivada`](#entrega-x-fruta-derivada) | Campos Kilos por variedad cuando hay varias variedades | Conservar por función visible |
| [`solicitud_transporte`](#solicitud-transporte) | Modal de solicitud y detalle de respuestas | Conservar por función visible |
| [`invitacion_transporte`](#invitacion-transporte) | Empresas seleccionadas dentro de la solicitud | Conservar por función visible |
| [`cotizacion_transporte`](#cotizacion-transporte) | Modal Registrar respuesta / TransportQuoteModal | Conservar por función visible |
| [`acuerdo_transporte`](#acuerdo-transporte) | Modal de acuerdo, monto, adelanto y saldo | Conservar por función visible |
| [`coordinacion_entrega`](#coordinacion-entrega) | Coordinación de la entrega con transporte, chofer y ventana | Conservar por función visible |
| [`origen_entrega`](#origen-entrega) | Productores y fincas de recojo dentro de la entrega | Conservar por función visible |
| [`cosecha`](#cosecha) | Flujo de cosecha, organización, avances y cierre | Conservar por función visible |
| [`analisis_calidad`](#analisis-calidad) | Registrar/editar análisis por productor y finca | Conservar por función visible |
| [`medicion_mtd`](#medicion-mtd) | MTD dentro del análisis y resumen compartido por finca | Conservar por función visible |
| [`carga`](#carga) | Modal de registro de carga | Conservar por función visible |
| [`proveedor_carga`](#proveedor-carga) | Filas de proveedores con kilos y envases en carga | Conservar por función visible |
| [`origen_carga`](#origen-carga) | Procedencia de la carga y sus fincas | Conservar por función visible |
| [`gasto_carga`](#gasto-carga) | Gastos/cuadrilla dentro del registro de carga | Conservar por función visible |
| [`guia_remision`](#guia-remision) | Editor de guía, documento y datos de transporte/llegada | Conservar por función visible |
| [`proveedor_guia`](#proveedor-guia) | Detalle de productores dentro de la guía | Conservar por función visible |
| [`guia_x_norma`](#guia-x-norma) | Selección de códigos fijos y texto generado en la guía | Conservar por función visible |
| [`historial_chofer`](#historial-chofer) | Reportar etapa y consultar historial del despacho | Conservar por función visible |
| [`recepcion_planta`](#recepcion-planta) | Checklist del chofer y consulta logística | Conservar por función visible |
| [`liquidacion_proveedor`](#liquidacion-proveedor) | Formulario de liquidación de compra y selección de persona | Conservar por función visible |
| [`liquidacion_transporte`](#liquidacion-transporte) | Liquidación de transporte por carga | Conservar por función visible |
| [`gasto_transporte`](#gasto-transporte) | Viáticos de movilidad e insumos asociados a la carga | Conservar por función visible |
| [`adelanto_transporte`](#adelanto-transporte) | Modal Registrar adelanto entregado | Conservar por función visible |
| [`aplicacion_adelanto`](#aplicacion-adelanto) | Modal Aplicar adelanto a esta carga | Conservar por función visible |
| [`factura_venta`](#factura-venta) | Liquidación de venta, facturación y validación documental | Conservar por función visible |
| [`pago_proveedor`](#pago-proveedor) | Modal Registrar pago al proveedor | Conservar por función visible |
| [`pago_transporte`](#pago-transporte) | Modal Registrar pago al transportista | Conservar por función visible |
| [`cobro_venta`](#cobro-venta) | Formulario de cobro de venta | Conservar por función visible |

### persona

**Tabla:** `persona` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de personas vinculadas y selector de liquidación.

**Hallazgo:** Se crean identidades reales y se elige a quién corresponde liquidar.

**Decisión y persistencia:** Conservar persona y selección; no convertirlas en una persona genérica.

**Predeterminados y límites:** Tipo de documento puede iniciar en DNI; nombre, documento y persona elegida deben ser reales.

**Fichas:** Sin ficha específica.

**Fuentes:** [settlement-person-picker.tsx:24](../prototipo/Campaign%20Management%20System/src/settlement-person-picker.tsx#L24).

### rol

**Tabla:** `rol` · **Dictamen:** Conservar con seed/configuración

**Interfaz:** Acceso por perfil; sin administración de roles.

**Hallazgo:** Los perfiles Administrador y Chofer se cargan mediante SQL inicial; el catálogo permite más perfiles sin requerir CRUD ahora.

**Decisión y persistencia:** Mantener tabla rol y sus dos registros iniciales SQL; no crear pantalla de catálogo por ahora.

**Predeterminados y límites:** Resolver por código estable; nunca usar un rol administrador predeterminado para cualquier cuenta.

**Fichas:** Sin ficha específica.

**Fuentes:** [App.tsx:196](../prototipo/Campaign%20Management%20System/src/App.tsx#L196), [App.tsx:18](../prototipo/Campaign%20Management%20System/src/App.tsx#L18).

### usuario

**Tabla:** `usuario` · **Dictamen:** Conservar por función técnica

**Interfaz:** Identidad de acceso; sin CRUD de cuentas de negocio.

**Hallazgo:** La ausencia de una pantalla de usuarios no elimina la necesidad de identificar al actor de las operaciones.

**Decisión y persistencia:** Conservar si la autenticación del backend usa esta entidad; mapear identidad autenticada y responsable.

**Predeterminados y límites:** Responsable desde la sesión autenticada, no usuario_id=1 ni una cuenta demo compartida.

**Fichas:** Sin ficha específica.

**Fuentes:** [App.tsx:196](../prototipo/Campaign%20Management%20System/src/App.tsx#L196), [App.tsx:18](../prototipo/Campaign%20Management%20System/src/App.tsx#L18).

### parametro-uit

**Tabla:** `parametro_uit` · **Dictamen:** Conservar con seed/configuración

**Interfaz:** Panel de consulta anual; valores en constantes del código.

**Hallazgo:** Existe consulta por año y conversión de operaciones, pero no CRUD del parámetro anual.

**Decisión y persistencia:** Conservar como tabla con datos iniciales SQL de 2025/2026 y umbral, ampliable por año sin CRUD; preservar snapshots aplicados.

**Predeterminados y límites:** Seed por año conocido; umbral del prototipo 0.90. Año ausente debe requerir configuración, nunca asumir valor cero ni reutilizar otro año.

**Fichas:** Sin ficha específica.

**Fuentes:** [purchase-uit.ts:6](../prototipo/Campaign%20Management%20System/src/purchase-uit.ts#L6).

### proveedor-x-persona

**Tabla:** `proveedor_x_persona` · **Dictamen:** Conservar por función visible

**Interfaz:** Agregar persona vinculada, vínculo y selección para liquidar.

**Hallazgo:** La relación representa personas vinculadas al proveedor y su vínculo, no un catálogo sin función.

**Decisión y persistencia:** Conservar los vínculos registrados; el proveedor principal no necesita una vinculación ficticia consigo mismo.

**Predeterminados y límites:** Sin filas automáticas; registrar solo personas realmente vinculadas. No inventar documento ni parentesco.

**Fichas:** Sin ficha específica.

**Fuentes:** [settlement-person-picker.tsx:24](../prototipo/Campaign%20Management%20System/src/settlement-person-picker.tsx#L24).

### proveedor-x-fruta-derivada

**Tabla:** `proveedor_x_fruta_derivada` · **Dictamen:** Conservar por función visible

**Interfaz:** Formulario del proveedor con variedades.

**Hallazgo:** El proveedor declara variedades que comercializa; es una selección distinta de las variedades calculadas de una campaña.

**Decisión y persistencia:** Conservar selección múltiple y unicidad proveedor/variedad.

**Predeterminados y límites:** Lista vacía hasta elegir; no asignar todas las variedades del catálogo.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1137](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1137), [store.tsx:409](../prototipo/Campaign%20Management%20System/src/store.tsx#L409).

### norma

**Tabla:** `norma` · **Dictamen:** Conservar con seed/configuración

**Interfaz:** Selectores fijos de certificación y códigos de guía.

**Hallazgo:** No existe CRUD de normas. Los tipos de certificado y GUIDE_STANDARDS son listas de código; no son necesariamente la misma taxonomía.

**Decisión y persistencia:** Conservar norma con cinco códigos iniciales SQL y FK explícitas. tipo_certificacion guarda la opción fija del certificado por separado; norma_id solo si se elige una relación real.

**Predeterminados y límites:** Lista fija versionada; sin fila genérica ni norma por defecto. Certificados deben conservar el tipo elegido.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:693](../prototipo/Campaign%20Management%20System/src/modules.tsx#L693), [remission-model.ts:5](../prototipo/Campaign%20Management%20System/src/remission-model.ts#L5).

### certificado-campana-x-proveedor

**Tabla:** `certificado_campana_x_proveedor` · **Dictamen:** Conservar por función visible

**Interfaz:** Selección de productores cubiertos en certificado.

**Hallazgo:** La cobertura por productor es real aunque se edite desde el modal de certificación y no tenga CRUD propio.

**Decisión y persistencia:** Conservar cobertura y unicidad certificado/proveedor. La FK ya referencia cxp_id de campania_x_proveedores, incluida la coherencia compuesta de campaña/proveedor.

**Predeterminados y límites:** Kilos autorizados deben derivarse de la cobertura real y guardarse como snapshot; no dividir el total por igual ni asignar cero para llenar el campo.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:693](../prototipo/Campaign%20Management%20System/src/modules.tsx#L693).

### ampliacion-certificado-campana

**Tabla:** `ampliacion_certificado_campana` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de ampliación del certificado.

**Hallazgo:** Hay registro de kilos adicionales, fecha y observaciones; el historial no se sustituye por un único total.

**Decisión y persistencia:** Conservar una fila por ampliación confirmada.

**Predeterminados y límites:** Kilos y fecha confirmada no se inventan. Ninguna ampliación se crea al abrir el modal ni requiere un estado adicional no observado.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:753](../prototipo/Campaign%20Management%20System/src/modules.tsx#L753).

### pago-certificado-campana

**Tabla:** `pago_certificado_campana` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de pago del certificado.

**Hallazgo:** Los pagos y su comprobante tienen registro propio en la interfaz.

**Decisión y persistencia:** Conservar movimientos reales separados del monto del certificado.

**Predeterminados y límites:** Fecha puede precargarse para confirmar; monto y moneda elegidos deben conservarse. No crear pago cero ni pago automático al emitir certificado.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:737](../prototipo/Campaign%20Management%20System/src/modules.tsx#L737).

### cliente-negocio-campana-x-fruta-derivada

**Tabla:** `cliente_negocio_campana_x_fruta_derivada` · **Dictamen:** Conservar por función visible

**Interfaz:** Selección múltiple de variedades del requerimiento.

**Hallazgo:** El cliente selecciona variedades; aquí el puente representa datos elegidos y no un cálculo automático.

**Decisión y persistencia:** Conservar la relación de variedades requeridas sin CRUD de catálogo adicional.

**Predeterminados y límites:** No asignar todas las variedades por defecto; guardar las elegidas en el formulario.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1324](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1324).

### contrato-venta

**Tabla:** `contrato_venta` · **Dictamen:** Conservar por función visible

**Interfaz:** Formulario de contrato por requerimiento.

**Hallazgo:** Se crean contratos con precio, moneda y condiciones/documento.

**Decisión y persistencia:** Conservar contrato y snapshots de lo acordado.

**Predeterminados y límites:** Conservar el estado que guarda el contrato real; no añadir un ciclo de borrador no observado. Precio/moneda no se infieren del selector de filtro.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1467](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1467).

### entrega-programada

**Tabla:** `entrega_programada` · **Dictamen:** Conservar por función visible

**Interfaz:** Programación y edición de entrega.

**Hallazgo:** La entrega tiene cantidades, fecha, destino y coordinación propios.

**Decisión y persistencia:** Conservar; destino permanece texto obligatorio por D08 y no vuelve a ser catálogo.

**Predeterminados y límites:** El estado de entrega se obtiene del flujo, sin agregar otra columna por rutina. Fecha, kilos y destino son datos reales; no usar dirección ni fecha ficticias.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1516](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1516).

### entrega-x-fruta-derivada

**Tabla:** `entrega_x_fruta_derivada` · **Dictamen:** Conservar por función visible

**Interfaz:** Campos Kilos por variedad cuando hay varias variedades.

**Hallazgo:** El código actual permite distribuir kilos y valida la suma; existe una función visible de esta tabla.

**Decisión y persistencia:** Conservar filas para la distribución registrada. Este editor actual matiza la evidencia anterior del recorrido del 27/10.

**Predeterminados y límites:** Con una sola variedad puede derivarse el total; con varias no repartir por igual ni inventar cantidades si no se informó distribución.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1591](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1591).

### solicitud-transporte

**Tabla:** `solicitud_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de solicitud y detalle de respuestas.

**Hallazgo:** La solicitud tiene ventana, ruta, condiciones, kilos y transportistas seleccionados.

**Decisión y persistencia:** Conservar cabecera y datos de la convocatoria.

**Predeterminados y límites:** Inicio BORRADOR; la UI indica envío simulado. No registrar envío real por abrir o guardar el formulario.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1706](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1706).

### invitacion-transporte

**Tabla:** `invitacion_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Empresas seleccionadas dentro de la solicitud.

**Hallazgo:** Cada destinatario permite relacionar sus respuestas y la empresa seleccionada; no necesita CRUD separado.

**Decisión y persistencia:** Conservar una fila por empresa seleccionada y correo snapshot opcional. Aclarar que INVITADA es estado lógico mientras no haya integración de envío.

**Predeterminados y límites:** Correo desde empresa si existe; NULL si falta. No inventar correo ni marcar correo ENVIADO sin confirmación de envío.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1706](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1706), [modules.tsx:1735](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1735).

### cotizacion-transporte

**Tabla:** `cotizacion_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal Registrar respuesta / TransportQuoteModal.

**Hallazgo:** El prototipo actual sí tiene editor de empresa, monto, moneda, disponibilidad, condiciones y archivo.

**Decisión y persistencia:** Conservar. disponibilidad text ya conserva el campo del editor sin un catálogo adicional.

**Predeterminados y límites:** fecha puede capturarse al registrar si no hay fecha documental distinta. RECIBIDA al guardar respuesta real; monto y moneda son los de esa respuesta.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1735](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1735).

### acuerdo-transporte

**Tabla:** `acuerdo_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de acuerdo, monto, adelanto y saldo.

**Hallazgo:** El acuerdo aceptado tiene función distinta de la cotización recibida y de la solicitud.

**Decisión y persistencia:** Conservar confirmación y enlace con la empresa/campaña; fecha de acuerdo puede capturarse al confirmar.

**Predeterminados y límites:** BORRADOR antes de confirmar. PEN según acuerdo vigente; corregir los selectores del prototipo que aún ofrecen otras monedas. No cambiar solo el código de una cotización USD sin conversión acordada.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:279](../prototipo/Campaign%20Management%20System/src/modules.tsx#L279).

### coordinacion-entrega

**Tabla:** `coordinacion_entrega` · **Dictamen:** Conservar por función visible

**Interfaz:** Coordinación de la entrega con transporte, chofer y ventana.

**Hallazgo:** La coordinación identifica el viaje y las reservas, no una tabla adicional solo para una pantalla.

**Decisión y persistencia:** Conservar la coordinación; responsables y recursos provienen de las selecciones y asignaciones reales.

**Predeterminados y límites:** Sin transportista/chofer/vehículo ficticio por defecto; ventanas desde la coordinación confirmada.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1516](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1516).

### origen-entrega

**Tabla:** `origen_entrega` · **Dictamen:** Conservar por función visible

**Interfaz:** Productores y fincas de recojo dentro de la entrega.

**Hallazgo:** Una entrega puede reunir varios orígenes; una finca mantiene una variedad según acuerdo vigente.

**Decisión y persistencia:** Conservar el detalle de los orígenes seleccionados.

**Predeterminados y límites:** No crear origen genérico. Kilos por origen solo si se informaron; no repartir el total automáticamente.

**Fichas:** Sin ficha específica.

**Fuentes:** [modules.tsx:1516](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1516), [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24).

### cosecha

**Tabla:** `cosecha` · **Dictamen:** Conservar por función visible

**Interfaz:** Flujo de cosecha, organización, avances y cierre.

**Hallazgo:** Existe una operación con ciclo y datos distintos de la programación de entrega.

**Decisión y persistencia:** Conservar el estado de la cosecha y sus JSON de organización/avances/cierre; no crear tablas nuevas por cada pestaña.

**Predeterminados y límites:** PENDIENTE y JSON vacíos son válidos al iniciar. Código de lote generado de forma única si no hay campo manual; pesos y cierre solo al registrarse.

**Fichas:** Sin ficha específica.

**Fuentes:** [export-harvest.tsx:58](../prototipo/Campaign%20Management%20System/src/export-harvest.tsx#L58).

### analisis-calidad

**Tabla:** `analisis_calidad` · **Dictamen:** Conservar por función visible

**Interfaz:** Registrar/editar análisis por productor y finca.

**Hallazgo:** El análisis y su evidencia se registran; puede preceder a la cosecha.

**Decisión y persistencia:** Conservar relación por participación/finca y vínculo de cosecha opcional.

**Predeterminados y límites:** No asignar resultado APROBADO, fecha de examen ni medición cero por defecto. Cosecha NULL cuando el análisis es previo.

**Fichas:** Sin ficha específica.

**Fuentes:** [export-harvest.tsx:75](../prototipo/Campaign%20Management%20System/src/export-harvest.tsx#L75).

### medicion-mtd

**Tabla:** `medicion_mtd` · **Dictamen:** Conservar por función visible

**Interfaz:** MTD dentro del análisis y resumen compartido por finca.

**Hallazgo:** Se guarda una medición reutilizada por campaña/proveedor/finca y existe lógica de historial en el store.

**Decisión y persistencia:** Conservar medición/evidencia compartidas; no exigir un CRUD nuevo ni duplicar una medición por cada pantalla que la consulta.

**Predeterminados y límites:** No usar MTD=0 para significar pendiente. Fecha de registro técnica desde backend; valor y evidencia desde el examen real.

**Fichas:** Sin ficha específica.

**Fuentes:** [export-harvest.tsx:75](../prototipo/Campaign%20Management%20System/src/export-harvest.tsx#L75), [store.tsx:824](../prototipo/Campaign%20Management%20System/src/store.tsx#L824).

### carga

**Tabla:** `carga` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal de registro de carga.

**Hallazgo:** Carga contiene fecha, responsable, kilos, bultos y registro de operación.

**Decisión y persistencia:** Conservar una cabecera por carga y sus datos capturados.

**Predeterminados y límites:** Código único generado y registrado_at=now() son seguros; kilos, fecha de carga y responsable no se inventan.

**Fichas:** Sin ficha específica.

**Fuentes:** [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24).

### proveedor-carga

**Tabla:** `proveedor_carga` · **Dictamen:** Conservar por función visible

**Interfaz:** Filas de proveedores con kilos y envases en carga.

**Hallazgo:** La UI permite múltiples proveedores con cantidades propias.

**Decisión y persistencia:** Conservar detalle y envases de cada proveedor; su participación ya referencia cxp_id de campania_x_proveedores.

**Predeterminados y límites:** No crear filas vacías para todos los participantes ni dividir cantidades sin registro.

**Fichas:** Sin ficha específica.

**Fuentes:** [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24).

### origen-carga

**Tabla:** `origen_carga` · **Dictamen:** Conservar por función visible

**Interfaz:** Procedencia de la carga y sus fincas.

**Hallazgo:** El origen mantiene trazabilidad del recojo; el contexto puede heredarse de la entrega.

**Decisión y persistencia:** Conservar orígenes efectivamente seleccionados o confirmados desde la entrega.

**Predeterminados y límites:** Puede heredarse el origen real conocido; no elegir la primera finca arbitrariamente ni inventar kilos por finca.

**Fichas:** Sin ficha específica.

**Fuentes:** [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24), [modules.tsx:1516](../prototipo/Campaign%20Management%20System/src/modules.tsx#L1516).

### gasto-carga

**Tabla:** `gasto_carga` · **Dictamen:** Conservar por función visible

**Interfaz:** Gastos/cuadrilla dentro del registro de carga.

**Hallazgo:** Los gastos repetibles de la carga tienen datos propios aunque estén dentro del mismo modal.

**Decisión y persistencia:** Conservar gastos registrados; conceptos pueden ser lista fija sin tabla de catálogo adicional.

**Predeterminados y límites:** Sin gasto = ninguna fila. Cero solo como ausencia explícita de un concepto, no como comprobante/pago realizado.

**Fichas:** Sin ficha específica.

**Fuentes:** [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24).

### guia-remision

**Tabla:** `guia_remision` · **Dictamen:** Conservar por función visible

**Interfaz:** Editor de guía, documento y datos de transporte/llegada.

**Hallazgo:** La guía contiene datos históricos y documentos; no es una simple vista calculada.

**Decisión y persistencia:** Conservar cabecera y snapshots de destino, normas y proveedores.

**Predeterminados y límites:** Contenido JSON vacío en borrador; numeración real/generada única al emitir o permitir número pendiente en borrador. No usar número genérico ni dirección por defecto.

**Fichas:** Sin ficha específica.

**Fuentes:** [remission-editor.tsx:19](../prototipo/Campaign%20Management%20System/src/remission-editor.tsx#L19).

### proveedor-guia

**Tabla:** `proveedor_guia` · **Dictamen:** Conservar por función visible

**Interfaz:** Detalle de productores dentro de la guía.

**Hallazgo:** El documento incluye los proveedores/cantidades que realmente ampara.

**Decisión y persistencia:** Conservar detalle/snapshot al emitir; origen puede precargarse desde la carga confirmada.

**Predeterminados y límites:** No agregar todos los proveedores de campaña; incluir solo los de esta guía y cantidades reales.

**Fichas:** Sin ficha específica.

**Fuentes:** [remission-editor.tsx:19](../prototipo/Campaign%20Management%20System/src/remission-editor.tsx#L19), [load-registration.tsx:24](../prototipo/Campaign%20Management%20System/src/load-registration.tsx#L24).

### guia-x-norma

**Tabla:** `guia_x_norma` · **Dictamen:** Conservar por función visible

**Interfaz:** Selección de códigos fijos y texto generado en la guía.

**Hallazgo:** La selección múltiple existe, pero el prototipo ya guarda standardCodes y standardText dentro de los detalles del documento.

**Decisión y persistencia:** Conservar el puente. Al guardar borrador, resolver los códigos seleccionados contra norma y sincronizar sus filas; preservar standardCodes y standardText como snapshot, sin precargar todas las normas.

**Predeterminados y límites:** Sin normas elegidas: [] y texto vacío. No asignar todas las normas ni recalcular la frase de guías emitidas al cambiar el catálogo.

**Fichas:** Sin ficha específica.

**Fuentes:** [remission-model.ts:5](../prototipo/Campaign%20Management%20System/src/remission-model.ts#L5), [remission-editor.tsx:19](../prototipo/Campaign%20Management%20System/src/remission-editor.tsx#L19).

### historial-chofer

**Tabla:** `historial_chofer` · **Dictamen:** Conservar por función visible

**Interfaz:** Reportar etapa y consultar historial del despacho.

**Hallazgo:** Las etapas tienen actor y momento; una columna estado no conserva ese historial.

**Decisión y persistencia:** Conservar un evento por reporte real y evitar duplicación del mismo reporte al reintentar.

**Predeterminados y límites:** Fecha técnica al reportar; estado inicial no implica que ya se hayan reportado todas las etapas.

**Fichas:** Sin ficha específica.

**Fuentes:** [dispatch-model.ts:9](../prototipo/Campaign%20Management%20System/src/dispatch-model.ts#L9).

### recepcion-planta

**Tabla:** `recepcion_planta` · **Dictamen:** Conservar por función visible

**Interfaz:** Checklist del chofer y consulta logística.

**Hallazgo:** Se registran peso recibido, descarte, jabas y documentos; las secciones de administración son en parte lectura.

**Decisión y persistencia:** Conservar recepción/checklist sin exigir CRUD nuevo de recepción administrativa.

**Predeterminados y límites:** Pendiente no es cero kg ni no hubo descarte. Campos de resultado y cierre permanecen NULL/no confirmados hasta la acción correspondiente.

**Fichas:** Sin ficha específica.

**Fuentes:** [driver-receipt.tsx:15](../prototipo/Campaign%20Management%20System/src/driver-receipt.tsx#L15).

### liquidacion-proveedor

**Tabla:** `liquidacion_proveedor` · **Dictamen:** Conservar por función visible

**Interfaz:** Formulario de liquidación de compra y selección de persona.

**Hallazgo:** La liquidación identifica documento, compra, peso/precio y persona; pago se registra por separado.

**Decisión y persistencia:** Conservar documento y snapshots de identidad, moneda y UIT aplicada.

**Predeterminados y límites:** PEN para compras según decisión vigente. Saldo/estado se obtienen de movimientos; sin pago ni persona ficticia por defecto.

**Fichas:** Sin ficha específica.

**Fuentes:** [finance.tsx:125](../prototipo/Campaign%20Management%20System/src/finance.tsx#L125), [settlement-person-picker.tsx:24](../prototipo/Campaign%20Management%20System/src/settlement-person-picker.tsx#L24).

### liquidacion-transporte

**Tabla:** `liquidacion_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Liquidación de transporte por carga.

**Hallazgo:** El flete, descuentos y saldo por carga son visibles; no equivalen al acuerdo de campaña.

**Decisión y persistencia:** Conservar liquidación por carga y ajustes confirmados.

**Predeterminados y límites:** Ajustes opcionales sin importe pueden iniciar en cero; total, flete y moneda desde el acuerdo real. No dar por pagado al liquidar.

**Fichas:** Sin ficha específica.

**Fuentes:** [finance.tsx:224](../prototipo/Campaign%20Management%20System/src/finance.tsx#L224).

### gasto-transporte

**Tabla:** `gasto_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Viáticos de movilidad e insumos asociados a la carga.

**Hallazgo:** Hay campos monetarios por concepto; los conceptos son fijos pero los importes son datos de cada carga.

**Decisión y persistencia:** Conservar importes/conceptos, sin tabla tipo_gasto. Distinguirlos de gastos de cuadrilla y del pago del flete.

**Predeterminados y límites:** El editor normaliza viáticos vacíos a cero y PEN. incluido_en_liquidacion=false hasta aplicarlos; no crear movimientos de pago por esos ceros.

**Fichas:** Sin ficha específica.

**Fuentes:** [load-expenses.tsx:10](../prototipo/Campaign%20Management%20System/src/load-expenses.tsx#L10), [finance.tsx:224](../prototipo/Campaign%20Management%20System/src/finance.tsx#L224).

### adelanto-transporte

**Tabla:** `adelanto_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal Registrar adelanto entregado.

**Hallazgo:** El adelanto es un movimiento real por empresa/campaña, distinto del adelanto pactado en el acuerdo.

**Decisión y persistencia:** Conservar monto, fecha, método y evidencia del movimiento entregado.

**Predeterminados y límites:** No crear adelanto entregado al pactar su monto. Fecha precargada debe confirmarse; monto positivo y evidencia/método reales.

**Fichas:** Sin ficha específica.

**Fuentes:** [transport-advance-ui.tsx:34](../prototipo/Campaign%20Management%20System/src/transport-advance-ui.tsx#L34).

### aplicacion-adelanto

**Tabla:** `aplicacion_adelanto` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal Aplicar adelanto a esta carga.

**Hallazgo:** La aplicación parcial afecta saldos de adelanto y de liquidación; existe acción independiente.

**Decisión y persistencia:** Conservar cada aplicación y validar saldo/disponibilidad.

**Predeterminados y límites:** Fecha al confirmar y monto elegido dentro del saldo; no aplicar automáticamente todo el saldo disponible.

**Fichas:** Sin ficha específica.

**Fuentes:** [transport-advance-ui.tsx:20](../prototipo/Campaign%20Management%20System/src/transport-advance-ui.tsx#L20).

### factura-venta

**Tabla:** `factura_venta` · **Dictamen:** Conservar por función visible

**Interfaz:** Liquidación de venta, facturación y validación documental.

**Hallazgo:** Existe ciclo de documento y controles previos al cobro.

**Decisión y persistencia:** Conservar documento, serie/número/moneda y estado de facturación.

**Predeterminados y límites:** PREPARADA antes de facturar. Importe/moneda desde la venta real; no asumir USD por un filtro ni simular facturación al crear la fila.

**Fichas:** Sin ficha específica.

**Fuentes:** [sales-billing.ts:10](../prototipo/Campaign%20Management%20System/src/sales-billing.ts#L10), [finance.tsx:197](../prototipo/Campaign%20Management%20System/src/finance.tsx#L197).

### pago-proveedor

**Tabla:** `pago_proveedor` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal Registrar pago al proveedor.

**Hallazgo:** Pago parcial/total se registra con fecha, método y comprobante; liquidar no equivale a pagar.

**Decisión y persistencia:** Conservar cada movimiento contra su liquidación.

**Predeterminados y límites:** Método puede precargarse Transferencia para confirmar; monto no se ejecuta por abrir el modal. Moneda heredada del documento.

**Fichas:** Sin ficha específica.

**Fuentes:** [settlement-payment-modal.tsx:10](../prototipo/Campaign%20Management%20System/src/settlement-payment-modal.tsx#L10).

### pago-transporte

**Tabla:** `pago_transporte` · **Dictamen:** Conservar por función visible

**Interfaz:** Modal Registrar pago al transportista.

**Hallazgo:** El mismo componente diferencia los pagos de transporte y compra.

**Decisión y persistencia:** Conservar movimientos y relación con la liquidación de transporte.

**Predeterminados y límites:** Moneda del documento, fecha confirmada y monto real; no descontar dos veces las aplicaciones de adelanto.

**Fichas:** Sin ficha específica.

**Fuentes:** [settlement-payment-modal.tsx:10](../prototipo/Campaign%20Management%20System/src/settlement-payment-modal.tsx#L10), [transport-advance-ui.tsx:20](../prototipo/Campaign%20Management%20System/src/transport-advance-ui.tsx#L20).

### cobro-venta

**Tabla:** `cobro_venta` · **Dictamen:** Conservar por función visible

**Interfaz:** Formulario de cobro de venta.

**Hallazgo:** Los cobros se registran por documento con método, fecha y evidencia.

**Decisión y persistencia:** Conservar cobros y validaciones de documento/saldo.

**Predeterminados y límites:** Moneda del documento y fecha confirmada; estado pendiente antes del movimiento. No cobrar automáticamente al facturar.

**Fichas:** Sin ficha específica.

**Fuentes:** [finance.tsx:197](../prototipo/Campaign%20Management%20System/src/finance.tsx#L197), [sales-billing.ts:10](../prototipo/Campaign%20Management%20System/src/sales-billing.ts#L10).

## Límites y pendientes

- Alinear DTO, servicios y selectores del prototipo/web con el SQL objetivo. Compra/transporte son PEN por decisión vigente; no convertir importes cambiando solo su código.
- La UI multifruta debe alinearse con una fruta por campaña. Las variedades se consultan desde el catálogo relacionado.
- sesion_usuario se retiró por decisión del usuario: gestión persistente de sesiones, tokens y revocación fuera del alcance. usuario y rol se mantienen; el backend debe definir su autenticación sin depender de esta tabla.
- Estados, fechas técnicas, JSON vacíos y gastos opcionales pueden tener predeterminados reales. No inventar resultados, kilos distribuidos, identidad, pagos, cobros, evidencia o recepción.
- Este SQL instala un esquema nuevo. Si hubiera datos del diseño anterior, preparar mapeo y backfill de participaciones antes de migrar; no ejecutar DROP CASCADE sobre la base existente.

## Trazabilidad

SQL SHA-256: `5094ec9efdab160dcf7adafd5b29858c9cbe2caedc44796412ed3e79a9ea8963`. Referencias de código y huellas por archivo en el JSON. Generador: `.validation/auditar_tablas_propuestas.py`.
