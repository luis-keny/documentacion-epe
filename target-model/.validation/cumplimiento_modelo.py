"""Cambios mínimos de persistencia FC01–FC14 sobre el modelo de revisión."""
def aplicar(M, F, addcol, fk):
    cambios = []
    def edit(t, n, definition, why):
        c = next(c for c in M[t]['columns'] if c['name'] == n)
        cambios.append({'tabla': t, 'columna': n, 'antes': c['definition'], 'despues': definition})
        status=('MODIFICAR' if c['status']=='ACTUAL' else 'AGREGAR') if M[t]['existing'] else 'TABLA NUEVA'
        c.update(definition=definition, why=why, status=status)
    def add(t, n, d, why):
        addcol(t, n, d, why)
    def check(t, expr):
        M[t]['constraints'].append({'definition': 'CHECK (' + expr + ')', 'status': 'NUEVA'})
    def obj(t, n, why, array=False):
        add(t, n, "jsonb NOT NULL DEFAULT '" + ('[]' if array else '{}') + "'::jsonb", why)
        check(t, "jsonb_typeof(" + n + ") = '" + ('array' if array else 'object') + "'")

    for n, d in [('nmr_documento','varchar(30) NOT NULL'), ('telefono','varchar(30) NOT NULL'), ('codigo_lugar_produccion','varchar(60)'), ('identidad_doc_url','text'), ('email','varchar(320)')]:
        edit('proveedor', n, d, 'FC01: conservar texto/ceros/letras o admitir dato pendiente del formulario.')
    add('proveedor','fecha_registro','date','Fecha de registro que muestra el padrón del prototipo.')
    for n in ['ha_total_finca','ha_cultivo']:
        edit('finca',n,'numeric(12,3) NOT NULL','FC01: admite hectáreas fraccionarias sin redondear a enteros.')
    edit('empresa_transporte_externo','ruc','varchar(11)','FC01: independiente identificado por documento; empresa conserva RUC obligatorio por CHECK.')
    for t,n in [('empresa_transporte_externo','correo'),('chofer_transporte_externo','correo'),('cliente_negocio','correo_corporativo')]:
        edit(t,n,'varchar(320)','FC01: correo opcional según el validador del padrón; no usar cadenas vacías compartidas.')
    check('empresa_transporte_externo', "(tipo_transportista = 'EMPRESA' AND ruc IS NOT NULL AND ruc ~ '^[0-9]{11}$') OR (tipo_transportista = 'INDEPENDIENTE' AND tipo_documento IS NOT NULL AND numero_documento IS NOT NULL AND length(trim(numero_documento)) > 0)")
    for n, typ in [('volumen','numeric(12,3)'),('ancho','numeric(10,3)'),('altura','numeric(10,3)'),('profundidad','numeric(10,3)'),('peso_neto','numeric(14,3)'),('peso_bruto','numeric(14,3)')]:
        edit('vehiculo_externo',n,typ,'FC01: dimensión/peso pendiente no obliga a inventar un valor positivo.')
    edit('campania_x_proveedores','mtd_ceratitis','numeric(12,3)','FC02: legacy opcional; MTD operativo se registra por finca en medicion_mtd.')
    for n, d in [('precio_compra_kg','numeric(14,4)'),('moneda',"varchar(3) NOT NULL DEFAULT 'PEN'"),('disponibilidad_desde','date'),('disponibilidad_hasta','date'),('observaciones','text')]:
        add('campania_x_proveedores',n,d,'FC02: datos del editor de participación; el precio no requiere un tarifario adicional.')
    check('campania_x_proveedores',"moneda = 'PEN' AND (precio_compra_kg IS NULL OR precio_compra_kg > 0)")
    check('campania_x_proveedores','disponibilidad_hasta >= disponibilidad_desde')
    for n in ['densidad','distanciamiento','frecuencia','nombre_aplicacion','anio_aplicacion']:
        c=next(c for c in M['entrevista_extencion']['columns'] if c['name']==n)
        edit('entrevista_extencion',n,c['definition'].replace(' NOT NULL',''),'FC02: el escalar legacy no impide guardar la descripción agronómica del formulario.')
    for n in ['resultado','documento_url','observacion','origen']:
        c=next(c for c in M['examen_proveedor']['columns'] if c['name']==n)
        edit('examen_proveedor',n,c['definition'].replace(' NOT NULL',''),'FC03: dato pendiente hasta completar la etapa correspondiente.')
    edit('examen_proveedor','estado_examen',"varchar(30) NOT NULL DEFAULT 'Pendiente'",'FC03: etapa explícita del trámite de laboratorio.')
    check('examen_proveedor',"estado_examen IN ('Pendiente','Enviado','Con resultado')")
    check('examen_proveedor',"estado_examen <> 'Con resultado' OR resultado IS NOT NULL")
    for n in ['document_url','recibo_url','fecha_vencimiento','estado']:
        c=next(c for c in M['certificado_campana']['columns'] if c['name']==n)
        edit('certificado_campana',n,c['definition'].replace(' NOT NULL',''),'FC04: permitir ficha inicial sin evidencia o fechas todavía completas.')
    add('certificado_campana','vigencia_desde','date','FC04: inicio de vigencia independiente de la emisión.')
    add('certificado_campana','observaciones','text','FC04: notas del editor de certificación.')
    obj('certificado_campana','historial_cobertura','FC04: filas {fecha,kilos,producerIds}; conserva cada selección anterior.',True)
    check('certificado_campana','fecha_vencimiento >= vigencia_desde')
    for n in ['documento_url','ficha_tecnica_url']:
        edit('cliente_negocio_campana',n,'text','FC05: vinculación inicial sin contrato/adjunto todavía.')
    M['cliente_negocio_campana']['indexes']=[i for i in M['cliente_negocio_campana']['indexes'] if 'UQ_cliente_negocio_campania' not in i]
    edit('contrato_venta','precio_kg','numeric(14,4)','FC05: contrato con precio pendiente; completar antes de preparar venta.')
    edit('contrato_venta','numero',"varchar(60) NOT NULL DEFAULT ('CTR-' || gen_random_uuid()::text)",'FC05: identificador interno autogenerado, sin pedir un campo nuevo en UI.')
    for n in ['condiciones_entrega','observaciones']:
        add('contrato_venta',n,'text','FC05: texto propio del contrato que el formulario vuelve a mostrar.')
    for n in ['fruta_derivada_id','fecha_inicio','fecha_fin']:
        c=next(c for c in M['acuerdo_compra']['columns'] if c['name']==n)
        edit('acuerdo_compra',n,c['definition'].replace(' NOT NULL',''),'Compatibilidad: el precio simple no exige variedad o vigencia de un tarifario nuevo.')
    add('acuerdo_compra','moneda',"varchar(3) NOT NULL DEFAULT 'PEN'",'Compra en soles según respuesta del usuario.')
    check('acuerdo_compra',"moneda = 'PEN'")
    for n in ['tipo_pago','monto_acordado','fecha_acuerdo']:
        c=next(c for c in M['acuerdo_transporte']['columns'] if c['name']==n)
        edit('acuerdo_transporte',n,c['definition'].replace(' NOT NULL',''),'FC06: el vínculo existe como borrador antes de completar las condiciones.')
    add('acuerdo_transporte','estado',"varchar(20) NOT NULL DEFAULT 'BORRADOR'",'FC06: BORRADOR vincula empresa/campaña; CONFIRMADO exige condiciones completas.')
    add('acuerdo_transporte','moneda',"varchar(3) NOT NULL DEFAULT 'PEN'",'Compra/transporte en soles según respuesta del usuario.')
    add('acuerdo_transporte','adelanto_acordado','numeric(14,2) NOT NULL DEFAULT 0','Distingue adelanto previsto de los desembolsos reales.')
    add('acuerdo_transporte','referencia_cotizacion','text','Texto de cotización del vínculo aun sin una cotización estructurada.')
    check('acuerdo_transporte',"estado IN ('BORRADOR','CONFIRMADO') AND moneda = 'PEN'")
    check('acuerdo_transporte',"estado <> 'CONFIRMADO' OR (tipo_pago IS NOT NULL AND monto_acordado IS NOT NULL AND fecha_acuerdo IS NOT NULL AND fecha_pago_final IS NOT NULL)")
    check('acuerdo_transporte','adelanto_acordado >= 0 AND (monto_acordado IS NULL OR adelanto_acordado <= monto_acordado)')
    for n,d in [('flete_asignado','numeric(14,2)'),('observacion_flete','text')]:
        add('coordinacion_entrega',n,d,'FC07: flete de esta entrega, previo a liquidar; observación para exceso del acuerdo.')
    check('coordinacion_entrega','flete_asignado > 0')
    M['coordinacion_entrega']['constraints'].append({'name':'EX_coordinacion_chofer_sin_solape','definition':"EXCLUDE USING gist (id_chofer_transporte_externo WITH =, tstzrange(inicio_programado, fin_programado, '[)') WITH &&)",'status':'NUEVA'})
    for n in ['fecha_asignacion_inicio','fecha_asignacion_final']:
        edit('chofer_vehiculo_externo',n,'timestamptz NOT NULL','Viajes sucesivos del chofer en un mismo día; intervalo de instantes [inicio,fin).')
    for c in M['chofer_vehiculo_externo']['constraints']:
        if c.get('name')=='EX_chofer_sin_rangos_superpuestos':
            c.update(definition='EXCLUDE USING gist (id_chofer_transporte_externo WITH =, tstzrange(fecha_asignacion_inicio, fecha_asignacion_final, \'[)\') WITH &&)',status='NUEVA')
        if c.get('name')=='CHK_asignacion_fechas_validas':
            c.update(definition='CHECK (fecha_asignacion_final > fecha_asignacion_inicio)',status='NUEVA')
    obj('campana','calidad','FC08: objeto por canal Industria/Exportación, con incorporación/estado y rechazos; no requiere entrega ficticia.')
    for n,array in [('organizacion',False),('avances',True),('cierre',False),('industria',False)]:
        obj('cosecha',n,'FC08: conserva el objeto/lista homólogo de QualityOperation ('+n+'); avances identifican proveedor/finca, fecha, kilos, jabas y responsable.',array)
    add('cosecha','observaciones','text','Notas de la operación de calidad/cosecha.')
    M['cosecha']['constraints'].append({'definition':'UNIQUE (entrega_programada_id)','status':'NUEVA'})
    obj('guia_remision','contenido','FC09: snapshot completo de RemissionGuideDetails y campos impresos; conserva datos históricos.')
    add('guia_remision','emitida_at','timestamptz','Distingue borrador de guía emitida; el contenido emitido se conserva.')
    obj('proveedor_guia','fincas_ids','FC09: IDs de las fincas de este proveedor seleccionadas para esta guía.',True)
    for n,array in [('compras',True),('logistica',False),('checklist',False),('documentos',False)]:
        obj('recepcion_planta',n,'FC10: datos de LogisticsDelivery; compras guarda providerId, recognizedQuantity, revisión y soporte; checklist conserva no aplica y confirmaciones.',array)
    for n,d in [('descarga_inicio_at','timestamptz'),('descarga_fin_at','timestamptz'),('jabas_iniciales','integer'),('jabas_no_aplica','boolean')]:
        add('recepcion_planta',n,d,'FC10: dato de descarga/devolución que no puede reconstruirse desde un único total o fecha.')
    check('recepcion_planta','descarga_fin_at >= descarga_inicio_at')
    check('recepcion_planta','jabas_iniciales >= 0 AND (jabas_iniciales IS NULL OR jabas_devueltas <= jabas_iniciales)')
    check('recepcion_planta','descarte_kg <= peso_planta_kg')
    for n,d in [('kilos_reconocidos','numeric(14,3) NOT NULL'),('precio_kg_aplicado','numeric(14,4) NOT NULL'),('moneda',"varchar(3) NOT NULL DEFAULT 'PEN'"),('fecha_vencimiento','date'),('persona_snapshot','jsonb NOT NULL'),('aviso_uit_confirmado','boolean NOT NULL DEFAULT false'),('limite_uit_aplicado','numeric(10,2) NOT NULL DEFAULT 75')]:
        add('liquidacion_proveedor',n,d,'FC11: base reconocida y precio históricos, identidad de la persona y datos del documento/control anual.')
    check('liquidacion_proveedor',"kilos_reconocidos > 0 AND precio_kg_aplicado > 0 AND moneda = 'PEN'")
    check('liquidacion_proveedor','importe_compra = round(kilos_reconocidos * precio_kg_aplicado, 2)')
    check('liquidacion_proveedor',"jsonb_typeof(persona_snapshot) = 'object'")
    check('liquidacion_proveedor','limite_uit_aplicado > 0')
    F[:]=[f for f in F if not (f['child']=='liquidacion_proveedor' and f['parent']=='proveedor_x_persona')]
    fk('liquidacion_proveedor',['persona_liquidacion_id'],'persona')
    for n,d in [('fecha_vencimiento','date'),('moneda',"varchar(3) NOT NULL DEFAULT 'PEN'"),('observaciones','text')]:
        add('liquidacion_transporte',n,d,'FC07/11: documento de transporte en soles y su vencimiento/notas.')
    check('liquidacion_transporte',"moneda = 'PEN'")
    M['factura_venta']['constraints']=[c for c in M['factura_venta']['constraints'] if c['definition'] not in ['UNIQUE (carga_id)','CHECK (importe_venta = round(kilos_facturados * precio_kg_aplicado, 2))']]
    for n,d in [('descuento','numeric(14,2) NOT NULL DEFAULT 0'),('cargos','numeric(14,2) NOT NULL DEFAULT 0'),('observaciones','text'),('verificada_at','timestamptz')]:
        add('factura_venta',n,d,'FC12: ajustes/notas y verificación de emisión del prototipo; varias facturas por carga según respuesta explícita.')
    check('factura_venta','descuento >= 0 AND cargos >= 0 AND importe_venta > 0')
    check('factura_venta','importe_venta = round(kilos_facturados * precio_kg_aplicado - descuento + cargos, 2)')
    M['empresa_transporte_externo']['description']='Padrón de empresas con RUC e independientes identificados por documento; admite correo y dimensiones pendientes en sus subrecursos.'
    M['acuerdo_compra']['description']='Compatibilidad opcional de condiciones de compra; la participación conserva el precio simple sin exigir tarifario ni vigencias.'
    M['acuerdo_transporte']['description']='Vínculo empresa/campaña en BORRADOR; al CONFIRMAR conserva monto, moneda PEN, tipo, adelanto previsto y fechas.'
    # D08 (29/10/2026): el prototipo captura destinos como texto, sin CRUD de catálogo.
    destino=next(c for c in M['entrega_programada']['columns'] if c['name']=='destino_id')
    destino.update(name='destino',definition='text NOT NULL',why='D08: destino libre capturado por el formulario de entrega; no referencia un catálogo.')
    check('entrega_programada',"btrim(destino) <> ''")
    M['guia_remision']['columns']=[c for c in M['guia_remision']['columns'] if c['name']!='destino_id']
    for c in M['guia_remision']['columns']:
        if c['name']=='direccion_llegada_snapshot':
            c['why']='D08: dirección de destino textual capturada en la guía; conserva el punto de llegada histórico sin catálogo.'
    del M['destino_cliente_negocio']
    F[:]=[f for f in F if f['child']!='destino_cliente_negocio' and f['parent']!='destino_cliente_negocio']
    return cambios
