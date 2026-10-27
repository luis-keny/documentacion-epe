from pathlib import Path
import re, json

ROOT=Path(__file__).resolve().parent.parent
tables={}; descriptions={}; refs=[]; checks={}; uniques={}
def T(name, description, columns, unique=(), check=()):
    descriptions[name]=description
    tables[name]=['id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY']+[s.strip() for s in columns.strip().split('\n') if s.strip()]
    uniques[name]=list(unique); checks[name]=list(check)
def FK(child, cols, parent, target='id'):
    refs.append((child,cols,parent,target))
def fields(table, text): tables[table]+=[x.strip() for x in text.strip().split('\n') if x.strip()]
T('personas','Identidad única de productores, familiares y conductores.', '''tipo_documento varchar(20) NOT NULL
numero_documento varchar(30) NOT NULL
nombres varchar(120) NOT NULL
apellidos varchar(120) NOT NULL
telefono varchar(30)
correo varchar(180)
documento_archivo_id bigint''', ['tipo_documento, numero_documento'])
T('roles','Perfiles de acceso; los permisos efectivos se aplican en el servidor.', 'nombre varchar(40) NOT NULL', ['nombre'])
T('usuarios','Cuenta asociada a una persona; no se crea una cuenta por cada participación comercial.', '''persona_id bigint NOT NULL
rol_id bigint NOT NULL
usuario varchar(80) NOT NULL
password_hash text NOT NULL
activo boolean NOT NULL DEFAULT true''', ['persona_id','usuario'])
T('archivos','Metadatos del objeto almacenado; la base no almacena URLs firmadas ni el binario.', '''nombre varchar(255) NOT NULL
ruta_storage text NOT NULL
tipo_mime varchar(100) NOT NULL
bytes bigint NOT NULL
sha256 varchar(64)
subido_por bigint
fecha_subida timestamptz NOT NULL DEFAULT now()''', ['ruta_storage'],['bytes > 0'])
T('sesiones_usuario','Propuesta técnica para persistir sesiones; solo se conserva el hash del token.', '''usuario_id bigint NOT NULL
token_hash text NOT NULL
creada_at timestamptz NOT NULL DEFAULT now()
expira_at timestamptz NOT NULL
revocada_at timestamptz''',['token_hash'],['expira_at > creada_at'])
T('parametros_uit','Parámetros anuales configurables del prototipo, sin afirmar vigencia tributaria.', '''anio integer NOT NULL
valor numeric(14,2) NOT NULL
limite_uit numeric(10,2) NOT NULL
umbral_alerta numeric(5,4) NOT NULL DEFAULT 0.90''',['anio'],['valor > 0','limite_uit > 0','umbral_alerta > 0 AND umbral_alerta <= 1'])
T('frutas','Catálogo de frutas.', 'nombre varchar(80) NOT NULL',['nombre'])
T('variedades','Variedades pertenecientes a una fruta.', '''fruta_id bigint NOT NULL
nombre varchar(100) NOT NULL''',['fruta_id, nombre'])
T('campanias','Campaña con sus fechas, responsable y cierre manual.', '''nombre varchar(120) NOT NULL
fruta_id bigint NOT NULL
temporada varchar(30) NOT NULL
fecha_inicio date NOT NULL
fecha_fin date NOT NULL
estado varchar(25) NOT NULL DEFAULT 'PLANIFICADO'
responsable_id bigint
lineamientos_id bigint
observaciones text
cerrada_at timestamptz
cerrada_por bigint
motivo_cierre text''',[],["estado IN ('PLANIFICADO','EN_PROCESO','FINALIZADO')",'fecha_fin >= fecha_inicio',"(estado = 'FINALIZADO') = (cerrada_at IS NOT NULL AND cerrada_por IS NOT NULL AND motivo_cierre IS NOT NULL)"])
T('campania_variedades','Variedades elegidas para una campaña.', '''campania_id bigint NOT NULL
variedad_id bigint NOT NULL''',['campania_id, variedad_id'])
T('proveedores','Identidad comercial del proveedor principal.', '''persona_principal_id bigint NOT NULL
codigo varchar(40) NOT NULL
zona varchar(120)
codigo_produccion varchar(60)
estado_sanidad varchar(30)
activo boolean NOT NULL DEFAULT true''',['persona_principal_id','codigo'])
T('personas_proveedor','Personas vinculadas; la relación no transfiere compras históricas.', '''proveedor_id bigint NOT NULL
persona_id bigint NOT NULL
vinculo varchar(60) NOT NULL
activo boolean NOT NULL DEFAULT true''',['proveedor_id, persona_id'])
T('proveedor_frutas','Frutas asociadas al padrón general.', '''proveedor_id bigint NOT NULL
fruta_id bigint NOT NULL''',['proveedor_id, fruta_id'])
T('proveedor_variedades','Variedades asociadas al padrón general.', '''proveedor_id bigint NOT NULL
variedad_id bigint NOT NULL''',['proveedor_id, variedad_id'])
T('fincas','Datos físicos de cada finca, independientes de la campaña.', '''proveedor_id bigint NOT NULL
nombre varchar(150) NOT NULL
codigo_produccion varchar(60)
codigo_catastral varchar(60)
departamento varchar(80) NOT NULL
provincia varchar(80) NOT NULL
distrito varchar(80) NOT NULL
ubigeo varchar(6)
direccion text
codigo_establecimiento varchar(4)
latitud numeric(10,7)
longitud numeric(10,7)
hectareas numeric(12,4) NOT NULL
hectareas_cultivo numeric(12,4) NOT NULL
variedad_id bigint
edad_cultivo_anios numeric(6,2)''',['id, proveedor_id'],['hectareas > 0','hectareas_cultivo >= 0 AND hectareas_cultivo <= hectareas',"ubigeo IS NULL OR ubigeo ~ '^[0-9]{6}$'",'latitud BETWEEN -90 AND 90','longitud BETWEEN -180 AND 180','(latitud IS NULL) = (longitud IS NULL)'])
T('certificados_propios','Certificados generales del proveedor; distintos del certificado de campaña.', '''proveedor_id bigint NOT NULL
nombre varchar(180) NOT NULL
fecha_revision date
archivo_id bigint NOT NULL''')
T('participaciones_proveedor','Vinculación proveedor–campaña; aquí pertenecen rol, oferta y evaluación.', '''campania_id bigint NOT NULL
proveedor_id bigint NOT NULL
rol_comercial varchar(20) NOT NULL
tipo_fruta varchar(20) NOT NULL
kilos_estimados numeric(14,3) NOT NULL
estado varchar(30) NOT NULL DEFAULT 'EXAMEN_PENDIENTE'
entrevista_aplica boolean NOT NULL DEFAULT true
fecha_registro timestamptz NOT NULL DEFAULT now()
observaciones text''',['campania_id, proveedor_id','id, campania_id, proveedor_id'],["rol_comercial IN ('PRODUCTOR','ACOPIADOR')","tipo_fruta IN ('ORGANICA','CONVENCIONAL')",'kilos_estimados >= 0',"estado IN ('EXAMEN_PENDIENTE','ENTREVISTA_PENDIENTE','APROBADO','RECHAZADO')"])
T('participacion_variedades','Variedades de la participación, sin deducirlas solo de contratos de compra.', '''participacion_id bigint NOT NULL
variedad_id bigint NOT NULL''',['participacion_id, variedad_id'])
T('fincas_campania','Fincas vinculadas a una participación; permite conservar historial por campaña.', '''participacion_id bigint NOT NULL
campania_id bigint NOT NULL
proveedor_id bigint NOT NULL
finca_id bigint NOT NULL''',['campania_id, finca_id','id, participacion_id'])
T('entrevistas','Registro agronómico de cada finca entrevistada en una campaña.', '''finca_campania_id bigint NOT NULL
codigo_fyv varchar(60) NOT NULL
registrada_at timestamptz NOT NULL DEFAULT now()
registrada_por bigint
densidad_plantacion numeric(12,3)
distanciamiento_m varchar(60)
frecuencia_riego varchar(120)
nombre_aplicacion varchar(180)
aplicaciones_anio integer
resultado text
archivo_id bigint''',[],['densidad_plantacion > 0','aplicaciones_anio >= 0'])
T('examenes','Exámenes sanitarios de la participación, con muestra y fechas de laboratorio.', '''participacion_id bigint NOT NULL
finca_campania_id bigint
tipo varchar(100) NOT NULL
codigo_muestra varchar(80)
origen varchar(180)
fecha_muestra date NOT NULL
fecha_envio date
estado varchar(30) NOT NULL DEFAULT 'PENDIENTE'
resultado varchar(180)
archivo_id bigint
observaciones text''',[],['fecha_envio IS NULL OR fecha_envio >= fecha_muestra'])
T('acuerdos_compra','Condiciones versionadas por finca, variedad y vigencia; no sustituye la participación.', '''finca_campania_id bigint NOT NULL
variedad_id bigint NOT NULL
precio_kg numeric(14,4) NOT NULL
kilos_acordados numeric(14,3)
fecha_inicio date NOT NULL
fecha_fin date NOT NULL
estado varchar(25) NOT NULL DEFAULT 'VIGENTE' ''',[],['precio_kg > 0','kilos_acordados >= 0','fecha_fin >= fecha_inicio'])
T('normas','Catálogo de normas de certificación y traslado.', '''codigo varchar(40) NOT NULL
nombre varchar(180) NOT NULL''',['codigo'])
T('certificaciones','Certificado de campaña, costo y organismo; un certificado por campaña según la UI.', '''campania_id bigint NOT NULL
norma_id bigint NOT NULL
nombre varchar(180) NOT NULL
codigo varchar(80)
organismo varchar(180) NOT NULL
fecha_emision date NOT NULL
fecha_vencimiento date NOT NULL
costo numeric(14,2) NOT NULL
moneda varchar(3) NOT NULL
archivo_id bigint NOT NULL''',['campania_id','id, campania_id'],['fecha_vencimiento >= fecha_emision','costo >= 0',"moneda IN ('PEN','USD','EUR')"])
T('certificacion_proveedor','Productores cubiertos y kilos iniciales capturados al certificar.', '''certificacion_id bigint NOT NULL
campania_id bigint NOT NULL
participacion_id bigint NOT NULL
proveedor_id bigint NOT NULL
kilos_autorizados numeric(14,3) NOT NULL''',['certificacion_id, participacion_id'],['kilos_autorizados > 0'])
T('ampliaciones_certificacion','Incrementos de cobertura, sin sobrescribir los kilos iniciales.', '''certificacion_id bigint NOT NULL
fecha date NOT NULL
kilos_adicionales numeric(14,3) NOT NULL
referencia varchar(180) NOT NULL
registrado_por bigint''',[],['kilos_adicionales > 0'])
T('pagos_certificacion','Desembolsos de la certificación en su misma moneda.', '''certificacion_id bigint NOT NULL
fecha date NOT NULL
monto numeric(14,2) NOT NULL
referencia varchar(100) NOT NULL
comprobante_id bigint NOT NULL
registrado_por bigint''',['certificacion_id, referencia'],['monto > 0'])
T('clientes','Padrón general del cliente y contacto.', '''razon_social varchar(180) NOT NULL
ruc varchar(11) NOT NULL
contacto varchar(180) NOT NULL
tipo varchar(20) NOT NULL
telefono varchar(30)
correo varchar(180)
ubicacion varchar(180)
fecha_registro date NOT NULL DEFAULT CURRENT_DATE''',['ruc'],["tipo IN ('EXPORTADOR','INDUSTRIA')","ruc ~ '^[0-9]{11}$'"])
T('destinos_cliente','Puntos de llegada de cada cliente; no asumir que todos comparten una planta.', '''cliente_id bigint NOT NULL
nombre varchar(150) NOT NULL
ubigeo varchar(6)
direccion text
codigo_establecimiento varchar(4)
latitud numeric(10,7)
longitud numeric(10,7)''',['id, cliente_id'],['latitud BETWEEN -90 AND 90','longitud BETWEEN -180 AND 180','(latitud IS NULL) = (longitud IS NULL)'])
T('requerimientos_comerciales','Participación cliente–campaña y necesidad original, previa a sus contratos.', '''campania_id bigint NOT NULL
cliente_id bigint NOT NULL
cantidad_kg numeric(14,3) NOT NULL
fecha_registro date NOT NULL
ficha_tecnica_id bigint
destino_solicitado varchar(180)
entrega_desde date
entrega_hasta date
observaciones text''',[],['cantidad_kg > 0','entrega_hasta >= entrega_desde'])
T('requerimiento_variedades','Selección múltiple de variedades requeridas.', '''requerimiento_id bigint NOT NULL
variedad_id bigint NOT NULL''',['requerimiento_id, variedad_id'])
T('contratos_venta','Varios contratos por requerimiento, con precio y moneda propios.', '''requerimiento_id bigint NOT NULL
numero varchar(60) NOT NULL
canal varchar(20) NOT NULL
fecha date NOT NULL
kilos_acordados numeric(14,3) NOT NULL
precio_kg numeric(14,4) NOT NULL
moneda varchar(3) NOT NULL
estado varchar(25) NOT NULL DEFAULT 'VIGENTE'
condiciones_pago text
archivo_id bigint''',['numero'],['kilos_acordados > 0','precio_kg > 0',"canal IN ('EXPORTACION','INDUSTRIA')","moneda IN ('PEN','USD','EUR')"])
T('entregas_programadas','Programación comercial; puede existir antes de asignar transporte.', '''contrato_id bigint NOT NULL
destino_id bigint NOT NULL
fecha date NOT NULL
kilos_programados numeric(14,3) NOT NULL
observaciones text''',[],['kilos_programados > 0'])
T('entrega_variedades','Distribución programada por variedad para el programa semanal.', '''entrega_id bigint NOT NULL
variedad_id bigint NOT NULL
kilos_programados numeric(14,3) NOT NULL''',['entrega_id, variedad_id'],['kilos_programados > 0'])
T('empresas_transporte','Nombre heredado del DBML; admite empresas e independientes.', '''tipo varchar(20) NOT NULL
razon_social varchar(180) NOT NULL
tipo_documento varchar(20) NOT NULL
numero_documento varchar(30) NOT NULL
persona_id bigint
registro_mtc varchar(80)
telefono varchar(30)
correo varchar(180)
departamento varchar(80)
provincia varchar(80)
ciudad varchar(80)
activo boolean NOT NULL DEFAULT true''',['tipo_documento, numero_documento'],["tipo IN ('EMPRESA','INDEPENDIENTE')","tipo <> 'INDEPENDIENTE' OR persona_id IS NOT NULL"])
T('vehiculos','Unidad de transporte con capacidad y pesos explícitos.', '''empresa_id bigint NOT NULL
placa varchar(15) NOT NULL
volumen_m3 numeric(12,3)
capacidad_kg numeric(14,3) NOT NULL
peso_bruto_kg numeric(14,3)
activo boolean NOT NULL DEFAULT true''',['placa','id, empresa_id'],['capacidad_kg > 0','volumen_m3 > 0','peso_bruto_kg >= capacidad_kg'])
T('choferes','Identidad del conductor y vínculo opcional a cuenta de acceso.', '''empresa_id bigint NOT NULL
persona_id bigint NOT NULL
usuario_id bigint
licencia varchar(40) NOT NULL
activo boolean NOT NULL DEFAULT true''',['persona_id','usuario_id','id, empresa_id'])
T('solicitudes_transporte','Solicitud persistida; enviar correos está simulado en el prototipo.', '''campania_id bigint NOT NULL
referencia varchar(100) NOT NULL
fecha timestamptz NOT NULL DEFAULT now()
origen text NOT NULL
destino text NOT NULL
ventana_servicio varchar(180)
cantidad_estimada varchar(100)
caracteristicas_vehiculo text
condiciones text
limite_respuesta timestamptz
mensaje text
archivo_id bigint
estado varchar(25) NOT NULL DEFAULT 'BORRADOR' ''',['referencia'])
T('invitaciones_transporte','Destinatarios por solicitud, con contacto capturado al invitar.', '''solicitud_id bigint NOT NULL
empresa_id bigint NOT NULL
correo_snapshot varchar(180)
estado varchar(25) NOT NULL DEFAULT 'INVITADA' ''',['solicitud_id, empresa_id'])
T('cotizaciones_transporte','Propuesta de respuesta; atributos no observables por lista vacía se proponen.', '''invitacion_id bigint NOT NULL
fecha date NOT NULL
monto numeric(14,2) NOT NULL
moneda varchar(3) NOT NULL
condiciones text
archivo_id bigint
estado varchar(25) NOT NULL DEFAULT 'RECIBIDA' ''',[],['monto > 0',"moneda IN ('PEN','USD','EUR')"])
T('acuerdos_transporte','Transportista vinculado a campaña y acuerdo de flete autorizado.', '''campania_id bigint NOT NULL
empresa_id bigint NOT NULL
cotizacion_id bigint
tipo_pago varchar(20) NOT NULL
monto_acordado numeric(14,2) NOT NULL
fecha_acuerdo date NOT NULL
fecha_pago_final date
archivo_id bigint''',['campania_id, empresa_id','id, empresa_id'],['monto_acordado > 0',"tipo_pago IN ('INMEDIATO','CON_ADELANTO','AL_FINAL')"])
T('coordinaciones_entrega','Asignación previa a la carga real; un registro por entrega.', '''entrega_id bigint NOT NULL
acuerdo_transporte_id bigint NOT NULL
empresa_id bigint NOT NULL
vehiculo_id bigint NOT NULL
chofer_id bigint NOT NULL
inicio_programado timestamptz NOT NULL
fin_programado timestamptz NOT NULL
origen_descripcion text NOT NULL
condiciones_carga text
observaciones text''',['entrega_id','id, entrega_id'],['fin_programado >= inicio_programado'])
T('origenes_entrega','Selección de varias fincas de varios proveedores antes de cargar.', '''coordinacion_id bigint NOT NULL
finca_campania_id bigint NOT NULL''',['coordinacion_id, finca_campania_id'])
T('cosechas','Operación de cosecha de una entrega; estado separado del despacho.', '''entrega_id bigint NOT NULL
codigo_lote varchar(60) NOT NULL
fecha_prevista date NOT NULL
kilos_estimados numeric(14,3) NOT NULL
kilos_cosechados numeric(14,3)
kilos_aceptados numeric(14,3)
estado varchar(30) NOT NULL DEFAULT 'PENDIENTE'
cierre_cosecha_at timestamptz
evidencia_id bigint''',['codigo_lote'],['kilos_estimados >= 0','kilos_cosechados >= 0','kilos_aceptados >= 0'])
T('analisis_calidad','Muestreo por operación y finca; no mezclar con exámenes de admisión.', '''cosecha_id bigint NOT NULL
finca_campania_id bigint NOT NULL
tipo varchar(100) NOT NULL
fecha_muestreo date NOT NULL
estado varchar(30) NOT NULL DEFAULT 'PENDIENTE'
resultado_texto varchar(180)
resultado_numerico numeric(14,4)
unidad varchar(30)
archivo_id bigint
observaciones text''')
T('mediciones_mtd','Historial de MTD por finca y campaña, con captura de respaldo.', '''finca_campania_id bigint NOT NULL
medido_at timestamptz NOT NULL
valor numeric(12,4) NOT NULL
limite_aplicado numeric(12,4) NOT NULL
archivo_id bigint NOT NULL
registrado_por bigint''',[],['valor >= 0','limite_aplicado >= 0'])
T('cargas','Carga física real de la coordinación; no crea otra asignación de camión o chofer.', '''coordinacion_id bigint NOT NULL
codigo varchar(80) NOT NULL
fecha_carga date NOT NULL
anotador_nombre varchar(180) NOT NULL
estado_calidad varchar(30) NOT NULL DEFAULT 'PENDIENTE'
viaticos_movilidad numeric(14,2) NOT NULL DEFAULT 0
viaticos_insumos numeric(14,2) NOT NULL DEFAULT 0
guia_salida_id bigint
guia_salida_registrada_at timestamptz
observaciones text''',['coordinacion_id','codigo','id, coordinacion_id'],['viaticos_movilidad >= 0','viaticos_insumos >= 0','(guia_salida_id IS NULL) = (guia_salida_registrada_at IS NULL)'])
T('proveedores_carga','Kilos reales por proveedor y variedad; la UI no reparte automáticamente por finca.', '''carga_id bigint NOT NULL
participacion_id bigint NOT NULL
variedad_id bigint NOT NULL
kilos_cargados numeric(14,3) NOT NULL
precio_compra_kg_aplicado numeric(14,4)
jabas_cargadas integer NOT NULL DEFAULT 0
jabas_vacias integer NOT NULL DEFAULT 0
bines_cargados integer NOT NULL DEFAULT 0
bines_vacios integer NOT NULL DEFAULT 0
mallas_cargadas integer NOT NULL DEFAULT 0
mallas_vacias integer NOT NULL DEFAULT 0''',['carga_id, participacion_id, variedad_id','id, carga_id'],['kilos_cargados > 0','precio_compra_kg_aplicado > 0'])
T('origenes_carga','Trazabilidad a fincas seleccionadas; asignación de kg opcional hasta medirla.', '''proveedor_carga_id bigint NOT NULL
finca_campania_id bigint NOT NULL
kilos_origen numeric(14,3)''',['proveedor_carga_id, finca_campania_id'],['kilos_origen > 0'])
T('gastos_carga','Cuadrilla, anotadores y otros costos de carga; no son automáticamente gasto de transporte.', '''carga_id bigint NOT NULL
concepto varchar(150) NOT NULL
monto numeric(14,2) NOT NULL''',['carga_id, concepto'],['monto >= 0'])
T('guias_remision','Documento de traslado y captura histórica de origen, destino y transportista.', '''carga_id bigint NOT NULL
numero varchar(30) NOT NULL
fecha_inicio_traslado date NOT NULL
fecha_entrega_transportista date
peso_bruto_kg numeric(14,3) NOT NULL
unidad_peso varchar(3) NOT NULL DEFAULT 'KGM'
numero_bultos integer NOT NULL
finca_partida_id bigint NOT NULL
destino_id bigint NOT NULL
ubigeo_partida_snapshot varchar(6) NOT NULL
direccion_partida_snapshot text NOT NULL
establecimiento_partida_snapshot varchar(4) NOT NULL
ubigeo_llegada_snapshot varchar(6) NOT NULL
direccion_llegada_snapshot text NOT NULL
establecimiento_llegada_snapshot varchar(4) NOT NULL
transportista_documento_snapshot varchar(30) NOT NULL
mtc_snapshot varchar(80)
placa_snapshot varchar(15) NOT NULL
conductor_documento_snapshot varchar(30) NOT NULL
conductor_nombre_snapshot varchar(180) NOT NULL
conductor_licencia_snapshot varchar(40) NOT NULL
archivo_id bigint
observaciones text''',['numero','id, carga_id'],['peso_bruto_kg > 0','numero_bultos > 0',"unidad_peso = 'KGM'"])
T('proveedores_guia','Distribución de kilos de una carga entre sus guías, sin duplicarlos.', '''guia_id bigint NOT NULL
carga_id bigint NOT NULL
proveedor_carga_id bigint NOT NULL
kilos_asignados numeric(14,3) NOT NULL''',['guia_id, proveedor_carga_id'],['kilos_asignados > 0'])
T('normas_guia','Selección múltiple de normas en la guía.', '''guia_id bigint NOT NULL
norma_id bigint NOT NULL''',['guia_id, norma_id'])
T('historial_chofer','Eventos ordenados del despacho; el estado vigente se deriva del último evento.', '''coordinacion_id bigint NOT NULL
carga_id bigint
chofer_id bigint NOT NULL
estado varchar(25) NOT NULL
fecha_hora timestamptz NOT NULL DEFAULT now()
observacion text''',['coordinacion_id, estado'],["estado IN ('EN_CARGA','SALIDA','EN_CAMINO','LLEGADA','CIERRE')"])
T('recepciones_planta','Recepción única con checklist, peso, descarte y cierre físico/administrativo.', '''carga_id bigint NOT NULL
chofer_id bigint NOT NULL
fecha_recepcion timestamptz
peso_planta_kg numeric(14,3)
hubo_descarte boolean
descarte_kg numeric(14,3)
evidencia_descarte_id bigint
reporte_recepcion_id bigint
resultado varchar(80)
recepcion_confirmada_at timestamptz
descarte_confirmado_at timestamptz
jabas_devueltas integer
jabas_devolucion_at timestamptz
descarga_at timestamptz
cierre_fisico_at timestamptz
cierre_administrativo_at timestamptz
observaciones text''',['carga_id'],['peso_planta_kg > 0','descarte_kg >= 0','jabas_devueltas >= 0',"hubo_descarte IS DISTINCT FROM false OR descarte_kg = 0","hubo_descarte IS DISTINCT FROM true OR (descarte_kg > 0 AND evidencia_descarte_id IS NOT NULL)"])
T('liquidaciones_proveedor','Documento por carga y proveedor, con persona receptora e importe histórico.', '''carga_id bigint NOT NULL
proveedor_id bigint NOT NULL
persona_liquidacion_id bigint NOT NULL
numero varchar(40) NOT NULL
fecha date NOT NULL
importe_compra numeric(14,2) NOT NULL
valor_uit_aplicado numeric(14,2) NOT NULL
registrado_por bigint NOT NULL
archivo_id bigint
observaciones text''',['carga_id, proveedor_id','numero'],['importe_compra > 0','valor_uit_aplicado > 0'])
T('liquidaciones_transporte','Documento por carga; flete ingresado al liquidar y gastos separados.', '''carga_id bigint NOT NULL
numero varchar(40) NOT NULL
fecha date NOT NULL
flete numeric(14,2) NOT NULL
registrado_por bigint NOT NULL
archivo_id bigint''',['carga_id','numero'],['flete >= 0'])
T('gastos_transporte','Gastos reales o viáticos aplicados una sola vez a la liquidación.', '''carga_id bigint NOT NULL
concepto varchar(150) NOT NULL
monto numeric(14,2) NOT NULL
origen varchar(20) NOT NULL
incluido_en_liquidacion boolean NOT NULL DEFAULT false''',['carga_id, concepto'],['monto >= 0',"origen IN ('VIATICO','REAL')"])
T('adelantos_transporte','Dinero entregado a la empresa antes de aplicarse a una carga.', '''acuerdo_id bigint NOT NULL
fecha date NOT NULL
monto numeric(14,2) NOT NULL
referencia varchar(100) NOT NULL
comprobante_id bigint NOT NULL''',['acuerdo_id, referencia'],['monto > 0'])
T('aplicaciones_adelanto','Aplicación de un adelanto existente; no representa otro desembolso.', '''adelanto_id bigint NOT NULL
liquidacion_id bigint NOT NULL
fecha date NOT NULL
monto numeric(14,2) NOT NULL''',['adelanto_id, liquidacion_id'],['monto > 0'])
T('facturas_venta','Preparación y factura externa en una fila; preserva peso, precio y moneda facturados.', '''carga_id bigint NOT NULL
referencia_preparacion varchar(40) NOT NULL
fecha_preparacion date NOT NULL
estado varchar(25) NOT NULL DEFAULT 'PREPARADA'
numero_factura varchar(80)
fecha_emision date
fecha_vencimiento date
kilos_facturados numeric(14,3) NOT NULL
precio_kg_aplicado numeric(14,4) NOT NULL
moneda varchar(3) NOT NULL
importe_venta numeric(14,2) NOT NULL
archivo_id bigint''',['carga_id','referencia_preparacion','numero_factura'],['kilos_facturados > 0','precio_kg_aplicado > 0','importe_venta = round(kilos_facturados * precio_kg_aplicado, 2)',"estado IN ('PREPARADA','EMITIDA')","moneda IN ('PEN','USD','EUR')","estado <> 'EMITIDA' OR (numero_factura IS NOT NULL AND fecha_emision IS NOT NULL AND archivo_id IS NOT NULL)",'fecha_vencimiento >= fecha_emision'])
for name,parent,key,desc in [('pagos_proveedor','liquidaciones_proveedor','liquidacion_id','Pagos parciales de compras en PEN.'),('pagos_transporte','liquidaciones_transporte','liquidacion_id','Desembolsos de transporte, distintos de aplicar adelantos.'),('cobros_venta','facturas_venta','factura_id','Cobros parciales en la moneda de la factura.')]:
    T(name,desc,f'''{key} bigint NOT NULL
fecha date NOT NULL
monto numeric(14,2) NOT NULL
medio varchar(30) NOT NULL
referencia varchar(100) NOT NULL
comprobante_id bigint NOT NULL
registrado_por bigint''',[f'{key}, referencia'],['monto > 0'])
    FK(name,key,parent)

# Relaciones simples inferidas únicamente por convención cuando el nombre es inequívoco.
targets={'persona_id':'personas','persona_principal_id':'personas','rol_id':'roles','subido_por':'usuarios','usuario_id':'usuarios','registrado_por':'usuarios','registrada_por':'usuarios','cerrada_por':'usuarios','responsable_id':'usuarios','fruta_id':'frutas','variedad_id':'variedades','campania_id':'campanias','proveedor_id':'proveedores','finca_id':'fincas','finca_partida_id':'fincas','participacion_id':'participaciones_proveedor','finca_campania_id':'fincas_campania','norma_id':'normas','certificacion_id':'certificaciones','cliente_id':'clientes','requerimiento_id':'requerimientos_comerciales','contrato_id':'contratos_venta','destino_id':'destinos_cliente','empresa_id':'empresas_transporte','solicitud_id':'solicitudes_transporte','invitacion_id':'invitaciones_transporte','cotizacion_id':'cotizaciones_transporte','acuerdo_transporte_id':'acuerdos_transporte','acuerdo_id':'acuerdos_transporte','coordinacion_id':'coordinaciones_entrega','entrega_id':'entregas_programadas','cosecha_id':'cosechas','carga_id':'cargas','proveedor_carga_id':'proveedores_carga','guia_id':'guias_remision','chofer_id':'choferes','adelanto_id':'adelantos_transporte'}
filecols={'archivo_id','documento_archivo_id','lineamientos_id','ficha_tecnica_id','evidencia_id','guia_salida_id','evidencia_descarte_id','reporte_recepcion_id','comprobante_id'}
for t,cols in tables.items():
    for col in cols:
        n=col.split()[0]
        target='archivos' if n in filecols else targets.get(n)
        if target and not any(r[0]==t and r[1]==n for r in refs): FK(t,n,target)
FK('fincas_campania','participacion_id, campania_id, proveedor_id','participaciones_proveedor','id, campania_id, proveedor_id')
FK('fincas_campania','finca_id, proveedor_id','fincas','id, proveedor_id')
FK('examenes','finca_campania_id, participacion_id','fincas_campania','id, participacion_id')
FK('certificacion_proveedor','certificacion_id, campania_id','certificaciones','id, campania_id')
FK('certificacion_proveedor','participacion_id, campania_id, proveedor_id','participaciones_proveedor','id, campania_id, proveedor_id')
for field,parent in [('acuerdo_transporte_id','acuerdos_transporte'),('vehiculo_id','vehiculos'),('chofer_id','choferes')]:
    FK('coordinaciones_entrega',field+', empresa_id',parent,'id, empresa_id')
FK('historial_chofer','carga_id, coordinacion_id','cargas','id, coordinacion_id')
FK('proveedores_guia','guia_id, carga_id','guias_remision','id, carga_id')
FK('proveedores_guia','proveedor_carga_id, carga_id','proveedores_carga','id, carga_id')
FK('liquidaciones_proveedor','proveedor_id, persona_liquidacion_id','personas_proveedor','proveedor_id, persona_id')
FK('aplicaciones_adelanto','liquidacion_id','liquidaciones_transporte')
for t in ['proveedores_carga']:
    for c in ['jabas_cargadas','jabas_vacias','bines_cargados','bines_vacios','mallas_cargadas','mallas_vacias']: checks[t].append(c+' >= 0')

sql=['-- AGRO EXPORTACIONES | modelo propuesto tras inspección del prototipo, 25/10/2026 (Lima).',
     '-- PostgreSQL. Instalación NUEVA en schema agro. No es una migración del sistema desplegado.',
     '-- No elimina ni reemplaza objetos existentes. Si agro ya existe, se aborta.',
     '-- Los valores UIT no se precargan: configurar después de validar el parámetro aplicable.',
     'BEGIN;','CREATE SCHEMA agro;','SET LOCAL search_path = agro, public;']
for t,cols in tables.items():
    definitions=cols+[f'UNIQUE ({u})' for u in uniques[t]]+[f'CHECK ({c})' for c in checks[t]]
    sql += [f'-- {descriptions[t]}',f'CREATE TABLE {t} (\n  '+',\n  '.join(definitions)+'\n);']
for i,(t,c,p,pc) in enumerate(refs,1): sql.append(f'ALTER TABLE {t} ADD CONSTRAINT fk_{t}_{i} FOREIGN KEY ({c}) REFERENCES {p} ({pc}) ON DELETE RESTRICT;')
# Índices de las columnas de búsqueda y FK. Los compuestos facilitan consultas sin duplicar entidades.
for i,(t,c,p,pc) in enumerate(refs,1):
    sql.append(f'CREATE INDEX ix_{t}_{i} ON {t} ({c});')
sql += ['CREATE INDEX ix_eventos_fecha ON historial_chofer (coordinacion_id, fecha_hora DESC, id DESC);',
        'CREATE INDEX ix_uit_persona_fecha ON liquidaciones_proveedor (persona_liquidacion_id, fecha);']
ROOT.joinpath('.validation/modelo.json').write_text(json.dumps({'tables':tables,'descriptions':descriptions,'refs':refs,'checks':checks,'uniques':uniques},ensure_ascii=False,indent=2),encoding='utf-8')
ROOT.joinpath('03_schema_total.sql').write_text('\n\n'.join(sql)+'\n\n',encoding='utf-8')
print(f'{len(tables)} tablas y {len(refs)} FK generadas')
