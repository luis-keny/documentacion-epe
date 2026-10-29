from pathlib import Path
import ast,json,re
R=Path(__file__).resolve().parent.parent
previous=(R/'01_reporte_especifico.md').read_text(encoding='utf8')
history=previous.split('## Validación de negocio y cuestionario pendiente',1)
history=('## Validación de negocio y cuestionario pendiente'+history[1]).split('## Schema actualizado tras la auditoría de cumplimiento',1)[0].rstrip() if len(history)>1 else ''
M=json.loads((R/'.validation/modelo_revision.json').read_text(encoding='utf8'))
T=M['tables']; F=M['refs']; A={x['table']:x for x in json.loads((R/'.validation/modelo_actual.json').read_text(encoding='utf8'))}
rename=json.loads((R/'.validation/renombres_tablas.json').read_text(encoding='utf8'))
results=json.loads((R/'.validation/resultado_revision.json').read_text(encoding='utf8'))
views=[]
revised_rules={
'Gestión Comercial — Clientes':'Se reutiliza cliente_negocio. El prototipo no tiene CRUD independiente de destinos; la entrega conserva destino como texto y la guía su dirección de llegada histórica (D08, 29/10/2026).',
'Entregas programadas':'Un contrato puede tener varias entregas. El servicio deberá controlar que sus kilos no superen el contrato y que la distribución por variedad sume la cabecera. El SQL declara las relaciones y cantidades positivas; esas sumas entre filas siguen pendientes de implementación transaccional.',
'Pago de certificación':'Se proponen pagos parciales en la moneda del certificado. Comprobar el saldo antes de registrar un pago y conservar sus evidencias son reglas del servicio a implementar. El costo y recibo actuales se conservan sin convertir automáticamente un recibo en un pago.',
'Transportistas por campaña':'acuerdo_transporte es una entidad nueva vinculada a la empresa y campaña actuales. Sus adelantos se registran aparte; no se infiere un pago por elegir una modalidad. Si se requiere guardar la vinculación sin acuerdo completo, revisar ese estado antes de implementar.',
'Programa semanal de entregas':'La consulta v_programa_semanal agrupa programación por variedad, año y semana ISO. La placa puede seguir sin asignar. No se crea otra tabla calendario ni se confunden cantidades programadas con cantidades cargadas.',
'Guías de remisión':'Una carga puede tener varias guías, con proveedores y kilos asignados. Las FK compuestas mantienen guía y detalle en la misma carga. La validación de kilos acumulados, punto físico de salida, bultos y emisión documental debe implementarse antes de utilizarlo en operación.',
'Cargas de campaña':'El último reporte puede consultarse desde v_estado_despacho. trazabilidad_transporte y sus estados actuales se conservan mientras se define el paso al historial de eventos propuesto. No cambiar los registros antiguos para hacerlos coincidir con un tablero de demostración.',
'Consulta de entrega':'Se documentan peso de origen, peso recibido, descarte y respaldo por carga. La diferencia entre balanzas no se clasifica automáticamente como descarte. Comprobar recepción completa antes de facturar es parte del servicio posterior; no se inventan reportes a partir de facturas.',
'Cargas registradas del cliente':'La factura propuesta conserva kilos facturados, precio, moneda e importe. Las restricciones locales comprueban importe y datos mínimos de emisión; el servicio debe validar el origen de peso/precio frente a recepción y contrato, impedir cambios posteriores y distinguir preparación de factura externa emitida.',
'Historial de cobros':'Una factura puede tener varios cobros en su moneda. El SQL exige montos positivos y referencia única por factura; la comprobación de saldo, factura emitida, permisos e inmutabilidad debe implementarse como proceso transaccional. Los reversos requieren un flujo explícito.',
'Liquidación de compra — Documento':'El documento de compra debe conservar persona, carga, importe y evidencia. El servicio debe calcularlo desde los kilos/precios aplicados y protegerlo después de registrar movimientos. Esta revisión estructural todavía no implementa ese cálculo ni el flujo de rectificación.',
'Control UIT por proveedor':'El acumulado se consulta por persona y año desde documentos de compra. parametro_uit incluye los valores iniciales del prototipo, que deben revisarse antes de operación. v_control_uit deja disponible nulo si falta el parámetro anual. No se mezclan compras registradas con dinero ya pagado.',
'Registrar descarte':'Nulo significa no informado; false significa informado sin descarte y cero kilos. El modelo propone evidencia obligatoria cuando hay descarte positivo. La comparación contra el peso de origen y el permiso de confirmar el checklist deberán validarse en el servicio.',
'Cerrar despacho':'Antes de cerrar deberá comprobarse llegada, recepción, descarte informado y documento de salida. Esa transición y sus permisos todavía necesitan servicio; historial_chofer aporta los datos para conservar eventos. La devolución de jabas no se vuelve obligatoria sin confirmar su uso en las vistas.'}
tree=ast.parse((R/'.validation/documentar.py').read_text(encoding='utf8'))
for n in tree.body:
    if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='V':
        args=[ast.literal_eval(x) for x in n.value.args]
        name,path,observed,tables,rule=args[:5]
        rule=revised_rules.get(name,rule)
        views.append({'name':name,'path':path,'observed':observed,'tables':[rename[t] for t in tables.split()],'rule':rule})
for v in views:
    if v['name']=='Gestión de transporte':v['tables']+=['vehiculo_externo','chofer_transporte_externo','trazabilidad_transporte','chofer_vehiculo_externo','detalle_trazabilidad']
    if v['name']=='Contratos — Participaciones comerciales':v['rule']='Se conserva el vínculo único cliente/campaña de cliente_negocio_campana. Los contratos múltiples se agregan como hijos en contrato_venta; no se duplica el vínculo para crear otro contrato.'
    if v['name']=='Certificaciones':v['rule']='La referencia inspeccionada muestra un certificado por campaña, pero el backend admite varios. Esta revisión conserva esa capacidad: cada certificado puede incorporar norma, organismo, moneda y cobertura. Revisar la diferencia con las vistas antes de imponer una nueva unicidad.'
    if v['name']=='Choferes':v['rule']='Se conserva el nombre y contacto del conductor. persona_id, usuario_id y numero_licencia son adicionales opcionales. No se inventan documentos ni se obliga a rehacer los registros actuales para instalar el modelo de revisión.'
    if v['name']=='Vehículos':v['rule']='Se conservan volumen, ancho, altura, profundidad, peso_neto y peso_bruto. capacidad_kg es un atributo adicional independiente; no se convierte peso_neto a capacidad. Confirmar unidades con las vistas antes de importar datos.'
    if v['name']=='Entrevista':v['rule']='Se reutiliza entrevista_extencion con entrevista_id, cam_x_prov_id, finca_id y codigo FVV único. Se conservan densidad, distanciamiento, frecuencia y anio_aplicacion. Los atributos adicionales permiten describir distanciamiento/riego y guardar aplicaciones_al_ano sin confundir cantidad con año calendario.'
    if v['name']=='Exámenes':v['rule']='Se conserva examen_proveedor y su resultado obligatorio positivo/negativo. Se proponen contexto cxp_id/finca_id, muestra, envío, estado y archivo. El nuevo estado por sí solo no habilita exámenes pendientes sin resultado: esa transición requiere revisar nulabilidad y DTO en una futura implementación.'
    if v['name']=='Gestión de Campaña':v['rule']='Se conservan campania_id, fruta_id, estado y requerimiento_comercial, con la regla de una campaña activa por fruta. Se añaden temporada, responsable, lineamientos y datos de cierre. Cambiar el estado automáticamente o verificar el cierre completo corresponde al servicio posterior.'
    if v['name']=='Proveedores de campaña':v['rule']='Por decisión del 27/10/2026, campania_x_proveedores representa al proveedor en la campaña y no selecciona finca: se retira finca_id y su FK. El SQL propone un registro por campaña/proveedor, extendiendo la unicidad que antes aplicaba a registros sin finca. Las entrevistas conservan finca_id y comprueban su pertenencia al proveedor. participacion_proveedor_campana sigue siendo una cabecera opcional propuesta cuya necesidad debe revisarse para evitar duplicar la participación. No se fusionan registros existentes automáticamente.'
    if v['name']=='Revisar cierre de campaña':v['rule']='Se documentan atributos de cierre en campana. El SQL conserva las reglas actuales y prepara las relaciones nuevas, pero no implementa un proceso completo de cierre financiero/documental. Definir y programar la comprobación transaccional de pendientes después de la revisión manual.'
    if v['name']=='Mi despacho':v['rule']='El historial propuesto permite separar los eventos del chofer del estado resumido de trazabilidad_transporte. La transición entre estados, el permiso del chofer asignado y el cierre del checklist requieren implementación de servicio; no se deducen de una actualización manual del estado.'
    # Sustituye nombres técnicos anteriores sin alterar las palabras normales del texto.
    compound={k:value for k,value in rename.items() if '_' in k}
    rx=re.compile(r'\b(?:'+'|'.join(sorted(compound,key=len,reverse=True))+r')\b')
    v['rule']=rx.sub(lambda m:compound[m.group()],v['rule'])
for v in views:
    v['tables']=[t for t in v['tables'] if t in T]
    v['rule']=v['rule'].replace('Los archivos se referencian por identificador de almacenamiento.','La integración documental queda pendiente; las referencias reservadas son opcionales y no tienen FK.')
    v['rule']=v['rule'].replace('El documento personal se guarda en personas y su archivo de identidad se referencia en archivos.','Se conservan los datos personales y la URL de identidad actuales; la referencia documental propuesta queda opcional y pendiente de relación.')
    if v['name']=='Guía de salida del vehículo':v['rule']='El adjunto de salida queda pendiente de la integración documental. Se conserva la fecha de registro como dato opcional, sin exigir un identificador de archivo ni afirmar un historial de almacenamiento implementado. Las guías de remisión estructuradas conservan su entidad propia.'
    if v['name']=='Registrar descarte':v['rule']='Nulo significa no informado; false indica informado sin descarte. El SQL conserva las reglas de kilos. La evidencia documental queda pendiente de integración: no hay tabla archivo ni FK a ella, y no se exige un identificador documental. La comparación con peso de origen y los permisos necesitan implementación del servicio.'
# Revisión de navegación 27/10/2026. E = escritura esperada; C = consulta;
# D = diseño por discutir; H = compatibilidad con el backend, sin editor propio observado.
specs={}
def S(i,e='',c='',d='',h=''):
    specs[i]={'E':e.split(),'C':c.split(),'D':d.split(),'H':h.split()}
S(1,'','usuario rol persona','sesion_usuario')
S(2)
S(3,'cliente_negocio')
S(4,'','cliente_negocio cliente_negocio_campana campana contrato_venta')
S(5,'cliente_negocio_campana cliente_negocio_campana_x_fruta_derivada','cliente_negocio campana fruta_derivada contrato_venta')
S(6,'','cliente_negocio_campana cliente_negocio campana cliente_negocio_campana_x_fruta_derivada fruta_derivada contrato_venta entrega_programada coordinacion_entrega')
S(7,'contrato_venta','cliente_negocio_campana cliente_negocio campana entrega_programada')
S(8,'entrega_programada entrega_x_fruta_derivada','contrato_venta cliente_negocio_campana cliente_negocio fruta_derivada coordinacion_entrega carga')
S(9,'campana campana_x_fruta_derivada','fruta fruta_derivada usuario')
S(10,'','campana fruta fruta_derivada campana_x_fruta_derivada usuario campania_x_proveedores examen_proveedor certificado_campana certificado_campana_x_proveedor ampliacion_certificado_campana cliente_negocio_campana contrato_venta entrega_programada coordinacion_entrega cosecha carga recepcion_planta')
S(11,'campania_x_proveedores','proveedor campana proveedor_x_fruta proveedor_x_fruta_derivada fruta fruta_derivada entrevista_extencion finca examen_proveedor','participacion_proveedor_campana participacion_proveedor_x_fruta_derivada')
S(12,'entrevista_extencion finca','campania_x_proveedores proveedor campana fruta_derivada fruta','acuerdo_compra')
S(13,'examen_proveedor','campania_x_proveedores proveedor finca campana fruta')
S(14,'certificado_campana certificado_campana_x_proveedor','campana campania_x_proveedores proveedor norma ampliacion_certificado_campana pago_certificado_campana','participacion_proveedor_campana')
S(15,'ampliacion_certificado_campana','certificado_campana')
S(16,'pago_certificado_campana','certificado_campana')
S(17,'acuerdo_transporte','empresa_transporte_externo campana','adelanto_transporte')
S(18,'','campana entrega_programada contrato_venta cliente_negocio_campana cliente_negocio coordinacion_entrega carga')
S(19,'coordinacion_entrega origen_entrega','entrega_programada contrato_venta cliente_negocio_campana cliente_negocio campana acuerdo_transporte empresa_transporte_externo vehiculo_externo chofer_transporte_externo campania_x_proveedores proveedor entrevista_extencion finca fruta_derivada')
S(20,'','campana cliente_negocio cliente_negocio_campana contrato_venta entrega_programada entrega_x_fruta_derivada fruta_derivada coordinacion_entrega vehiculo_externo')
S(21,'proveedor proveedor_x_fruta proveedor_x_fruta_derivada','fruta fruta_derivada','persona proveedor_x_persona')
S(22,'','proveedor proveedor_x_fruta proveedor_x_fruta_derivada fruta fruta_derivada','persona')
S(23,'finca','proveedor fruta fruta_derivada')
S(24,'certificado_proveedor','proveedor')
S(25,'empresa_transporte_externo','vehiculo_externo chofer_transporte_externo','persona')
S(26,'empresa_transporte_externo','vehiculo_externo chofer_transporte_externo')
S(27,'vehiculo_externo','empresa_transporte_externo')
S(28,'chofer_transporte_externo','empresa_transporte_externo','persona usuario')
S(29,'solicitud_transporte invitacion_transporte cotizacion_transporte','campana empresa_transporte_externo')
S(30,'solicitud_transporte invitacion_transporte cotizacion_transporte','campana empresa_transporte_externo')
S(31,'','campana cliente_negocio cliente_negocio_campana contrato_venta entrega_programada cosecha carga','')
S(32,'','campana fruta cosecha carga')
S(33,'analisis_calidad medicion_mtd','campana campania_x_proveedores proveedor entrevista_extencion finca fruta_derivada cosecha')
S(34,'carga proveedor_carga origen_carga gasto_carga','campana coordinacion_entrega entrega_programada contrato_venta cliente_negocio_campana cliente_negocio empresa_transporte_externo vehiculo_externo chofer_transporte_externo proveedor finca fruta_derivada cosecha analisis_calidad')
S(35,'','cosecha carga coordinacion_entrega origen_entrega campania_x_proveedores proveedor finca fruta_derivada entrega_programada contrato_venta cliente_negocio_campana empresa_transporte_externo vehiculo_externo chofer_transporte_externo analisis_calidad medicion_mtd proveedor_carga origen_carga')
S(36,'','carga proveedor_carga coordinacion_entrega entrega_programada contrato_venta cliente_negocio_campana cliente_negocio empresa_transporte_externo vehiculo_externo chofer_transporte_externo guia_remision proveedor_guia guia_x_norma norma')
S(37,'guia_remision proveedor_guia guia_x_norma','carga proveedor_carga origen_carga origen_entrega finca proveedor fruta_derivada coordinacion_entrega empresa_transporte_externo vehiculo_externo chofer_transporte_externo entrega_programada contrato_venta cliente_negocio_campana cliente_negocio norma')
S(38,'','campana cliente_negocio_campana contrato_venta entrega_programada coordinacion_entrega carga historial_chofer')
S(39,'','campana carga coordinacion_entrega historial_chofer entrega_programada contrato_venta cliente_negocio_campana cliente_negocio vehiculo_externo chofer_transporte_externo')
S(40,'','campana coordinacion_entrega origen_entrega finca entrega_programada contrato_venta cliente_negocio_campana cliente_negocio empresa_transporte_externo vehiculo_externo chofer_transporte_externo carga proveedor_carga proveedor fruta_derivada gasto_carga historial_chofer recepcion_planta guia_remision')
S(41,'','campana carga coordinacion_entrega entrega_programada contrato_venta cliente_negocio_campana')
S(42,'','campana cliente_negocio cliente_negocio_campana contrato_venta entrega_programada coordinacion_entrega carga factura_venta cobro_venta')
S(43,'factura_venta','cliente_negocio cliente_negocio_campana contrato_venta entrega_programada coordinacion_entrega carga proveedor_carga recepcion_planta cobro_venta')
S(44,'cobro_venta','factura_venta carga cliente_negocio_campana cliente_negocio')
S(45,'','campana carga coordinacion_entrega entrega_programada contrato_venta cliente_negocio_campana liquidacion_proveedor pago_proveedor liquidacion_transporte pago_transporte')
S(46,'','campana carga proveedor_carga proveedor liquidacion_proveedor liquidacion_transporte coordinacion_entrega empresa_transporte_externo vehiculo_externo chofer_transporte_externo entrega_programada contrato_venta cliente_negocio_campana cliente_negocio')
S(47,'liquidacion_proveedor pago_proveedor','carga proveedor_carga proveedor fruta_derivada persona proveedor_x_persona')
S(48,'','liquidacion_proveedor pago_proveedor carga proveedor_carga proveedor persona proveedor_x_persona')
S(49,'','parametro_uit proveedor proveedor_x_persona persona liquidacion_proveedor carga')
S(50,'liquidacion_transporte gasto_transporte pago_transporte','carga coordinacion_entrega empresa_transporte_externo vehiculo_externo chofer_transporte_externo acuerdo_transporte adelanto_transporte aplicacion_adelanto')
S(51,'','acuerdo_transporte empresa_transporte_externo campana adelanto_transporte aplicacion_adelanto liquidacion_transporte pago_transporte gasto_transporte')
S(52,'campana','cliente_negocio_campana contrato_venta entrega_programada coordinacion_entrega historial_chofer cosecha carga recepcion_planta factura_venta cobro_venta liquidacion_proveedor pago_proveedor liquidacion_transporte pago_transporte acuerdo_transporte adelanto_transporte aplicacion_adelanto certificado_campana pago_certificado_campana')
S(53,'','usuario chofer_transporte_externo empresa_transporte_externo coordinacion_entrega entrega_programada contrato_venta cliente_negocio_campana campana')
S(54,'','chofer_transporte_externo coordinacion_entrega origen_entrega finca proveedor entrega_programada contrato_venta cliente_negocio_campana cliente_negocio vehiculo_externo carga historial_chofer')
S(55,'','origen_entrega finca proveedor coordinacion_entrega')
S(56,'','coordinacion_entrega carga chofer_transporte_externo entrega_programada contrato_venta cliente_negocio_campana cliente_negocio')
S(57,'carga proveedor_carga origen_carga gasto_carga','coordinacion_entrega origen_entrega finca campania_x_proveedores proveedor fruta_derivada entrega_programada','acuerdo_compra')
S(58,'historial_chofer','carga proveedor_carga proveedor fruta_derivada coordinacion_entrega recepcion_planta chofer_transporte_externo')
S(59,'recepcion_planta','carga coordinacion_entrega historial_chofer')
S(60,'recepcion_planta','carga coordinacion_entrega historial_chofer')
S(61,'carga','coordinacion_entrega historial_chofer')
S(62,'historial_chofer','recepcion_planta carga coordinacion_entrega chofer_transporte_externo')

# Las tres tablas de transporte existentes no se presentan como otro flujo nuevo en el padrón.
# Se conservan visibles como compatibilidad, para decidir cómo integrar el modelo del backend.
specs[25]['H']=['trazabilidad_transporte','chofer_vehiculo_externo','detalle_trazabilidad']
assert set(specs)==set(range(1,63))
for i,v in enumerate(views,1):
    v['roles']={t:role for role,ts in specs[i].items() for t in ts if t in T}
    v['tables']=list(v['roles'])
assert {n for v in views for n in v['tables']}==set(T)

# Función de cada tabla compartida. El uso concreto (escritura, consulta o discusión)
# se declara por vista y no se deduce de que una tabla aparezca como padre de una FK.
purpose={
'persona':'Identifica a una persona natural para cuentas o destinatarios de compras; su reutilización no crea otro proveedor ni autoriza por sí sola a cobrar.',
'rol':'Distingue permisos de Administrador y Chofer; las autorizaciones se comprobarán en el servidor.',
'usuario':'Relaciona la cuenta autenticada con la identidad y, cuando corresponde, con el chofer. El selector del demo todavía no constituye autenticación.',
'sesion_usuario':'Propuesta técnica para mantener acceso y vencimiento; no se ha decidido si se usará sesión propia o un proveedor de autenticación.',
'campana':'Identifica la campaña, sus fechas, fruta, responsable y estado; aporta el ámbito de todas las consultas de la vista.',
'fruta':'Proporciona el catálogo de cultivos y la fruta de la campaña. No representa kilos comprados ni cosechados.',
'fruta_derivada':'Identifica una variedad y su fruta. Permite mostrar el cultivo de la finca sin duplicar fruta_id en finca.',
'campana_x_fruta_derivada':'Conserva las variedades seleccionadas para la campaña, distintas de las variedades efectivamente cargadas.',
'proveedor':'Mantiene el padrón comercial y datos generales de la persona o entidad proveedora, compartidos entre campañas.',
'proveedor_x_fruta':'Asocia las frutas del padrón al proveedor; se conserva mientras no se apruebe derivarlas exclusivamente de sus fincas.',
'proveedor_x_fruta_derivada':'Propuesta para las variedades del padrón del proveedor. No identifica la finca física de recojo.',
'proveedor_x_persona':'Vincula al proveedor con personas principal/vinculadas que pueden figurar como destinatarias; no reparte ni transfiere compras históricas.',
'finca':'Conserva ubicación, coordenadas, hectáreas y una variedad por finca en este alcance. Su fruta se obtiene por fruta_derivada; no tiene FK directa a participación.',
'campania_x_proveedores':'Es la participación del proveedor en una campaña y el punto de agrupación de entrevistas, evaluación y cantidades. Se conserva obligatoriamente y no selecciona finca.',
'entrevista_extencion':'Añade los datos agronómicos de la visita a una finca del proveedor en esa campaña. Las fincas entrevistadas se obtienen de estas filas, sin otra vinculación directa finca–participación.',
'examen_proveedor':'Registra muestras y exámenes de evaluación del proveedor, con contexto de campaña propuesto. No sustituye los análisis operativos de Calidad.',
'certificado_proveedor':'Conserva certificados propios del proveedor y revisión SENASA, separados de la cobertura de campaña; su relación documental está pendiente.',
'participacion_proveedor_campana':'Cabecera adicional propuesta por el diseño anterior que se solapa con campania_x_proveedores. No se debe poblar como segunda participación hasta definir una función diferente.',
'participacion_proveedor_x_fruta_derivada':'Selección propuesta de variedades por participación. Su FK a la cabecera adicional deberá revisarse si se consolida el diseño en campania_x_proveedores.',
'acuerdo_compra':'Propuesta para condiciones de precio y vigencia por proveedor/variedad. No se observó un editor propio de acuerdos en entrevistas; el precio aplicado existe al liquidar.',
'certificado_campana':'Guarda el certificado de campaña, vigencia y costo. No guarda como pago el recibo ni reemplaza el certificado propio del proveedor.',
'norma':'Catálogo de normas que se referencian desde certificación y guías; evita duplicar nombres libres en cada documento.',
'certificado_campana_x_proveedor':'Distribuye la cobertura inicial del certificado entre productores de esa campaña. Su dependencia de la cabecera adicional de participación sigue por afinar.',
'ampliacion_certificado_campana':'Registra cada aumento de kilos certificados como evento, sin sobrescribir el volumen inicial.',
'pago_certificado_campana':'Registra desembolsos parciales del certificado en su moneda. El saldo se calcula con los pagos y no por una etiqueta de estado.',
'cliente_negocio':'Mantiene cliente, tipo Exportador/Industria y contacto. Un cliente comercial no es automáticamente empresa transportista aunque compartan nombre.',
'cliente_negocio_campana':'Representa el vínculo y requerimiento del cliente en la campaña, previo a sus contratos. El backend mantiene un vínculo único por cliente/campaña.',
'cliente_negocio_campana_x_fruta_derivada':'Conserva la selección múltiple de variedades solicitadas en el requerimiento comercial.',
'contrato_venta':'Representa cada contrato del cliente/campaña con kilos, precio y moneda propios. Contratado no equivale a programado ni facturado.',
'entrega_programada':'Guarda fecha, kilos y destino previstos de un contrato antes de completar transporte o registrar carga física.',
'entrega_x_fruta_derivada':'Desglosa los kilos programados por variedad para el calendario semanal; no es una segunda entrega.',
'empresa_transporte_externo':'Es el proveedor logístico contratado, empresa o independiente previsto. No representa a la agroexportadora que opera el sistema.',
'vehiculo_externo':'Identifica la unidad y su empresa, placa, dimensiones y pesos. Los datos se consultan al asignar y se capturan históricamente en documentos.',
'chofer_transporte_externo':'Mantiene conductor, contacto y empresa. El vínculo opcional a usuario permitirá filtrar las asignaciones de quien inicia sesión.',
'chofer_vehiculo_externo':'Conserva las asignaciones actuales del backend con chofer, unidad, trazabilidad y fechas; integrar su autoridad con coordinacion_entrega requiere una decisión.',
'trazabilidad_transporte':'Conserva el transporte actual por participación de proveedor. No equivale directamente al viaje multiproveedor del mockup.',
'detalle_trazabilidad':'Conserva costos, guía URL y SCTR del transporte actual; no duplicar automáticamente esos costos como gasto_carga o gasto_transporte.',
'solicitud_transporte':'Guarda el requerimiento común de servicio, campaña, ruta, ventana y condiciones antes de recibir respuestas.',
'invitacion_transporte':'Identifica cada transportista destinatario de una solicitud, preservando el contacto usado. No supone que se haya enviado un correo real.',
'cotizacion_transporte':'Propuesta para cada respuesta económica de un invitado; la lista actual está vacía y el formulario de respuesta no pudo contrastarse.',
'acuerdo_transporte':'Representa vinculación de transportista/campaña y condiciones comerciales. Debe definirse si puede existir como borrador antes de registrar el acuerdo.',
'adelanto_transporte':'Registra el dinero efectivamente entregado por adelantado; el monto prometido en el acuerdo no acredita desembolso.',
'aplicacion_adelanto':'Imputa parte de un adelanto existente a una liquidación. No registra un segundo pago ni otro dinero entregado.',
'coordinacion_entrega':'Selecciona transportista, unidad, chofer y fechas para una entrega programada. Puede existir antes de la carga real.',
'origen_entrega':'Selecciona cada finca de los proveedores de la entrega. finca_id identifica el punto físico; cxp_id acredita la participación en campaña.',
'cosecha':'Representa la operación agrícola, sus estimados, cantidades y estado propios. No debe crearse artificialmente solo para permitir un análisis previo.',
'analisis_calidad':'Registra muestreo por campaña/proveedor/finca antes de la cosecha; cosecha_id es opcional por decisión aprobada. Conserva resultado y unidad cuando lleguen.',
'medicion_mtd':'Conserva mediciones históricas por participación y finca, su valor y límite aplicado. La evidencia queda pendiente de relación documental.',
'carga':'Representa la carga física de una coordinación, fecha y responsable. El peso real se obtiene de sus líneas de proveedores y se diferencia del programado.',
'proveedor_carga':'Desglosa kilos reales, variedad, bultos y precio aplicado por proveedor. No distribuye automáticamente kilos entre las fincas de ese proveedor.',
'origen_carga':'Conserva las fincas que aportaron a una línea de proveedor de la carga; los kilos por finca pueden quedar sin medir.',
'gasto_carga':'Desglosa costos como cuadrilla o anotadores de esa carga. No equivale al flete ni a los desembolsos de transporte.',
'guia_remision':'Representa el documento estructurado del traslado, con datos históricos de partida, llegada, transportista y conductor. Permanece aunque archivo se difiera.',
'proveedor_guia':'Asigna kilos de las líneas de proveedor de la carga a cada guía; permite varias guías sin duplicar kilos.',
'guia_x_norma':'Guarda las normas seleccionadas para una guía, reutilizando el catálogo norma.',
'historial_chofer':'Registra cada evento En carga, Salida, En camino, Llegada o Cierre con fecha y responsable. El estado resumido se consulta desde el último evento.',
'recepcion_planta':'Mantiene una recepción por carga, peso de planta, descarte y cierres previstos. Recepción y descarte son pasos distintos sobre la misma fila.',
'liquidacion_proveedor':'Guarda el documento de compra por carga/proveedor y la persona destinataria, con importes históricos. Liquidar no significa pagar.',
'pago_proveedor':'Registra cada desembolso parcial o total de una liquidación de compra. Sus sumas determinan el saldo.',
'parametro_uit':'Guarda los parámetros del control anual como configuración a revisar; los valores del mockup no se toman como norma tributaria verificada.',
'liquidacion_transporte':'Guarda el documento del servicio por carga, flete y moneda. No debe crear un pago solo por elegir modalidad completa.',
'gasto_transporte':'Registra viáticos y gastos reales del transporte que se incluirán una sola vez en su liquidación.',
'pago_transporte':'Registra desembolsos de una liquidación de transporte, separados de adelantos y sus aplicaciones.',
'factura_venta':'Guarda la preparación y registro de la factura externa por carga, con kilos facturados, precio y moneda. No implica emisión fiscal desde la app.',
'cobro_venta':'Registra uno o varios ingresos contra una factura, en la moneda de esta. Los cobros no alteran el peso recibido.'}
purpose={t:description for t,description in purpose.items() if t in T}
for t in ['campania_x_proveedores','norma','guia_x_norma','rol','parametro_uit']:
    purpose[t]=T[t]['description']
assert set(purpose)==set(T)

navigation={
1:'Seleccionar Administrador → Entrar como administrador → Módulos; seleccionar Chofer → elegir usuario → Mis campañas.',
2:'Cada una de las ocho tarjetas abre su módulo; Volver a módulos permite cambiar de flujo.',
3:'Gestión Comercial → Clientes → Ver cliente, Editar o Vincular a campaña; Contratos cambia al listado de participaciones.',
4:'Clientes → Ver cliente SUTRIMEX → Participaciones por campaña → Abrir participación.',
5:'Gestión Comercial → Contratos → Ver/Editar participación; Más opciones → Contratos o Entregas.',
6:'Ver participación o Abrir participación → consulta cliente–campaña → Volver al origen.',
7:'Contratos → Más opciones de SUTRIMEX → Contratos → Registrar/Editar contrato o Entregas.',
8:'Contrato → Entregas → Registrar/Ver entrega; completar transporte corresponde a Campaña en proceso.',
9:'Módulos → Gestión de Campaña → Planificado / En Proceso / Finalizado → Detalle o Más opciones.',
10:'En Proceso → Ver detalle de Mango 2026 → Datos generales; Revisar cierre abre su control separado.',
11:'Planificado → Más opciones de Palta 2027 → Proveedores → Ver participación; Más opciones del proveedor → Entrevista / Exámenes.',
12:'Proveedores de campaña → Más opciones de Roberto Palacios → Entrevista → Fincas entrevistadas → Ver finca o Registrar entrevista.',
13:'Proveedores de campaña → Más opciones del proveedor → Exámenes → Registrar examen.',
14:'Planificado → Más opciones de campaña → Certificaciones → Editar certificado / Ampliación / Registrar pago.',
15:'Certificaciones → + Ampliación → modal; Cancelar vuelve sin registrar evento.',
16:'Certificaciones → Registrar pago → modal; Cancelar vuelve sin registrar desembolso.',
17:'En Proceso → Más opciones de Mango 2026 → Transportistas → Vincular; Más opciones de empresa → Acuerdo de pago.',
18:'En Proceso → Más opciones → Entregas → Completar entrega, Editar coordinación o Ver entrega según preparación.',
19:'Entregas → Completar entrega → Completar coordinación → elegir transportista, chofer, unidad y orígenes.',
20:'Campaña → Más opciones → Programa semanal de entregas → semana/variedad → cantidad diaria abre su composición.',
21:'Módulos → Gestión de Proveedores → Ver/Editar proveedor; Más opciones → Fincas o Certificados.',
22:'Gestión de Proveedores → Ver proveedor → Datos generales, frutas y variedades → Volver a proveedores.',
23:'Proveedor → Más opciones → Fincas → Registrar / Ver / Editar finca.',
24:'Proveedor → Más opciones → Certificados → Registrar / Ver / Editar certificado propio.',
25:'Módulos → Gestión de Transporte → Ver empresa; selección de empresas → Solicitar cotización.',
26:'Ver empresa SUTRIMEX → Ver vehículos / Ver choferes / Nuevo vehículo / Nuevo chofer / Editar transportista.',
27:'Ficha del transportista → Ver vehículos → listado filtrado por empresa → Ver/Editar unidad.',
28:'Ficha del transportista → Ver choferes → listado filtrado por empresa → Ver/Editar conductor.',
29:'Gestión de Transporte → Requerimientos y cotizaciones → Nueva solicitud. El listado estaba vacío.',
30:'Padrón → seleccionar transportistas → Solicitar cotización → formulario → Revisar solicitud. No se ejecutó envío.',
31:'Módulos → Cosecha y Control de Calidad → Exportador/Industria → Ver campaña o menú de opciones.',
32:'Calidad → Ver campaña Mango 2026 → resumen de estado y fechas → Volver a campañas.',
33:'Calidad → Opciones de campaña → Análisis y revisión → Registrar análisis o Completar/editar.',
34:'Calidad → Opciones → Carga / Cargas por entrega → Registrar carga, Ver carga o Editar datos.',
35:'Cargas por entrega → Ver carga 2 → operación EXP-MAN-002 → entrega, controles, MTD y documentos.',
36:'Calidad → Opciones → Guías de remisión → fila de carga → Preparar guía o Ver detalle.',
37:'Preparar guía → Guías de la carga → Completar datos → formulario de traslado, proveedores, conductor, partida, llegada y normas.',
38:'Módulos → Logística y Despacho → Ingresar a cargas de una campaña.',
39:'Campaña de Logística → filtrar estado → Ver entrega por código.',
40:'Cargas de Logística → Ver entrega DEMO-FACTURAR-001 → historial, viaje, carga, checklist y recepción en consulta.',
41:'Módulos → Facturación y cobros → campaña → Ver clientes.',
42:'Campaña → clientes con cargas → Facturar → cargas registradas del cliente.',
43:'Cliente → desplegar Carga 5 DEMO-FACTURAR-001 → Ver factura, Registrar cobro o Historial de cobros.',
44:'Carga facturada → Historial de cobros → movimientos y saldos → Registrar cobro.',
45:'Módulos → Liquidación de Compra → campaña → Ver cargas; acceso global a proveedores y límites UIT.',
46:'Campaña → Ver cargas → Proveedor o Transportista por cada carga; Control UIT por proveedor.',
47:'Carga → Proveedor → Por liquidar / Por pagar / Pagados → documento e historial de pagos.',
48:'Proveedor → Pagados → Ver LC-000004 → modal de liquidación de compra.',
49:'Liquidación → Control UIT por proveedor → año → personas vinculadas / detalle anual.',
50:'Carga → Transportista → documento LT, Historial de pagos y paneles de acuerdo/saldo.',
51:'Transportista → desplegar Acuerdo de la empresa y saldo de campaña → adelanto, flete liquidado y saldo.',
52:'Detalle de campaña → Revisar cierre → grupos de pendientes y motivo; Confirmar permanecía bloqueado.',
53:'Bienvenido → Chofer Miguel Torres o Elena Ruiz → Mis campañas filtradas por asignación.',
54:'Mis campañas → campaña → tarjetas de Mis cargas, con datos programados y estado del despacho.',
55:'Mis cargas → Ver ubicación y ruta → selector de finca → mapa. No se activó Usar mi ubicación.',
56:'Mis cargas → tarjeta Exportación Por completar → Completar carga → Llenar datos de carga.',
57:'Completar carga → Llenar datos → formulario de peso, variedad, bultos, responsable y gastos por proveedor.',
58:'Mis cargas → tarjeta de Industria con carga real → Mi despacho → pasos, checklist e historial.',
59:'Mi despacho en Llegada → Recepción en planta → modal de peso recibido → Cancelar o Guardar paso.',
60:'Mi despacho → Descarte informado → Sí/No; Sí muestra kilos, porcentaje calculado y evidencia.',
61:'Mi despacho → Guía de salida del vehículo → adjunto y Guardar documento. En el objetivo se difiere archivo.',
62:'Mi despacho → Cerrar despacho, habilitado solo tras requisitos. No se ejecutó una transición de cierre.'}
assert set(navigation)==set(range(1,63))

observations={
1:'Selector de perfil y conductores de demo; se accedió como administrador, Miguel Torres y Elena Ruiz. Los registros se anuncian compartidos entre dispositivos.',
2:'Ocho módulos y botón de cierre de sesión. La aplicación mantiene la URL raíz; los breadcrumbs de este documento son rutas lógicas.',
3:'Padrón con empresa, contacto, teléfono, correo, RUC y tipo Exportador/Industria; acciones Ver, Editar y Vincular.',
4:'SUTRIMEX muestra sus datos generales y participaciones de Mango 2026 y Palta 2027, kilos y número de contratos.',
5:'Listado cliente/campaña con cantidades, kilos acordados y contratos; existen varias filas de Batimix/Mango 2026 en los datos de demostración.',
6:'Consulta SUTRIMEX/Mango 2026 con ficha técnica, variedades, destino Rotterdam, ventana de entrega y resúmenes programados.',
7:'Cuatro contratos de SUTRIMEX/Mango 2026; tres en USD y uno en PEN. Cada contrato accede a sus entregas.',
8:'Contrato con dos entregas de 500 kg, destino y preparación; edición y eliminación deshabilitadas con carga registrada.',
9:'Planificado, En Proceso y Finalizado; campaña pasa por fecha a En proceso según texto visible. La fecha final no ejecuta el cierre.',
10:'Resumen de Mango 2026 con estimados, certificados y comprometidos; advertencias de recepciones incompletas; no equivalen a nuevas tablas.',
11:'Roberto Palacios aparece como productor de Palta 2027. El detalle muestra dos fincas; se confirma con el usuario que serán las fincas entrevistadas.',
12:'Dos fincas entrevistadas, fecha/hora, códigos FYV de la UI y detalle agronómico. El backend conserva codigo FVV; revisar el prefijo antes de cambiar datos.',
13:'Examen por fruta, análisis, muestra, origen, toma/envío, estado, resultado y documento. El registro visible tiene resultado negativo.',
14:'El editor dice un certificado por campaña y muestra productor cubierto, kilos iniciales, ampliaciones y pago. El resumen reconoce cobertura múltiple; no se cambia la unicidad sin decidirlo.',
15:'Modal de kilos adicionales, fecha y referencia/evidencia textual. No se guardó ampliación.',
16:'Modal con costo, pagado, monto, fecha, referencia y evidencia de pago. No se registró desembolso.',
17:'Tres transportistas vinculados; el acuerdo se abre aparte y queda solo lectura cuando ya tiene liquidación.',
18:'Entregas Por completar, Lista para carga o Con carga registrada; el texto diferencia programación comercial y coordinación.',
19:'Formulario con transportista vinculado, varios proveedores/fincas, camión, chofer, fechas, origen, condiciones y observaciones.',
20:'Programa por semana ISO, cliente, contrato, placa y variedad; las cantidades diarias se consultan y pueden existir con placa Por asignar.',
21:'Padrón general con frutas y variedades, sanidad y accesos separados a Fincas y Certificados.',
22:'Ficha de Roberto Palacios con identidad, contacto, ubicación y frutas/variedades. No se observó editor de personas vinculadas en esta ficha.',
23:'Dos fincas con SENASA, ubicación, cultivo/variedad y hectáreas; datos agronómicos gestionados por campaña.',
24:'Certificados propios con nombre, revisión SENASA y documento, separados explícitamente del certificado de campaña.',
25:'Padrón de empresas e independientes; selección múltiple para cotizar. Las tablas actuales de trazabilidad no tienen un editor independiente en esta pantalla.',
26:'Ficha SUTRIMEX con ubicación, MTC y accesos a sus dos vehículos y dos choferes.',
27:'Listado de unidades filtrado por empresa, placa, volumen y pesos; Ver/Editar. No se interpreta peso neto como capacidad útil.',
28:'Listado de Miguel Torres y Rosa Aguilar para SUTRIMEX, con teléfono y correo. Usuario y chofer son conceptos distintos.',
29:'La lista de solicitudes estaba vacía; se inspeccionó el acceso a nueva solicitud. No hay respuesta de cotización observable sin crear datos.',
30:'Formulario de solicitud a empresas seleccionadas con campaña, ruta, ventana, estimado, vehículo, condiciones y fecha límite. El correo se anuncia simulado.',
31:'Campañas de Calidad por canal Exportador/Industria y botón Agregar campaña. La persistencia de esa incorporación requiere decisión propia.',
32:'La ficha consultada muestra estado, inicio y fin; indica consultar los estados de calidad desde las opciones de campaña.',
33:'Análisis por proveedor/finca y fecha, con resultado pendiente permitido; MTD y captura son obligatorios en el mockup. Se aprobó permitir análisis anterior a cosecha.',
34:'Listado de carga por entrega con transportista, placa/chofer, kilos e indicador de calidad. La UI declara una carga por entrega pero repite en1 en datos demo.',
35:'Detalle EXP-MAN-002 con datos programados, finca/orígenes y controles. Hay diferencias entre kilos de lista y detalle: no se resuelven inventando pesos.',
36:'Guías por carga, estado y kilos; la preparación abre el conjunto de guías de esa carga.',
37:'Formulario con kilos, KGM, bultos y secciones de transportista, conductor, partida, llegada y normas. Al abrir preparación apareció fila Por preparar y sincronización; no se guardó ni emitió una guía.',
38:'Tablero por campaña y estados En carga, Salida de finca, En camino, Llegada y Cierre-Completado.',
39:'Listado con código de despacho, cliente/destino, unidad/chofer, kilos, estado y último reporte.',
40:'Consulta de DEMO-FACTURAR-001: 580 kg de origen y 570 kg en planta; el historial y resumen no siempre coinciden en los datos demo.',
41:'Campañas con cargas, incluidas finalizadas; navegación a clientes de cada campaña.',
42:'Resumen facturado/cobrado/saldo y tabla de kilos e importes contratados, que no deben mezclarse con facturación.',
43:'DEMO-FACTURAR-001 muestra 580 kg cargados, 570 recibidos/facturados, USD 1,368 total y USD 500 cobrado.',
44:'Historial de un cobro parcial con fecha, medio, referencia y evidencia. Cambia el saldo, no el contrato ni el peso.',
45:'Listado de campañas con cargas, acceso a pagados y control global UIT.',
46:'Cada carga presenta liquidaciones de proveedores y de transporte por separado.',
47:'Pestañas Por liquidar, Por pagar y Pagados; carga consultada con tres proveedores pagados y documentos propios.',
48:'Modal LC-000004 con proveedor, campaña, fecha, kilos, precio, importe, pagado, saldo y documento adjunto.',
49:'Control por año y persona, principal y vinculadas; incluye todas las campañas y declara que pagos no cambian el acumulado.',
50:'Transporte de la carga con flete, viáticos, total, documento LT y pagos; acuerdo de empresa se consulta en otro panel.',
51:'Panel separa flete autorizado, adelanto entregado sin aplicar, flete liquidado y gastos. Liquidar no registra pago ni aplica adelanto.',
52:'Ocho grupos de pendientes para cerrar; confirmación bloqueada. Revisión visible de despachos, recepción, cosechas, finanzas y certificaciones.',
53:'Miguel Torres ve campañas asignadas en proceso; Elena Ruiz ve una histórica Mango 2025 Cerrada. Filtrado por identidad del conductor.',
54:'Tarjetas distinguen canal, preparación/estado, cliente, varias fincas, destino, unidad y kilos programados.',
55:'Mapa con selector de finca, coordenadas y herramientas de ruta. No se usó ubicación personal ni se observó necesidad de guardar GPS.',
56:'Exportación Por completar abre En carga y Llenar datos; no se crea otra entrega desde este paso.',
57:'Formulario por proveedor con una variedad, kilos y jabas/bines/mallas cargados/vacíos; viáticos y gastos de cuadrilla/anotadores.',
58:'Llegada muestra carga, proveedores, checklist, guía de salida e historial de eventos. La guía adjunta es distinta de la guía de remisión estructurada.',
59:'Modal de peso recibido; texto explícito: la diferencia de peso no se registra como descarte.',
60:'Descarte exige informar Sí/No; Sí muestra kilos y porcentaje calculado sobre origen, más evidencia en la UI.',
61:'Adjunto independiente de salida del vehículo; en el esquema vigente su integración documental sigue pendiente por decisión del usuario.',
62:'Cerrar despacho bloqueado mientras falta recepción; no se ejecutó cierre. La campaña histórica también conserva inconsistencias de checklist, sin rellenarlas.'}
assert set(observations)==set(range(1,63))
for i,v in enumerate(views,1):
    v['observed']=observations[i]
    v['navigation']=navigation[i]
    if i==12:v['rule']='Se conserva entrevista_extencion agrupada por campania_x_proveedores y vinculada a finca. Reutiliza los datos físicos de finca y agrega los datos agronómicos de la visita/campaña. La propiedad de la finca debe coincidir con el proveedor. La UI muestra FYV y el backend conserva FVV; no se renombra el código sin decidirlo.'
    if i==23:v['rule']='Una finca pertenece al proveedor y tendrá una variedad en este alcance; la fruta se obtiene de esa variedad. La asociación propuesta se mantiene opcional para registros históricos incompletos y debe completarse antes de la operación que la requiera. Las hectáreas son datos de finca; la entrevista añade datos de campaña sin duplicar la finca.'
    if i==25:v['rule']='Se conservan empresa_transporte_externo, vehiculo_externo y chofer_transporte_externo. El mockup incluye independientes; el RUC obligatorio del backend todavía necesita adaptación para ese caso. Las tres tablas actuales de trazabilidad se presentan solo como compatibilidad, sin forzar su edición desde este padrón. La coincidencia del nombre del cliente y del transportista no fusiona ambas entidades.'
    if i==33:v['rule']='El usuario aprobó registrar análisis por participación y finca antes de cosecha; cosecha_id queda opcional. La campaña se obtiene desde cxp_id. El MTD conserva historial y límite aplicado por finca/campaña. Si después se vincula una operación, el servicio comprobará que corresponde a la misma campaña y finca. La evidencia exigida por el mockup queda pendiente de integración documental.'
    if i==59:v['rule']='Recepción y descarte se completan sobre una misma recepción por carga. El formulario del chofer solo solicita el peso de planta. Resultado, descarga, reporte y cierres administrativos previstos requieren precisar su acción y responsable en el flujo administrativo; no se presentan como campos observados en este modal. La integración del reporte documental sigue pendiente.'

decisions={
'D01':('Por discutir','Participación adicional','campania_x_proveedores se conserva para agrupar entrevistas del proveedor por campaña. participacion_proveedor_campana sigue en el general como propuesta, pero duplica funciones; no se ha aprobado borrarla ni mantener dos fuentes editables. Revisar también sus tablas de variedades y cobertura.'),
'D02':('Aprobado por el usuario','Fincas entrevistadas','El listado de fincas de una participación se obtiene desde entrevista_extencion. No se vuelve a agregar finca_id a campania_x_proveedores; los orígenes de entrega/carga seleccionan las fincas físicas de recojo.'),
'D03':('Aprobado por el usuario','Análisis antes de cosecha','analisis_calidad identifica cxp_id y finca_id; cosecha_id queda opcional. La campaña se obtiene por la participación, sin otra FK redundante a campaña. El servicio validará coincidencia de campaña y origen si se vincula posteriormente una cosecha.'),
'D04':('Aprobado por el usuario','Una variedad por finca','Se conserva finca.fruta_derivada_id y se obtiene fruta por fruta_derivada.fruta_id. No se agrega una tabla de varios cultivos por finca. El vínculo permanece opcional para datos históricos; completar variedad antes de operar cuando la vista la requiere.'),
'D05':('Por discutir','Autoridad de transporte','chofer_vehiculo_externo/trazabilidad_transporte conservan el modelo actual; coordinacion_entrega prepara el viaje multiproveedor. Definir cuál registra la asignación y cómo se sincroniza el otro; una FK opcional no evita dos fuentes contradictorias.'),
'D06':('Por discutir','Vincular antes del acuerdo','El mockup permite vincular transportista y registrar el acuerdo después. acuerdo_transporte exige condiciones completas en el SQL: evaluar estado borrador con atributos opcionales o un vínculo independiente. No se agrega otra tabla todavía.'),
'D07':('Por discutir','Incorporación de campaña a Calidad','Agregar campaña puede ser habilitación manual por canal o un filtro de las operaciones existentes. Solo si el negocio exige persistir esa habilitación tendría sentido una entidad específica; aún no se añade.'),
'D08':('Confirmado e incorporado al SQL','Destino como texto','Decisión del 29/10/2026: se retira el catálogo sin CRUD propio. La entrega guarda destino textual y la guía sus datos de llegada históricos.'),
'D09':('Por discutir','Cantidad de certificados','El editor dice uno por campaña; el backend y el resumen admiten varios. Se mantiene la capacidad actual hasta decidir si las normas requieren certificados distintos.'),
'D10':('Por discutir','Condiciones de compra','acuerdo_compra permitiría precios por proveedor/variedad/vigencia, pero no tiene editor observado en Entrevista. Decidir si se administra allí o si basta el precio histórico capturado al liquidar.'),
'D11':('Por discutir','Personas y autenticación','persona/proveedor_x_persona justifican destinatarios del control anual; no requieren que todo proveedor sea usuario. sesion_usuario depende de la estrategia de autenticación y no se exige para navegar el demo.'),
'D12':('Pendiente técnico por decidir','Examen pendiente de resultado','El resultado actual de examen_proveedor sigue obligatorio positivo/negativo. El estado adicional no habilita un examen sin resultado; requiere decidir nulabilidad y adaptar DTO/servicio.'),
'D13':('Decisión previa conservada','Gestión documental diferida','archivo no está en el SQL ni en diagramas. Los campos de documentos, comprobantes y evidencias son opcionales y sin FK. El mockup puede exigir archivos, pero esa exigencia no está implementada en el esquema de esta etapa.'),
'D14':('Por discutir','Una carga por entrega','La UI declara una sola carga por entrega, pero en1 aparece repetida en el demo. Se mantiene la unicidad de la propuesta; permitir viajes parciales requeriría definir un viaje independiente y el reparto de kilos antes de cambiarla.'),
'D15':('Por discutir','Un requerimiento por cliente/campaña','El listado demo repite Batimix/Mango 2026, mientras el backend exige un vínculo único cliente/campaña. La propuesta conserva esa unicidad y varios contratos como hijos; confirmar si las filas son duplicados de prueba o requerimientos comerciales independientes.')}
view_decisions={
1:['D11'],3:['D08'],5:['D08'],8:['D08','D14'],10:['D01','D09'],11:['D01','D02'],12:['D02','D04','D10'],13:['D12','D13'],14:['D01','D09','D13'],15:['D09'],16:['D13'],17:['D06'],19:['D02','D05','D06'],21:['D11'],22:['D11'],23:['D04'],24:['D13'],25:['D05'],26:['D05'],27:['D05'],28:['D05','D11'],29:['D13'],30:['D13'],31:['D07'],33:['D03','D04','D13'],34:['D14','D05'],35:['D03','D14'],36:['D14','D13'],37:['D13','D14'],38:['D05'],39:['D05'],40:['D05','D13'],43:['D13'],44:['D13'],47:['D10','D11'],48:['D13'],49:['D11'],50:['D05','D06','D13'],51:['D06'],52:['D13','D14'],53:['D05','D11'],54:['D02','D05'],55:['D02','D04'],56:['D14'],57:['D02','D04','D10','D14'],58:['D05','D13'],59:['D13'],60:['D13'],61:['D13'],62:['D13']}
for i in [5,6,7]:view_decisions.setdefault(i,[]).append('D15')
usage={
(1,'usuario'):'Identificar al usuario en la futura autenticación; el selector actual permite entrar sin credenciales y no prueba que se persista una cuenta.',
(10,'campania_x_proveedores'):'Consultar oferta y evaluación desde la única participación campania_x_proveedores, sin duplicar cantidades.',
(11,'campania_x_proveedores'):'Crear o actualizar la participación del proveedor, su tipo, cantidad y evaluación en la campaña; es el identificador usado para agrupar sus entrevistas.',
(11,'entrevista_extencion'):'Consultar las entrevistas de la participación y obtener sus fincas distintas para el detalle «Fincas vinculadas a la campaña», según decisión confirmada.',
(11,'finca'):'Leer las fincas alcanzadas a través de entrevistas; no es una asociación directa de finca con la participación.',
(12,'finca'):'Reutilizar una finca existente del proveedor o registrar una nueva desde la entrevista, separando datos físicos del registro agronómico de campaña.',
(12,'entrevista_extencion'):'Guardar una visita por finca y participación, fecha/hora y datos agronómicos; el código identifica la entrevista, no una nueva finca.',
(13,'campania_x_proveedores'):'Aportar el contexto de campaña/proveedor del examen; validar que el proveedor del examen coincide con el de la participación.',
(14,'certificado_campana_x_proveedor'):'Guardar productores cubiertos y kilos iniciales por certificado. La selección debe corresponder a la campaña; su FK a la cabecera adicional sigue por afinar.',
(17,'acuerdo_transporte'):'La intención de esta vista es vincular al transportista y registrar sus condiciones aparte. La fila actual propuesta necesita un estado borrador o un rediseño para representar el intervalo sin acuerdo.',
(19,'origen_entrega'):'Guardar una fila por finca seleccionada de cada proveedor participante; comprobar pertenencia de finca al proveedor y, cuando se exija, entrevista en esa campaña.',
(20,'entrega_x_fruta_derivada'):'Consultar cantidades programadas por variedad para cada día de la semana; las sumas del calendario se calculan sin otra tabla semanal.',
(25,'trazabilidad_transporte'):'Solo compatibilidad: conservar los registros actuales por proveedor/campaña. No se edita un viaje paralelo desde el listado de transportistas.',
(25,'chofer_vehiculo_externo'):'Solo compatibilidad: conservar asignaciones y restricciones existentes. Su papel frente a coordinacion_entrega debe decidirse antes de generar nuevas asignaciones.',
(25,'detalle_trazabilidad'):'Solo compatibilidad: conservar guía URL, SCTR y costos históricos; no copiar esos importes como gastos nuevos por mostrar esta vista.',
(31,'campana'):'Leer campañas para incorporarlas o consultarlas en Calidad. No se crea otra campaña; la persistencia de «Agregar campaña» y su canal sigue en discusión.',
(32,'cosecha'):'Consulta prevista desde las opciones de campaña. La ficha resumen visitada solo muestra estado y fechas; no exige una tabla de resumen ni crea operaciones.',
(33,'analisis_calidad'):'Crear el análisis previo por participación y finca, permitiendo resultado pendiente. Vincular cosecha solo cuando exista y pertenezca al mismo contexto.',
(33,'medicion_mtd'):'Registrar el valor de la finca y conservar historial. La captura que exige el mockup queda pendiente de integración documental en este esquema.',
(33,'cosecha'):'Consultar o vincular opcionalmente una operación posterior; ya no es requisito para registrar el muestreo inicial.',
(34,'carga'):'Registrar o editar datos propios de la carga real, respetando una por coordinación en el SQL propuesto. No copiar el viaje desde la campaña como si fuera otra asignación.',
(35,'medicion_mtd'):'Consultar historial por finca y campaña de la operación; el demo muestra también fincas externas al detalle, por lo que el filtro deberá revisarse.',
(37,'guia_remision'):'Guardar el borrador estructurado y los datos históricos de traslado; definir una partida física y no convertir una cadena de fincas en dirección válida.',
(37,'proveedor_guia'):'Seleccionar proveedores de la misma carga y distribuir kilos pendientes entre guías; requiere validación transaccional de acumulados.',
(40,'recepcion_planta'):'Consultar peso recibido y descarte de la misma carga, sin inferirlos de una factura. No se observó un editor administrativo en la pantalla visitada.',
(43,'factura_venta'):'Preparar y después registrar factura externa de la carga, usando peso recibido y precio aplicado. El adjunto se difiere, aunque el mockup lo solicite.',
(48,'liquidacion_proveedor'):'Mostrar el documento ya existente y su persona, peso e importe históricos; abrir el modal no crea una segunda liquidación.',
(49,'liquidacion_proveedor'):'Sumar documentos por persona y año entre campañas. Los pagos se excluyen de la base del acumulado.',
(50,'pago_transporte'):'Registrar dinero entregado contra la liquidación solo en la acción de pago; ni abrir el documento ni liquidar crea el desembolso.',
(51,'adelanto_transporte'):'Consultar dinero entregado y saldo sin aplicar; mantenerlo separado del monto de adelanto pactado en el acuerdo.',
(52,'campana'):'Actualizar cierre, responsable y motivo únicamente tras validar los pendientes de sus registros relacionados; no registrar pagos ni modificar pesos al cerrar.',
(53,'coordinacion_entrega'):'Consultar las entregas asignadas al chofer autenticado y obtener sus campañas por entrega/contrato/participación comercial; no crear otra tabla chofer_campaña.',
(55,'finca'):'Leer coordenadas del punto seleccionado. El cálculo de ruta no implica persistir GPS personal ni crear una tabla de seguimiento.',
(57,'proveedor_carga'):'Guardar kilos, variedad y bultos por proveedor. No repartir kilos entre fincas por igual ni deducir precio de compra del precio de venta.',
(57,'origen_carga'):'Conservar las fincas elegidas como origen real de cada proveedor; kilos_origen puede quedar sin medición, sin perder el punto de recojo.',
(58,'historial_chofer'):'Agregar eventos al avanzar el despacho. La identidad del chofer debe autorizar cada evento y no venir libremente del formulario.',
(59,'recepcion_planta'):'Crear o completar la misma recepción de la carga con el peso en planta; no obliga a duplicar la recepción para informar después el descarte.',
(60,'recepcion_planta'):'Actualizar hubo_descarte y descarte_kg en la misma recepción. No informado, sin descarte y con descarte son estados distintos; el porcentaje se calcula.',
(61,'carga'):'Reservar referencia y fecha de la guía de salida, con relación documental pendiente. No confundir este adjunto con una fila de guia_remision ni exigir un identificador inventado.',
(62,'historial_chofer'):'Registrar el evento CIERRE tras validar checklist y condiciones que finalmente se acuerden para adjuntos pendientes; no cerrar la campaña completa desde el teléfono.'}

def nullable(t,cols):return any('NOT NULL' not in next(c['definition'] for c in T[t]['columns'] if c['name']==n) and n!=T[t]['pk'] for n in cols)
def unique_keys(t):
    keys=[{T[t]['pk']}]
    for con in T[t]['constraints']:
        m=re.match(r'UNIQUE \(([^)]+)\)',con['definition'])
        if m:keys.append({x.strip().strip('"') for x in m.group(1).split(',')})
    for ix in T[t]['indexes']:
        if 'UNIQUE INDEX' in ix and ' WHERE ' not in ix:
            m=re.search(r'\(([^)]+)\)',ix)
            if m:keys.append({x.strip().strip('"') for x in m.group(1).split(',')})
    return keys
def diagram(scope,internal=False):
    groups={}
    for f in F:
        if f['child'] not in scope or (internal and f['parent'] not in scope):continue
        groups.setdefault((f['parent'],f['child']),[]).append(f)
    lines=['```mermaid','erDiagram'];connected=set()
    for (parent,child),fs in groups.items():
        left='o|' if all(nullable(child,f['cols']) for f in fs) else '||'
        one=any(any(k<=set(f['cols']) for k in unique_keys(child)) for f in fs)
        label='actual' if all(f['status']=='ACTUAL' for f in fs) else 'propuesta'
        lines.append(f'    {parent} {left}..{"o|" if one else "o{"} {child} : {label}');connected.update([parent,child])
    lines += ['    '+t for t in scope if t not in connected]
    return lines+['```','']
def tablegroups(scope):
    actual=[t for t in scope if T[t]['existing']];new=[t for t in scope if not T[t]['existing']]
    out=[]
    if actual:out+=['**Tablas actuales que se conservan:** '+', '.join('`'+t+'`' for t in actual)+'.','']
    if new:out+=['**Tablas propuestas para revisar:** '+', '.join('`'+t+'`' for t in new)+'.','']
    return out

from cumplimiento_documentacion import ajustar,introduccion,cierre
views,decisions=ajustar(views,decisions)
intro=introduccion(M,results)
detail=[intro,'## Columnas adicionales en tablas actuales','','| Tabla actual | Atributos para agregar | Para qué se añaden |','|---|---|---|']
for t,table in T.items():
    if not table['existing']:continue
    extra=[c for c in table['columns'] if c['status']=='AGREGAR']
    detail.append('| `'+t+'` | '+(', '.join('`'+c['name']+'`' for c in extra) if extra else 'Ninguno en esta revisión')+' | '+('Consultar la finalidad de cada columna en su diccionario por vista.' if extra else 'Se conserva el catálogo o asociación actual.')+' |')
detail+=['']
general=['# Tablas y relaciones por vista — modelo revisado','',
'**Schema actualizado para cumplimiento — 29/10/2026.** Se incorporan JSONB de formularios y cambios de tipo/nulabilidad; el diccionario vigente distingue MODIFICAR de AGREGAR. Se permiten varios requerimientos cliente/campaña y varias facturas por carga según respuesta del usuario. Los diagramas reflejan las FK y unicidades actuales del SQL objetivo, incluido el vínculo directo persona–liquidación. No se modificó una base existente.','',
'[Diccionario con atributos actuales y adicionales](01_reporte_especifico.md) · [SQL de revisión](03_schema_total.sql). Se incluyen 19 tablas actuales y 41 propuestas: 60 en total. Participación consolidada y catálogos con datos iniciales SQL. archivo queda fuera del esquema, con sus relaciones pendientes. No se modificó la base desplegada.','',
'Los nombres de las tablas actuales coinciden con las entidades TypeORM. Este documento no incluye atributos. Las tablas propuestas complementan el flujo; no sustituyen por nombre a las tablas actuales de transporte.','']
legend='**Mermaid:** `||` = exactamente uno; `o|` = cero o uno; `o{` = cero o muchos. Cada caja es una tabla del esquema general. Las líneas son FK del SQL revisado: actual indica relación ya programada y propuesta indica una relación del diseño revisado, sin afirmar aprobación definitiva ni despliegue. Las FK compuestas del mismo par se agrupan. Una tabla aislada se consulta o participa en una decisión de diseño, sin FK directa en ese recorte. No se dibujan relaciones de navegación como si fueran FK.'
overview=['campana','proveedor','finca','campania_x_proveedores','entrevista_extencion','cliente_negocio','cliente_negocio_campana','contrato_venta','entrega_programada','coordinacion_entrega','carga','proveedor_carga','recepcion_planta','trazabilidad_transporte','chofer_vehiculo_externo','detalle_trazabilidad','factura_venta','liquidacion_proveedor','liquidacion_transporte']
overview += ['empresa_transporte_externo','chofer_transporte_externo','vehiculo_externo','acuerdo_transporte']
overview += ['fruta','fruta_derivada','proveedor_x_fruta','certificado_proveedor','examen_proveedor','certificado_campana','certificado_campana_x_proveedor','norma','archivo','ampliacion_certificado_campana','pago_certificado_campana']
overview += ['participacion_proveedor_campana']
overview=[t for t in overview if t in T]
# El mapa general debe contener todo el modelo; los recortes por vista se explican debajo.
overview=list(T)
image_note='**Entidades amarillas de las referencias incorporadas al mapa:** `fruta`, `fruta_derivada`, `proveedor_x_fruta`, `certificado_proveedor`, `examen_proveedor` y `certificado_campana`. Los rótulos históricos `Certificados` y `certificados_campana` se representan con `certificado_campana` para el certificado de campaña; `certificado_x_productor` se corresponde con la cobertura propuesta `certificado_campana_x_proveedor`, vinculada a proveedor y campaña. Esta equivalencia expresa su función; no afirma que todos los atributos del dibujo sean idénticos. `certificado_proveedor` permanece separado para documentos propios del proveedor. No se añade otra tabla genérica Certificados sin definir un ciclo de vida distinto. `proveedor_x_fruta` se conserva: la nota de la imagen que plantea trasladarlo a finca dice CONFIRMAR y no constituye una decisión aprobada. Las hectáreas están en `finca` (`ha_total_finca`, `ha_cultivo`) en el diccionario específico.'
transport_note='**Gestión de empresas logísticas, choferes y unidades:** `empresa_transporte_externo` registra al proveedor logístico externo contratado por la agroexportadora; `chofer_transporte_externo` y `vehiculo_externo` registran sus choferes y unidades. `chofer_vehiculo_externo` asigna un chofer y una unidad a `trazabilidad_transporte`, con fechas de inicio y fin. Estas cuatro tablas ya existen y se conservan en el SQL. `acuerdo_transporte` es la tabla propuesta para vincular la empresa transportista con la campaña y sus condiciones comerciales. La empresa agroexportadora que opera el sistema no se representa con `empresa_transporte_externo`; este modelo todavía no define una entidad propia para gestionar varias agroexportadoras.'
for doc in [detail,general]:doc += [legend,'','**Mapa de integración:** las tablas actuales se conservan junto al flujo adicional propuesto, incluyendo empresas transportistas, choferes, unidades y sus asignaciones.','']+diagram(overview,True)+[transport_note,'']
for doc in [detail,general]:doc += [image_note,'', '**Trazabilidad de finca tras el cambio:** origen_entrega, origen_carga, analisis_calidad y medicion_mtd ahora identifican finca directamente; antes la obtenían de la participación. El servicio deberá comprobar que esa finca pertenece al proveedor de cxp_id. Los orígenes admiten varias fincas de un proveedor en la misma entrega o carga. El precio simple queda en campania_x_proveedores; no existe una cabecera adicional de acuerdo_compra.', '','**Decisión de negocio — 27/10/2026:** se elimina el vínculo directo finca–campania_x_proveedores del modelo objetivo. Se mantiene proveedor–finca y la entrevista relaciona campaña/proveedor con la finca visitada. El código actual todavía contiene el vínculo retirado; estos documentos y el SQL son la propuesta para revisión.','']
for doc in [detail,general]:doc += ['**Relaciones documentales pendientes:** archivo queda excluida del SQL y de todos los diagramas. Las referencias de documentos, comprobantes, guías y evidencias se definirán en otra etapa. Las columnas reservadas quedan opcionales, sin FK ni obligación de asignarles un identificador. Las URL actuales se conservan.','']
detail += ['**Inventario de relaciones pendientes a archivo (sin implementar):**','','| Tabla | Referencia reservada opcional, sin FK |','|---|---|']
for f in M['pending_file_relations']:detail += ['| `'+f['child']+'` | '+', '.join('`'+n+'`' for n in f['cols'])+' |']
detail += ['']
for doc in [detail,general]:
    doc += ['**Decisiones para afinar el modelo durante el desarrollo:**','','| Referencia | Estado | Tema | Alcance |','|---|---|---|---|']
    for key,(status,title,body) in decisions.items():doc += [f'| {key} | {status} | {title} | {body} |']
    doc += ['','**Recorrido entre módulos:** Comercial programa la entrega; Campaña coordina transporte y fincas; Calidad registra análisis y carga; el Chofer reporta eventos y recepción; Logística consulta el seguimiento; Facturación registra venta y cobros; Liquidación registra compras, transporte y pagos. Volver a módulos cambia de navegación, sin crear otro registro de negocio.','']
    doc += ['**Mapa del flujo funcional:** estas flechas indican navegación o información compartida; no son claves foráneas.','','```mermaid','flowchart LR',
    '    acceso["Selección de perfil"] --> inicio["Administrador: módulos"]',
    '    acceso --> jornada["Chofer: Mis campañas y Mis cargas"]',
    '    inicio --> comercial["Gestión Comercial"]',
    '    inicio --> campanas["Gestión de Campaña"]',
    '    inicio --> proveedores["Gestión de Proveedores"]',
    '    inicio --> transporte["Gestión de Transporte"]',
    '    inicio --> calidad["Cosecha y Calidad"]',
    '    inicio --> logistica["Logística y Despacho"]',
    '    inicio --> ventas["Facturación y cobros"]',
    '    inicio --> compras["Liquidación de Compra"]',
    '    comercial -->|"Entregas programadas"| campanas',
    '    proveedores -->|"Proveedor y fincas"| campanas',
    '    transporte -->|"Empresa, unidad y chofer"| campanas',
    '    campanas -->|"Entrevistas y orígenes"| calidad',
    '    campanas -->|"Entregas asignadas"| jornada',
    '    calidad -->|"Carga real y guías"| logistica',
    '    jornada -->|"Carga, eventos y recepción"| logistica',
    '    logistica -->|"Recepción"| ventas',
    '    calidad -->|"Detalle real de carga"| compras',
    '    ventas --> revision["Revisión de cierre de campaña"]',
    '    compras --> revision',
    '    logistica --> revision','```','']
seen=set()
for i,v in enumerate(views,1):
    head=f'## {v["name"]} ({v["path"]})'
    detail += [head,'',f'**Referencia de revisión:** V{i:02d} · Recorrido del 27/10/2026.','', '**Entrada, acciones y salida:** '+v['navigation'],'', '**Observado en la aplicación de referencia:** '+v['observed'],'','**Criterio para revisar el modelo:** '+v['rule'],'']
    general += [head,'',f'**Referencia:** V{i:02d}. **Navegación:** '+v['navigation'],'']
    scope=list(dict.fromkeys(v['tables']))
    if not scope:
        for doc in [detail,general]:doc += ['Es navegación de módulos; no requiere una tabla de negocio propia.','']
        continue
    # Solo se dibujan tablas cuyo papel se declara en esta vista: no se agregan padres invisibles.
    labels={'E':'Escritura esperada','C':'Consulta','D':'Por discutir','H':'Compatibilidad actual'}
    detail += ['**Funcionalidad esperada de cada tabla en esta vista:**','','| Tabla | Uso en esta vista | Funcionalidad esperada | Situación |','|---|---|---|---|']
    for t in scope:
        role=v['roles'][t]
        state='Tabla actual incluida' if T[t]['existing'] else 'Tabla propuesta, sin implementar'
        if role=='D':state+='; permanencia o diseño por discutir'
        detail += [f'| [`{t}`](#tabla-{t}) | {labels[role]} | {usage.get((i,t),purpose[t])} | {state} |']
    detail += ['','**Esquema de relaciones utilizado por esta vista:**','']
    for doc in [detail,general]:doc += tablegroups(scope)+diagram(scope,True)
    for key in view_decisions.get(i,[]):
        status,title,body=decisions[key]
        for doc in [detail,general]:doc += [f'**{key} — {title} ({status}):** {body}','']
    general += ['**Función de las tablas:** consultar la ficha '+f'V{i:02d}'+' del [reporte específico](01_reporte_especifico.md); este documento conserva nombres, relaciones y decisiones, sin repetir atributos.','']
    if v['name']=='Gestión de transporte':
        detail += [transport_note,'','**Reglas para revisar antes de implementar:** la asignación conserva las fechas y la restricción actual que impide solapamientos del mismo chofer. Las FK por separado no garantizan que el chofer y la unidad pertenezcan a la misma empresa, ni impiden por sí solas que una unidad tenga asignaciones simultáneas. Validar esas reglas en el servicio y definir si se permiten unidades o conductores de otra empresa. El vínculo opcional a coordinacion_entrega integra el flujo propuesto sin sustituir la trazabilidad actual.','']
    for t in scope:
        if t in seen:
            detail+=['**`'+t+'`:** reutiliza su diccionario anterior; no crea una tabla duplicada.',''];continue
        seen.add(t);table=T[t]
        detail += ['<a id="tabla-'+t+'"></a>','','**Diccionario de `'+t+'` — '+('tabla actual ampliada' if table['existing'] else 'tabla propuesta')+'.**','',
        '**Clave primaria:** `'+table['pk']+'`. '+table['description'],'']
        if t in A:
            path=R.parent.parent/A[t]['source'];detail += ['**Fuente actual:** ['+A[t]['entity']+']('+path.as_posix()+').','']
        detail+=['| Atributo | Estado | Tipo y obligatoriedad en el modelo revisado | Finalidad / relación |','|---|---|---|---|']
        for c in table['columns']:
            relations=[f'FK a `{f["parent"]}.{",".join(f["targets"])}`' for f in F if f['child']==t and c['name'] in f['cols']]
            why=c['why']+(' '+ '; '.join(dict.fromkeys(relations))+'.' if relations else '')
            detail.append(f'| `{c["name"]}` | **{c["status"]}** | `{c["definition"]}` | {why} |')
        detail+=['']
        existing=[c['definition'] for c in table['constraints'] if c['status']=='ACTUAL'];added=[c['definition'] for c in table['constraints'] if c['status']=='NUEVA']
        if existing:detail += ['**Restricciones actuales conservadas:** '+'; '.join('`'+x+'`' for x in existing)+'.','']
        if table['indexes']:detail += ['**Índices actuales conservados:** '+'; '.join('`'+x+'`' for x in table['indexes'])+'.','']
        if added:detail += ['**Restricciones propuestas para revisar:** '+'; '.join('`'+x+'`' for x in added)+'.','']
assert seen==set(T)
detail += ['**Verificación de este SQL revisado:** instalación en PostgreSQL temporal PGlite con btree_gist; '+str(len(results['pruebas']))+' comprobaciones de persistencia y reglas financieras acotadas. No se ejecutó en la base del usuario, ni verifica la UI, los permisos, la concurrencia multiconexión o el cierre completo.','','| Comprobación | Resultado |','|---|---|']
detail += ['| '+p['prueba']+' | '+p['resultado']+' |' for p in results['pruebas']]
detail += ['','**Antes de aplicar cambios a tu base:** revisar vista por vista los atributos marcados AGREGAR y las tablas nuevas; decidir cuáles se implementan primero; preparar migraciones TypeORM aditivas con backfill validado. Este archivo SQL total es una referencia de instalación nueva, no una migración de tus registros.','']
if history:
    detail += ['## Historial anterior a esta actualización del SQL','','Los hallazgos y frases en tiempo presente que siguen describen las revisiones anteriores. El dictamen y estado actuales son la introducción, los diccionarios regenerados y el apartado final Schema actualizado.','',history,'']
detail += [cierre(M,results)]
(R/'01_reporte_especifico.md').write_text('\n'.join(detail),encoding='utf8')
(R/'02_tablas_y_relaciones.md').write_text('\n'.join(general),encoding='utf8')
print(f'{len(views)} vistas, {len(seen)} diccionarios; columnas ACTUAL/AGREGAR/TABLA NUEVA; nombres y claves alineados al backend.')
