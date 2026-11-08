"""Auditoría estática y reproducible de las propuestas; no modifica el SQL."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
from urllib.parse import quote

DOCS = Path(__file__).resolve().parents[2]
BASE = DOCS / 'agro-schema'
SRC = DOCS / 'prototipo/Campaign Management System/src'
DATE = '2026-10-29'
LABELS = {
    'simplificar': 'Simplificar o consolidar',
    'configurar': 'Conservar con seed/configuración',
    'tecnica': 'Conservar por función técnica',
    'diferir': 'Resolver con la autenticación',
    'conservar': 'Conservar por función visible',
}

# Las líneas se resuelven contra el código actual, no contra el recorrido anterior.
NEEDLES = {
    'menu': ('App.tsx', "key: 'comercial'"),
    'acceso': ('App.tsx', "account.role === 'driver'"),
    'personas': ('settlement-person-picker.tsx', 'Agregar persona vinculada'),
    'uit': ('purchase-uit.ts', 'export const UIT_VALUES'),
    'campana': ('modules.tsx', 'const derivadas = Array.from'),
    'proveedor': ('modules.tsx', 'function ProviderModal'),
    'participacion': ('modules.tsx', 'function CampaignProviderModal'),
    'certificacion': ('modules.tsx', 'function CertificationModal'),
    'ampliacion': ('modules.tsx', 'function CertificationExpansionModal'),
    'pago_certificacion': ('modules.tsx', 'function CertificationPaymentModal'),
    'requerimiento': ('modules.tsx', 'function CommercialParticipationModal'),
    'contrato': ('modules.tsx', 'export function CommercialContractModal'),
    'entrega': ('modules.tsx', 'function CommercialDeliveriesModal'),
    'variedades_entrega': ('modules.tsx', 'Kilos por variedad'),
    'solicitud': ('modules.tsx', 'function TransportRequestModal'),
    'cotizacion': ('modules.tsx', 'function TransportQuoteModal'),
    'acuerdo_transporte': ('modules.tsx', 'function TransportPaymentAgreementModal'),
    'cosecha': ('export-harvest.tsx', 'export function ExportHarvestFlow'),
    'analisis': ('export-harvest.tsx', 'function ExportAnalysisEditor'),
    'mtd': ('store.tsx', 'saveExportMtd: (record) =>'),
    'carga': ('load-registration.tsx', 'export function LoadRegistrationModal'),
    'viaticos': ('load-expenses.tsx', 'export function LoadTravelExpensesEditor'),
    'guia': ('remission-editor.tsx', 'export function RemissionGuideEditor'),
    'normas': ('remission-model.ts', 'export const GUIDE_STANDARDS'),
    'despacho': ('dispatch-model.ts', 'export function dispatchHistory'),
    'recepcion': ('driver-receipt.tsx', 'function DriverReceiptForm'),
    'liquidacion_proveedor': ('finance.tsx', 'function SourceLiquidationModal'),
    'liquidacion_transporte': ('finance.tsx', 'function TransportSettlementModal'),
    'adelanto': ('transport-advance-ui.tsx', 'function TransportAdvancePaymentModal'),
    'aplicacion': ('transport-advance-ui.tsx', 'export function ApplyTransportAdvanceModal'),
    'factura': ('sales-billing.ts', 'export function invoiceBillingIssue'),
    'pago': ('settlement-payment-modal.tsx', 'export function SettlementPaymentModal'),
    'cobro': ('finance.tsx', 'function FinancialMovementForm'),
    'frutas': ('store.tsx', 'export const FRUIT_CATALOG'),
}

# tabla, decisión, presencia UI, diagnóstico, propuesta concreta, valores por defecto,
# evidencias. Un detalle/selección puede justificar tabla sin CRUD independiente.
ROWS = [
('persona','conservar','Modal de personas vinculadas y selector de liquidación',
 'Se crean identidades reales y se elige a quién corresponde liquidar.',
 'Conservar persona y selección; no convertirlas en una persona genérica.',
 'Tipo de documento puede iniciar en DNI; nombre, documento y persona elegida deben ser reales.', ['personas']),
('rol','configurar','Acceso por perfil; sin administración de roles',
 'Los perfiles Administrador y Chofer se cargan mediante SQL inicial; el catálogo permite más perfiles sin requerir CRUD ahora.',
 'Mantener tabla rol y sus dos registros iniciales SQL; no crear pantalla de catálogo por ahora.',
 'Resolver por código estable; nunca usar un rol administrador predeterminado para cualquier cuenta.', ['acceso','menu']),
('usuario','tecnica','Identidad de acceso; sin CRUD de cuentas de negocio',
 'La ausencia de una pantalla de usuarios no elimina la necesidad de identificar al actor de las operaciones.',
 'Conservar si la autenticación del backend usa esta entidad; mapear identidad autenticada y responsable.',
 'Responsable desde la sesión autenticada, no usuario_id=1 ni una cuenta demo compartida.', ['acceso','menu']),
('sesion_usuario','diferir','No se observa gestión de sesiones; depende del mecanismo de acceso',
 'El prototipo no demuestra que se necesite persistir token_hash en una tabla propia.',
 'Usarla únicamente con sesiones opacas gestionadas por el backend; si se usa proveedor externo/JWT, justificar revocación o retirarla del SQL objetivo.',
 'creada_at=now() es correcto; token, expiración y revocación no se rellenan con valores ficticios.', ['acceso']),
('parametro_uit','configurar','Panel de consulta anual; valores en constantes del código',
 'Existe consulta por año y conversión de operaciones, pero no CRUD del parámetro anual.',
 'Conservar como tabla con datos iniciales SQL de 2025/2026 y umbral, ampliable por año sin CRUD; preservar snapshots aplicados.',
 'Seed por año conocido; umbral del prototipo 0.90. Año ausente debe requerir configuración, nunca asumir valor cero ni reutilizar otro año.', ['uit']),
('campana_x_fruta_derivada','simplificar','Chips calculados; no selección de variedades de campaña',
 'CampaignModal calcula derivadas desde FRUIT_CATALOG para las frutas seleccionadas; no administra filas de esta relación.',
 'Retirar la relación y obtener variedades desde la fruta/catálogo, mientras no exista selección de un subconjunto propio de campaña.',
 'No insertar todas las variedades como filas predeterminadas. Resolver antes la contradicción: UI permite varias frutas y el acuerdo vigente define una fruta por campaña.', ['campana','frutas']),
('proveedor_x_persona','conservar','Agregar persona vinculada, vínculo y selección para liquidar',
 'La relación representa personas vinculadas al proveedor y su vínculo, no un catálogo sin función.',
 'Conservar los vínculos registrados; el proveedor principal no necesita una vinculación ficticia consigo mismo.',
 'Sin filas automáticas; registrar solo personas realmente vinculadas. No inventar documento ni parentesco.', ['personas']),
('proveedor_x_fruta_derivada','conservar','Formulario del proveedor con variedades',
 'El proveedor declara variedades que comercializa; es una selección distinta de las variedades calculadas de una campaña.',
 'Conservar selección múltiple y unicidad proveedor/variedad.',
 'Lista vacía hasta elegir; no asignar todas las variedades del catálogo.', ['proveedor','frutas']),
('participacion_proveedor_campana','simplificar','Una sola vinculación proveedor–campaña en la UI',
 'El formulario guarda un CampaignProvider. El modelo mantiene además campania_x_proveedores para la misma participación lógica.',
 'Consolidar sobre campania_x_proveedores, conservando su ID y los campos necesarios. Remapear primero certificados y cargas; eliminar el enlace redundante entre ambas cabeceras.',
 'No mantener dos participaciones por defecto ni crear una segunda fila al vincular. La consolidación sigue siendo propuesta, no decisión aplicada.', ['participacion']),
('participacion_proveedor_x_fruta_derivada','simplificar','Variedad derivada de fruta/campaña; sin editor de esta asociación',
 'El alta de participación guarda fruta/variedad en un único payload; no hay mantenimiento de filas de este puente adicional.',
 'Retirar el puente y usar la variedad ya disponible en la participación, finca u origen. Si se incorpora selección múltiple real, revisar esa necesidad.',
 'No generar cruces con todas las variedades. Respetar la selección o el origen real.', ['participacion']),
('acuerdo_compra','simplificar','Precio y kilos dentro de la vinculación; sin acuerdo separado',
 'El prototipo no presenta contrato/versiones de compra separados de la participación; el precio simple ya vive en ella.',
 'Retirar la cabecera propuesta mientras no exista un flujo propio de acuerdos/versiones. Conservar precio/kilos y sus snapshots en participación y liquidación.',
 'No crear un acuerdo ficticio automáticamente para satisfacer el diseño.', ['participacion']),
('norma','configurar','Selectores fijos de certificación y códigos de guía',
 'No existe CRUD de normas. Los tipos de certificado y GUIDE_STANDARDS son listas de código; no son necesariamente la misma taxonomía.',
 'Conservar norma con cinco códigos iniciales SQL y FK explícitas. tipo_certificacion guarda la opción fija del certificado por separado; norma_id solo si se elige una relación real.',
 'Lista fija versionada; sin fila genérica ni norma por defecto. Certificados deben conservar el tipo elegido.', ['certificacion','normas']),
('certificado_campana_x_proveedor','conservar','Selección de productores cubiertos en certificado',
 'La cobertura por productor es real aunque se edite desde el modal de certificación y no tenga CRUD propio.',
 'Conservar cobertura y unicidad certificado/proveedor. La FK ya referencia cxp_id de campania_x_proveedores, incluida la coherencia compuesta de campaña/proveedor.',
 'Kilos autorizados deben derivarse de la cobertura real y guardarse como snapshot; no dividir el total por igual ni asignar cero para llenar el campo.', ['certificacion']),
('ampliacion_certificado_campana','conservar','Modal de ampliación del certificado',
 'Hay registro de kilos adicionales, fecha y observaciones; el historial no se sustituye por un único total.',
 'Conservar una fila por ampliación confirmada.',
 'Kilos y fecha confirmada no se inventan. Ninguna ampliación se crea al abrir el modal ni requiere un estado adicional no observado.', ['ampliacion']),
('pago_certificado_campana','conservar','Modal de pago del certificado',
 'Los pagos y su comprobante tienen registro propio en la interfaz.',
 'Conservar movimientos reales separados del monto del certificado.',
 'Fecha puede precargarse para confirmar; monto y moneda elegidos deben conservarse. No crear pago cero ni pago automático al emitir certificado.', ['pago_certificacion']),
('cliente_negocio_campana_x_fruta_derivada','conservar','Selección múltiple de variedades del requerimiento',
 'El cliente selecciona variedades; aquí el puente representa datos elegidos y no un cálculo automático.',
 'Conservar la relación de variedades requeridas sin CRUD de catálogo adicional.',
 'No asignar todas las variedades por defecto; guardar las elegidas en el formulario.', ['requerimiento']),
('contrato_venta','conservar','Formulario de contrato por requerimiento',
 'Se crean contratos con precio, moneda y condiciones/documento.',
 'Conservar contrato y snapshots de lo acordado.',
 'Conservar el estado que guarda el contrato real; no añadir un ciclo de borrador no observado. Precio/moneda no se infieren del selector de filtro.', ['contrato']),
('entrega_programada','conservar','Programación y edición de entrega',
 'La entrega tiene cantidades, fecha, destino y coordinación propios.',
 'Conservar; destino permanece texto obligatorio por D08 y no vuelve a ser catálogo.',
 'El estado de entrega se obtiene del flujo, sin agregar otra columna por rutina. Fecha, kilos y destino son datos reales; no usar dirección ni fecha ficticias.', ['entrega']),
('entrega_x_fruta_derivada','conservar','Campos Kilos por variedad cuando hay varias variedades',
 'El código actual permite distribuir kilos y valida la suma; existe una función visible de esta tabla.',
 'Conservar filas para la distribución registrada. Este editor actual matiza la evidencia anterior del recorrido del 27/10.',
 'Con una sola variedad puede derivarse el total; con varias no repartir por igual ni inventar cantidades si no se informó distribución.', ['variedades_entrega']),
('solicitud_transporte','conservar','Modal de solicitud y detalle de respuestas',
 'La solicitud tiene ventana, ruta, condiciones, kilos y transportistas seleccionados.',
 'Conservar cabecera y datos de la convocatoria.',
 'Inicio BORRADOR; la UI indica envío simulado. No registrar envío real por abrir o guardar el formulario.', ['solicitud']),
('invitacion_transporte','conservar','Empresas seleccionadas dentro de la solicitud',
 'Cada destinatario permite relacionar sus respuestas y la empresa seleccionada; no necesita CRUD separado.',
 'Conservar una fila por empresa seleccionada y correo snapshot opcional. Aclarar que INVITADA es estado lógico mientras no haya integración de envío.',
 'Correo desde empresa si existe; NULL si falta. No inventar correo ni marcar correo ENVIADO sin confirmación de envío.', ['solicitud','cotizacion']),
('cotizacion_transporte','conservar','Modal Registrar respuesta / TransportQuoteModal',
 'El prototipo actual sí tiene editor de empresa, monto, moneda, disponibilidad, condiciones y archivo.',
 'Conservar. disponibilidad text ya conserva el campo del editor sin un catálogo adicional.',
 'fecha puede capturarse al registrar si no hay fecha documental distinta. RECIBIDA al guardar respuesta real; monto y moneda son los de esa respuesta.', ['cotizacion']),
('acuerdo_transporte','conservar','Modal de acuerdo, monto, adelanto y saldo',
 'El acuerdo aceptado tiene función distinta de la cotización recibida y de la solicitud.',
 'Conservar confirmación y enlace con la empresa/campaña; fecha de acuerdo puede capturarse al confirmar.',
 'BORRADOR antes de confirmar. PEN según acuerdo vigente; corregir los selectores del prototipo que aún ofrecen otras monedas. No cambiar solo el código de una cotización USD sin conversión acordada.', ['acuerdo_transporte']),
('coordinacion_entrega','conservar','Coordinación de la entrega con transporte, chofer y ventana',
 'La coordinación identifica el viaje y las reservas, no una tabla adicional solo para una pantalla.',
 'Conservar la coordinación; responsables y recursos provienen de las selecciones y asignaciones reales.',
 'Sin transportista/chofer/vehículo ficticio por defecto; ventanas desde la coordinación confirmada.', ['entrega']),
('origen_entrega','conservar','Productores y fincas de recojo dentro de la entrega',
 'Una entrega puede reunir varios orígenes; una finca mantiene una variedad según acuerdo vigente.',
 'Conservar el detalle de los orígenes seleccionados.',
 'No crear origen genérico. Kilos por origen solo si se informaron; no repartir el total automáticamente.', ['entrega','carga']),
('cosecha','conservar','Flujo de cosecha, organización, avances y cierre',
 'Existe una operación con ciclo y datos distintos de la programación de entrega.',
 'Conservar el estado de la cosecha y sus JSON de organización/avances/cierre; no crear tablas nuevas por cada pestaña.',
 'PENDIENTE y JSON vacíos son válidos al iniciar. Código de lote generado de forma única si no hay campo manual; pesos y cierre solo al registrarse.', ['cosecha']),
('analisis_calidad','conservar','Registrar/editar análisis por productor y finca',
 'El análisis y su evidencia se registran; puede preceder a la cosecha.',
 'Conservar relación por participación/finca y vínculo de cosecha opcional.',
 'No asignar resultado APROBADO, fecha de examen ni medición cero por defecto. Cosecha NULL cuando el análisis es previo.', ['analisis']),
('medicion_mtd','conservar','MTD dentro del análisis y resumen compartido por finca',
 'Se guarda una medición reutilizada por campaña/proveedor/finca y existe lógica de historial en el store.',
 'Conservar medición/evidencia compartidas; no exigir un CRUD nuevo ni duplicar una medición por cada pantalla que la consulta.',
 'No usar MTD=0 para significar pendiente. Fecha de registro técnica desde backend; valor y evidencia desde el examen real.', ['analisis','mtd']),
('carga','conservar','Modal de registro de carga',
 'Carga contiene fecha, responsable, kilos, bultos y registro de operación.',
 'Conservar una cabecera por carga y sus datos capturados.',
 'Código único generado y registrado_at=now() son seguros; kilos, fecha de carga y responsable no se inventan.', ['carga']),
('proveedor_carga','conservar','Filas de proveedores con kilos y envases en carga',
 'La UI permite múltiples proveedores con cantidades propias.',
 'Conservar detalle y envases de cada proveedor; su participación ya referencia cxp_id de campania_x_proveedores.',
 'No crear filas vacías para todos los participantes ni dividir cantidades sin registro.', ['carga']),
('origen_carga','conservar','Procedencia de la carga y sus fincas',
 'El origen mantiene trazabilidad del recojo; el contexto puede heredarse de la entrega.',
 'Conservar orígenes efectivamente seleccionados o confirmados desde la entrega.',
 'Puede heredarse el origen real conocido; no elegir la primera finca arbitrariamente ni inventar kilos por finca.', ['carga','entrega']),
('gasto_carga','conservar','Gastos/cuadrilla dentro del registro de carga',
 'Los gastos repetibles de la carga tienen datos propios aunque estén dentro del mismo modal.',
 'Conservar gastos registrados; conceptos pueden ser lista fija sin tabla de catálogo adicional.',
 'Sin gasto = ninguna fila. Cero solo como ausencia explícita de un concepto, no como comprobante/pago realizado.', ['carga']),
('guia_remision','conservar','Editor de guía, documento y datos de transporte/llegada',
 'La guía contiene datos históricos y documentos; no es una simple vista calculada.',
 'Conservar cabecera y snapshots de destino, normas y proveedores.',
 'Contenido JSON vacío en borrador; numeración real/generada única al emitir o permitir número pendiente en borrador. No usar número genérico ni dirección por defecto.', ['guia']),
('proveedor_guia','conservar','Detalle de productores dentro de la guía',
 'El documento incluye los proveedores/cantidades que realmente ampara.',
 'Conservar detalle/snapshot al emitir; origen puede precargarse desde la carga confirmada.',
 'No agregar todos los proveedores de campaña; incluir solo los de esta guía y cantidades reales.', ['guia','carga']),
('guia_x_norma','conservar','Selección de códigos fijos y texto generado en la guía',
 'La selección múltiple existe, pero el prototipo ya guarda standardCodes y standardText dentro de los detalles del documento.',
 'Conservar el puente. Al guardar borrador, resolver los códigos seleccionados contra norma y sincronizar sus filas; preservar standardCodes y standardText como snapshot, sin precargar todas las normas.',
 'Sin normas elegidas: [] y texto vacío. No asignar todas las normas ni recalcular la frase de guías emitidas al cambiar el catálogo.', ['normas','guia']),
('historial_chofer','conservar','Reportar etapa y consultar historial del despacho',
 'Las etapas tienen actor y momento; una columna estado no conserva ese historial.',
 'Conservar un evento por reporte real y evitar duplicación del mismo reporte al reintentar.',
 'Fecha técnica al reportar; estado inicial no implica que ya se hayan reportado todas las etapas.', ['despacho']),
('recepcion_planta','conservar','Checklist del chofer y consulta logística',
 'Se registran peso recibido, descarte, jabas y documentos; las secciones de administración son en parte lectura.',
 'Conservar recepción/checklist sin exigir CRUD nuevo de recepción administrativa.',
 'Pendiente no es cero kg ni no hubo descarte. Campos de resultado y cierre permanecen NULL/no confirmados hasta la acción correspondiente.', ['recepcion']),
('liquidacion_proveedor','conservar','Formulario de liquidación de compra y selección de persona',
 'La liquidación identifica documento, compra, peso/precio y persona; pago se registra por separado.',
 'Conservar documento y snapshots de identidad, moneda y UIT aplicada.',
 'PEN para compras según decisión vigente. Saldo/estado se obtienen de movimientos; sin pago ni persona ficticia por defecto.', ['liquidacion_proveedor','personas']),
('liquidacion_transporte','conservar','Liquidación de transporte por carga',
 'El flete, descuentos y saldo por carga son visibles; no equivalen al acuerdo de campaña.',
 'Conservar liquidación por carga y ajustes confirmados.',
 'Ajustes opcionales sin importe pueden iniciar en cero; total, flete y moneda desde el acuerdo real. No dar por pagado al liquidar.', ['liquidacion_transporte']),
('gasto_transporte','conservar','Viáticos de movilidad e insumos asociados a la carga',
 'Hay campos monetarios por concepto; los conceptos son fijos pero los importes son datos de cada carga.',
 'Conservar importes/conceptos, sin tabla tipo_gasto. Distinguirlos de gastos de cuadrilla y del pago del flete.',
 'El editor normaliza viáticos vacíos a cero y PEN. incluido_en_liquidacion=false hasta aplicarlos; no crear movimientos de pago por esos ceros.', ['viaticos','liquidacion_transporte']),
('adelanto_transporte','conservar','Modal Registrar adelanto entregado',
 'El adelanto es un movimiento real por empresa/campaña, distinto del adelanto pactado en el acuerdo.',
 'Conservar monto, fecha, método y evidencia del movimiento entregado.',
 'No crear adelanto entregado al pactar su monto. Fecha precargada debe confirmarse; monto positivo y evidencia/método reales.', ['adelanto']),
('aplicacion_adelanto','conservar','Modal Aplicar adelanto a esta carga',
 'La aplicación parcial afecta saldos de adelanto y de liquidación; existe acción independiente.',
 'Conservar cada aplicación y validar saldo/disponibilidad.',
 'Fecha al confirmar y monto elegido dentro del saldo; no aplicar automáticamente todo el saldo disponible.', ['aplicacion']),
('factura_venta','conservar','Liquidación de venta, facturación y validación documental',
 'Existe ciclo de documento y controles previos al cobro.',
 'Conservar documento, serie/número/moneda y estado de facturación.',
 'PREPARADA antes de facturar. Importe/moneda desde la venta real; no asumir USD por un filtro ni simular facturación al crear la fila.', ['factura','cobro']),
('pago_proveedor','conservar','Modal Registrar pago al proveedor',
 'Pago parcial/total se registra con fecha, método y comprobante; liquidar no equivale a pagar.',
 'Conservar cada movimiento contra su liquidación.',
 'Método puede precargarse Transferencia para confirmar; monto no se ejecuta por abrir el modal. Moneda heredada del documento.', ['pago']),
('pago_transporte','conservar','Modal Registrar pago al transportista',
 'El mismo componente diferencia los pagos de transporte y compra.',
 'Conservar movimientos y relación con la liquidación de transporte.',
 'Moneda del documento, fecha confirmada y monto real; no descontar dos veces las aplicaciones de adelanto.', ['pago','aplicacion']),
('cobro_venta','conservar','Formulario de cobro de venta',
 'Los cobros se registran por documento con método, fecha y evidencia.',
 'Conservar cobros y validaciones de documento/saldo.',
 'Moneda del documento y fecha confirmada; estado pendiente antes del movimiento. No cobrar automáticamente al facturar.', ['cobro','factura']),
]

CONSTANTS = [
 {'name':'Moneda','storage':'Campo moneda en cada transacción; no hay tabla moneda propuesta.', 'proposal':'Opciones fijas por contexto. Compra y acuerdo de transporte: PEN según decisión vigente. Ventas/certificados conservan la moneda elegida entre las opciones permitidas. El prototipo aún ofrece otras monedas en transporte: alinear la UI y sus validaciones, sin cambiar solo la etiqueta de un importe.', 'evidence':['participacion','acuerdo_transporte','contrato','cotizacion']},
 {'name':'Perfiles','storage':'rol o enum; usuario mantiene el perfil real.', 'proposal':'Administrador y Chofer pueden ser seed. No se necesita CRUD de roles para este prototipo; la autorización sí debe comprobarse en backend.', 'evidence':['acceso']},
 {'name':'Normas y tipos de certificado','storage':'Códigos/tipos validados y snapshots del documento.', 'proposal':'norma permanece como tabla con cinco códigos iniciales. guia_x_norma guarda selecciones reales; tipo_certificacion es un campo validado con opciones fijas, independiente del catálogo de normas. Se conserva la frase emitida.', 'evidence':['normas','certificacion']},
 {'name':'Frutas y variedades','storage':'fruta/fruta_derivada son tablas actuales; relaciones de selección cuando corresponda.', 'proposal':'FRUIT_CATALOG puede alimentar seed de los catálogos existentes. No hardcodear IDs numéricos ni copiar todas las variedades a cada campaña. La UI multifruta contradice el acuerdo de una fruta por campaña.', 'evidence':['frutas','campana']},
 {'name':'UIT anual y umbral','storage':'Configuración por año y snapshot de los valores aplicados.', 'proposal':'Puede mantenerse seed/configuración controlada sin CRUD. No es una constante eterna ni se completa un año ausente con cero. Esta auditoría observa código; no valida vigencia normativa de sus importes.', 'evidence':['uit']},
 {'name':'Tipos de examen, etapas y estados','storage':'Código/enum/CHECK; resultados e historial por operación.', 'proposal':'Opciones fijas del prototipo sin una tabla de catálogo por selector. El estado inicial no sustituye un evento o resultado real.', 'evidence':['analisis','despacho']},
 {'name':'Métodos de pago y conceptos de viático','storage':'Código/texto validado en el movimiento o gasto.', 'proposal':'Listas fijas sin catálogos nuevos. Mantener importes, evidencias y aplicaciones: un concepto fijo no vuelve fijo al movimiento.', 'evidence':['pago','viaticos','adelanto']},
]


def build():
    sql_path = BASE / '03_schema_total.sql'
    sql = sql_path.read_text(encoding='utf-8')
    model = json.loads((BASE / '.validation/modelo_revision.json').read_text(encoding='utf-8'))
    proposed = set(re.findall(r'^-- TABLA PROPUESTA: ([^\r\n]+)', sql, re.M))
    from simplificacion_modelo import REMOVED
    assert len(ROWS)==46 and len(proposed)==41
    assert set(row[0] for row in ROWS) == proposed | set(REMOVED)
    assert len(set(row[0] for row in ROWS)) == len(ROWS)
    evidence = {}
    for key, (file, needle) in NEEDLES.items():
        path = SRC / file
        lines = path.read_text(encoding='utf-8').splitlines()
        matches = [(i, line) for i, line in enumerate(lines, 1) if needle in line]
        assert matches, f'Falta evidencia {key}: {file}: {needle}'
        line, excerpt = matches[0]
        evidence[key] = {'file':file, 'line':line, 'needle':needle, 'excerpt':excerpt.strip()[:360],
                         'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    report = (BASE / '01_reporte_especifico.md').read_text(encoding='utf-8')
    refs = list(re.finditer(r'\*\*Referencia de revisión:\*\*\s*(V\d+)', report))
    views = {name:[] for name in proposed}
    for i, match in enumerate(refs):
        chunk = report[match.end():refs[i+1].start() if i+1 < len(refs) else len(report)]
        block = re.search(r'\*\*Funcionalidad esperada de cada tabla en esta vista:\*\*\s*\n\n(.*?)(?:\n\n\*\*Esquema de relaciones|\n\n## |\Z)', chunk, re.S)
        if block:
            for name in set(re.findall(r'^\|\s*`([^`]+)`', block.group(1), re.M)) & proposed:
                views[name].append(match.group(1))
    records = []; removed_records = []
    for table, decision, ui, finding, proposal, defaults, sources in ROWS:
        assert decision in LABELS and all(x in evidence for x in sources)
        if table in REMOVED:
            removed_records.append({'table':table,'outcome':'Consolidada en campania_x_proveedores' if table=='participacion_proveedor_campana' else 'Retirada del objetivo','finding':finding,'evidence':sources})
            continue
        definition = model['tables'][table]
        records.append({'table':table, 'decision':decision, 'label':LABELS[decision], 'ui':ui,
                        'finding':finding, 'proposal':proposal, 'defaults':defaults,
                        'views':views[table], 'evidence':sources,
                        'columns':len(definition['columns']),
                        'inbound_fks':[r for r in model['refs'] if r['parent']==table],
                        'outbound_fks':[r for r in model['refs'] if r['child']==table]})
    counts = Counter(r['decision'] for r in records)
    assert counts == {'conservar':37, 'configurar':3, 'tecnica':1}, counts
    output = {'date':DATE, 'method':'Auditoría estática del código local, contrastada con las fichas V01–V62. No prueba ejecución ni persistencia normalizada del backend.',
              'scope':'46 propuestas revisadas originalmente: cinco retiradas/consolidadas y 41 vigentes; 19 tablas actuales conservadas.',
              'applied':True, 'reviewed_total':46, 'removed_tables':removed_records, 'sql_sha256':hashlib.sha256(sql_path.read_bytes()).hexdigest(),
              'schema_tables':60, 'counts':dict(counts), 'labels':LABELS,
              'evidence':evidence, 'constants':CONSTANTS, 'tables':records}
    (BASE / 'auditoria-tablas-propuestas.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    write_markdown(output)
    print(json.dumps({'audit_date':DATE,'proposed_tables':len(records),'decisions':dict(counts),'evidence':len(evidence),'simplifications_applied':5}, ensure_ascii=False))


def source_link(key, data):
    e = data['evidence'][key]
    href = '../prototipo/Campaign%20Management%20System/src/'+quote(e['file'])+'#L'+str(e['line'])
    return f"[{e['file']}:{e['line']}]({href})"


def write_markdown(data):
    lines=['# Auditoría aplicada al esquema agroexportador', '', '**Decisiones incorporadas al SQL objetivo — 29/10/2026.**', '',
     'Se revisaron 46 propuestas originales: cinco se retiraron o consolidaron y quedan **41 propuestas vigentes**, junto a 19 tablas actuales: **60 tablas y 124 FK**. Se conserva norma con datos iniciales y guia_x_norma para selecciones reales. Estos cambios están incorporados al SQL y los HTML de revisión; no se ha modificado una base desplegada ni la aplicación.', '',
     '[Revisar HTML por vistas](diagramas/esquema-agro-vistas.html#auditoria) · [SQL total](03_schema_total.sql) · [Datos iniciales reejecutables](04_datos_iniciales.sql) · [Evidencias JSON](auditoria-tablas-propuestas.json)', '',
     '## Simplificaciones y retiro de sesiones confirmado', '',
     '| Tabla | Decisión aplicada |', '|---|---|']
    for r in data['removed_tables']:
        lines.append(f"| `{r['table']}` | {r['outcome']}. No se conserva una cabecera/acuerdo/puente sin función independiente. |")
    lines += ['| `norma` | Conservada como catálogo relacionado, con cinco códigos iniciales SQL. |',
              '| `guia_x_norma` | Conservada para las normas seleccionadas de cada guía; no recibe filas del seed. |', '',
              'La participación única es campania_x_proveedores.cxp_id. Certificados y cargas ya la referencian; la FK compuesta conserva coherencia de campaña/proveedor. cantidad_proveedor, tipo_proveedor, estado, created_at, precio y observaciones mantienen la información equivalente sin duplicarla. El tipo de fruta sigue la regla del proveedor y las etapas se obtienen de examen/entrevista. No se añaden filas de variedades derivadas de la campaña; sí permanecen las selecciones reales de proveedor/cliente y distribución de kilos por variedad.', '',
              '## Catálogos iniciales y opciones constantes', '',
              'El SQL total ya carga dos perfiles, cinco normas, cinco frutas, 17 variedades y dos parámetros anuales tomados del prototipo. 04_datos_iniciales.sql permite repetir la carga sin duplicar registros ni sobrescribir configuración existente. Los importes UIT proceden del código y requieren revisión antes de operación; no se acredita vigencia normativa.', '',
              '| Selector o parámetro | Persistencia | Decisión |', '|---|---|---|']
    for c in data['constants']:
        lines.append(f"| {c['name']} | {c['storage']} | {c['proposal']} |")
    lines += ['', '## Cómo se guarda guia_x_norma', '',
              '1. El selector consulta norma y presenta los códigos iniciales; no se necesita CRUD del catálogo.',
              '2. Al guardar una guía en borrador, el servicio resuelve los códigos elegidos a norma_id y sincroniza solo sus filas de guia_x_norma en la misma transacción. UNIQUE (guia_remision_id, norma_id) impide duplicados.',
              '3. Una selección vacía deja cero filas. No se asigna NOP ni todas las normas por defecto; un código desconocido se rechaza.',
              '4. contenido.standardCodes refleja esa selección y standardText conserva el texto histórico. Al emitir se congela el documento; cambiar el catálogo después no reescribe sus frases.',
              '5. El SQL aporta catálogo, FK y unicidad; la sincronización del formulario, los permisos y el bloqueo de guías emitidas corresponden al servicio aún por implementar.', '',
              '## Alcance de la evidencia', '', data['method'], '',
              'Las fichas Vxx identifican usos documentados, no CRUD independiente. La auditoría no ejecutó un nuevo recorrido manual de las 62 vistas. Los editores actuales de cotización y kilos por variedad justifican conservar sus tablas. disponibilidad text y tipo_certificacion guardan sus opciones/datos sin catálogos nuevos.', '',
              '## Dictamen de las 41 propuestas vigentes', '', '| Tabla | Interfaz | Dictamen |', '|---|---|---|']
    for r in data['tables']:
        lines.append(f"| [`{r['table']}`](#{r['table'].replace('_','-')}) | {r['ui']} | {r['label']} |")
    for r in data['tables']:
        lines += ['', '### '+r['table'].replace('_','-'), '', f"**Tabla:** `{r['table']}` · **Dictamen:** {r['label']}", '',
                  f"**Interfaz:** {r['ui']}.", '', f"**Hallazgo:** {r['finding']}", '', f"**Decisión y persistencia:** {r['proposal']}", '',
                  f"**Predeterminados y límites:** {r['defaults']}", '',
                  '**Fichas:** '+(', '.join(f'[{v}](diagramas/esquema-agro-vistas.html#{v.lower()})' for v in r['views']) or 'Sin ficha específica')+'.', '',
                  '**Fuentes:** '+', '.join(source_link(k,data) for k in r['evidence'])+'.']
    lines += ['', '## Límites y pendientes', '',
              '- Alinear DTO, servicios y selectores del prototipo/web con el SQL objetivo. Compra/transporte son PEN por decisión vigente; no convertir importes cambiando solo su código.',
              '- La UI multifruta debe alinearse con una fruta por campaña. Las variedades se consultan desde el catálogo relacionado.',
              '- sesion_usuario se retiró por decisión del usuario: gestión persistente de sesiones, tokens y revocación fuera del alcance. usuario y rol se mantienen; el backend debe definir su autenticación sin depender de esta tabla.',
              '- Estados, fechas técnicas, JSON vacíos y gastos opcionales pueden tener predeterminados reales. No inventar resultados, kilos distribuidos, identidad, pagos, cobros, evidencia o recepción.',
              '- Este SQL instala un esquema nuevo. Si hubiera datos del diseño anterior, preparar mapeo y backfill de participaciones antes de migrar; no ejecutar DROP CASCADE sobre la base existente.', '',
              '## Trazabilidad', '', f"SQL SHA-256: `{data['sql_sha256']}`. Referencias de código y huellas por archivo en el JSON. Generador: `.validation/auditar_tablas_propuestas.py`.", '']
    (BASE/'auditoria-tablas-propuestas-vs-prototipo.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    build()
