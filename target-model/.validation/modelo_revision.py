from pathlib import Path
import json,re,copy
R=Path(__file__).resolve().parent.parent
A={t['table']:t for t in json.loads((R/'.validation/modelo_actual.json').read_text(encoding='utf8'))}
B=json.loads((R/'.validation/resultado_actual.json').read_text(encoding='utf8'))
P=json.loads((R/'.validation/modelo_alineado.json').read_text(encoding='utf8'))
M={};F=[];enums={}
def qi(s):return '"'+s.replace('"','""')+'"'
def splitcols(s):return [x.strip() for x in s.split(',')]
def pk(t):return M[t]['pk']
def addcol(t,n,definition,why,parent=None):
    assert n not in {c['name'] for c in M[t]['columns']},(t,n)
    M[t]['columns'].append({'name':n,'definition':definition,'status':'AGREGAR' if t in A else 'TABLA NUEVA','why':why})
    if parent:F.append({'child':t,'cols':[n],'parent':parent,'targets':[pk(parent)],'onDelete':'RESTRICT','status':'NUEVA'})
def fk(t,cols,p,targets=None):
    targets=targets or [pk(p)]
    if not any(f['child']==t and f['cols']==cols and f['parent']==p and f['targets']==targets for f in F):
        F.append({'child':t,'cols':cols,'parent':p,'targets':targets,'onDelete':'RESTRICT','status':'NUEVA'})

# Base exacta: no renombra ni reemplaza los campos de las 20 entidades actuales.
for t,a in A.items():
    cols=[]
    for c in a['columns']:
        d=next(x for x in B['columns'] if x['table_name']==t and x['column_name']==c['name'])
        typ=d['data_type']
        if c['primary']:typ='serial'
        elif typ=='USER-DEFINED':
            typ=qi(d['udt_name']);enums[d['udt_name']]=c['enum']
        elif typ=='character varying':typ='varchar'+(f"({d['character_maximum_length']})" if d['character_maximum_length'] else '')
        elif typ=='numeric':typ=f"numeric({d['numeric_precision']},{d['numeric_scale']})"
        definition=typ+(' NOT NULL' if not c['nullable'] else '')
        if d['column_default'] and not c['primary']:definition+=' DEFAULT '+d['column_default'].replace('public.','agro.')
        cols.append({'name':c['name'],'definition':definition,'status':'ACTUAL','why':'Se conserva de la entidad/migración actual.'})
    M[t]={'pk':next(c['name'] for c in a['columns'] if c['primary']),'existing':True,'description':P['descriptions'].get(t,'Tabla actual de transporte que se conserva con su historial.'),'columns':cols,'constraints':[],'indexes':[]}
    for c in B['constraints']:
        if c['table_name']==t and c['contype'] not in ['f','n']:
            M[t]['constraints'].append({'name':c['conname'],'definition':c['definition'],'status':'ACTUAL'})
    for f in a['foreignKeys']:
        fragment='FOREIGN KEY ('+', '.join(f['columns'])+') REFERENCES '+f['parent']+'('+', '.join(f['target'])+')'
        migrated=next(c for c in B['constraints'] if c['table_name']==t and c['contype']=='f' and c['definition'].startswith(fragment))
        F.append({'child':t,'cols':f['columns'],'parent':f['parent'],'targets':f['target'],'onDelete':f['onDelete'],'status':'ACTUAL','name':migrated['conname']})
    autoindex={c['conname'] for c in B['constraints'] if c['table_name']==t and c['contype'] in ['p','u','x']}
    for ix in B['indexes']:
        if ix['tablename']==t and ix['indexname'] not in autoindex:M[t]['indexes'].append(ix['indexdef'].replace('ON public.','ON agro.'))

new=[t for t in P['tables'] if t not in A]
for t in new:
    M[t]={'pk':t+'_id','existing':False,'description':P['descriptions'][t],'columns':[],'constraints':[],'indexes':[]}
aliases={'variedad_id':'fruta_derivada_id','cliente_id':'cliente_negocio_id','requerimiento_id':'cliente_negocio_campana_id','empresa_id':'id_empresa_transporte_externo','chofer_id':'id_chofer_transporte_externo','vehiculo_id':'id_vehiculo_externo','finca_campania_id':'cxp_id','participacion_id':'participacion_proveedor_campana_id','certificacion_id':'certificado_id','coordinacion_id':'coordinacion_entrega_id','entrega_id':'entrega_programada_id','contrato_id':'contrato_venta_id','solicitud_id':'solicitud_transporte_id','invitacion_id':'invitacion_transporte_id','cotizacion_id':'cotizacion_transporte_id','acuerdo_id':'acuerdo_transporte_id','guia_id':'guia_remision_id','adelanto_id':'adelanto_transporte_id','factura_id':'factura_venta_id','registrado_por':'registrado_por_usuario_id','registrada_por':'registrado_por_usuario_id'}
maps={}
for t in P['tables']:
    maps[t]={**aliases,'id':pk(t)}
maps['pago_proveedor']['liquidacion_id']='liquidacion_proveedor_id'
for t in ['pago_transporte','aplicacion_adelanto']:maps[t]['liquidacion_id']='liquidacion_transporte_id'
def replacecols(s,m):
    return re.sub(r'\b(?:'+'|'.join(sorted(m,key=len,reverse=True))+r')\b',lambda x:m[x.group()],s)
for t in new:
    for col in P['tables'][t]:
        name,definition=col.split(' ',1); n=maps[t].get(name,name)
        definition=definition.replace('bigint','integer')
        if name=='id':definition='integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY'
        M[t]['columns'].append({'name':n,'definition':definition,'status':'TABLA NUEVA','why':'Atributo propuesto para cubrir el flujo de la vista.'})
    for u in P['uniques'][t]:M[t]['constraints'].append({'definition':'UNIQUE ('+replacecols(u,maps[t])+')','status':'NUEVA'})
    for c in P['checks'][t]:M[t]['constraints'].append({'definition':'CHECK ('+replacecols(c,maps[t])+')','status':'NUEVA'})
    addcol(t,'created_at','timestamptz NOT NULL DEFAULT now()','Auditoría con la misma convención del backend.')
    addcol(t,'updated_at','timestamptz NOT NULL DEFAULT now()','Auditoría con la misma convención del backend; el servicio/ORM actualiza esta fecha.')
for child,cc,parent,pc in P['refs']:
    if child not in new:continue
    fk(child,[maps[child].get(x,x) for x in splitcols(cc)],parent,[maps[parent].get(x,x) for x in splitcols(pc)])

# Atributos adicionales: opcionales para poder revisar y completar registros existentes.
addcol('archivo','subido_por_usuario_id','integer','Identificar quién incorporó el archivo.','usuario')
for n,d,why,p in [
('temporada','varchar(30)','Periodo o temporada de la campaña.',None),
('responsable_usuario_id','integer','Responsable de la campaña.','usuario'),
('lineamientos_archivo_id','integer','Archivo de lineamientos.','archivo'),
('observaciones','text','Notas generales de campaña.',None),
('cerrada_at','timestamptz','Fecha del cierre revisado.',None),
('cerrada_por_usuario_id','integer','Usuario que confirmó el cierre.','usuario'),
('motivo_cierre','text','Resumen o justificación del cierre.',None)]:addcol('campana',n,d,why,p)
addcol('campania_x_proveedores','participacion_proveedor_campana_id','integer','Vínculo opcional a la cabecera propuesta; revisar su necesidad al quedar la participación sin finca.','participacion_proveedor_campana')
for n,d,why,p in [
('codigo','varchar(80)','Identificador externo del certificado.',None),('norma_id','integer','Norma del certificado.','norma'),
('organismo','varchar(255)','Organismo certificador.',None),('fecha_emision','date','Fecha de emisión del certificado.',None),
('moneda','varchar(3)','Moneda del costo y de sus pagos; no se deduce automáticamente.',None),
('documento_archivo_id','integer','Documento confirmado en el almacenamiento.','archivo')]:addcol('certificado_campana',n,d,why,p)
for t in ['chofer_transporte_externo','proveedor']:
    addcol(t,'persona_id','integer','Vincular identidad compartida sin eliminar los nombres/documentos actuales.','persona')
    addcol(t,'activo','boolean NOT NULL DEFAULT true','Permitir desactivación sin borrar historial.')
addcol('chofer_transporte_externo','usuario_id','integer','Cuenta que ingresará con el rol de chofer.','usuario')
addcol('chofer_transporte_externo','numero_licencia','varchar(40)','Licencia real del conductor; completar antes de emitir documentos.')
addcol('proveedor','documento_archivo_id','integer','Documento de identidad confirmado en almacenamiento.','archivo')
for n,d,why,p in [
('coordinacion_entrega_id','integer','Identificar la entrega coordinada cuando se confirme la equivalencia.','coordinacion_entrega')]:addcol('chofer_vehiculo_externo',n,d,why,p)
addcol('cliente_negocio','fecha_registro','date','Fecha comercial de registro, si se conoce; created_at se conserva.')
for n,d,why,p in [
('ficha_tecnica_archivo_id','integer','Archivo de ficha técnica, conservando la URL actual.','archivo'),
('destino_solicitado','varchar(255)','Ciudad/planta/país solicitado en el requerimiento.',None),
('entrega_desde','date','Inicio de la ventana solicitada.',None),('entrega_hasta','date','Fin de la ventana solicitada.',None),
('observaciones','text','Requerimientos y notas comerciales.',None)]:addcol('cliente_negocio_campana',n,d,why,p)
for n,p,why in [('carga_id','carga','Carga nueva a la que corresponden los costos, solo después de revisar el viaje.'),('guia_remision_id','guia_remision','Guía estructurada, sin borrar guia_url.'),('sctr_archivo_id','archivo','Respaldo de SCTR; el dato sctr actual se conserva.')]:addcol('detalle_trazabilidad',n,'integer',why,p)
for n,d,why,p in [
('tipo_transportista',"varchar(20) NOT NULL DEFAULT 'EMPRESA'",'Diferenciar empresa e independiente; el RUC obligatorio actual todavía debe revisarse para independientes.',None),
('tipo_documento','varchar(20)','Tipo de identificación cuando se amplíe el flujo a independientes.',None),
('numero_documento','varchar(30)','Documento general; conservar el RUC actual hasta decidir su transición.',None),
('persona_id','integer','Identidad del transportista independiente.','persona'),
('registro_mtc','varchar(80)','Registro MTC cuando corresponda.',None),
('departamento','varchar(100)','Ubicación del transportista.',None),('provincia','varchar(100)','Ubicación del transportista.',None),
('ciudad','varchar(100)','Ubicación del transportista.',None),('activo','boolean NOT NULL DEFAULT true','Desactivar sin borrar historial.',None)]:addcol('empresa_transporte_externo',n,d,why,p)
for n,d,why,p in [
('fruta_derivada_id','integer','Variedad entrevistada, si se registra.','fruta_derivada'),
('distanciamiento_descripcion','varchar(60)','Expresión como 5 x 4; no sustituye automáticamente el escalar actual.',None),
('frecuencia_riego_descripcion','varchar(120)','Expresión como cada cuatro días; frecuencia actual sigue numérica.',None),
('aplicaciones_al_ano','integer','Cantidad de aplicaciones en un año; distinta de anio_aplicacion.',None),
('observaciones','text','Notas de la entrevista.',None),('archivo_id','integer','Respaldo opcional de la entrevista.','archivo'),
('registrado_por_usuario_id','integer','Responsable de la entrevista.','usuario')]:addcol('entrevista_extencion',n,d,why,p)
for n,d,why,p in [
('cxp_id','integer','Contexto de campaña/proveedor cuando se conoce.','campania_x_proveedores'),
('finca_id','integer','Finca de la muestra cuando se conoce.','finca'),
('codigo_muestra','varchar(80)','Identificador de muestra.',None),('fecha_envio','date','Fecha de envío al laboratorio.',None),
('estado_examen','varchar(30)','Estado del trámite. Resultado actual sigue obligatorio: permitir pendiente requiere otro cambio explícito.',None),
('documento_archivo_id','integer','Resultado de laboratorio confirmado en almacenamiento.','archivo')]:addcol('examen_proveedor',n,d,why,p)
for n,d,why,p in [
('codigo_lugar_produccion','varchar(60)','Código SENASA del lugar físico de producción.',None),
('codigo_catastral','varchar(60)','Código catastral de la finca.',None),('ubigeo','varchar(6)','Ubigeo de la finca.',None),
('direccion','text','Dirección física para recojo/guías.',None),('codigo_establecimiento','varchar(4)','Código de establecimiento si aplica.',None),
('fruta_derivada_id','integer','Variedad asociada a la finca.','fruta_derivada'),('edad_cultivo_anios','numeric(6,2)','Edad del cultivo expresada en años.',None)]:addcol('finca',n,d,why,p)
for n,p,why in [('coordinacion_entrega_id','coordinacion_entrega','Coordinación futura relacionada; revisar equivalencia sin agrupar por coincidencias de fechas.'),('carga_id','carga','Carga multiproveedor futura relacionada; no convierte esta fila en una carga automáticamente.')]:addcol('trazabilidad_transporte',n,'integer',why,p)
addcol('vehiculo_externo','capacidad_kg','numeric(14,3)','Capacidad útil en kg, independiente de peso_neto y peso_bruto.')
addcol('medicion_mtd','trampa_referencia','varchar(120)','Referencia textual de trampa observada en el modelo de Calidad; no se inventa un catálogo de trampas.')

extra_checks={
'campana':['fecha_fin >= fecha_inicio'],
'cliente_negocio_campana':['entrega_hasta >= entrega_desde'],
'entrevista_extencion':['aplicaciones_al_ano >= 0'],
'finca':["ubigeo IS NULL OR ubigeo ~ '^[0-9]{6}$'",'edad_cultivo_anios >= 0'],
'vehiculo_externo':['capacidad_kg > 0'],
'empresa_transporte_externo':["tipo_transportista IN ('EMPRESA','INDEPENDIENTE')"],
'certificado_campana':["moneda IS NULL OR moneda IN ('PEN','USD','EUR')"]}
for t,cs in extra_checks.items():
    for c in cs:M[t]['constraints'].append({'definition':'CHECK ('+c+')','status':'NUEVA'})

# Decisión de negocio 2026-10-27: la participación no selecciona una finca.
M['campania_x_proveedores']['columns']=[c for c in M['campania_x_proveedores']['columns'] if c['name']!='finca_id']
M['campania_x_proveedores']['indexes']=[ix for ix in M['campania_x_proveedores']['indexes'] if 'finca' not in ix]
M['campania_x_proveedores']['description']='Participación del proveedor en una campaña, sin relación directa a finca. La entrevista y los orígenes operativos identifican la finca cuando corresponde.'
F=[f for f in F if not (f['child']=='campania_x_proveedores' and 'finca_id' in f['cols'])]
# La unicidad anterior sin finca se conserva para todas las participaciones.
M['campania_x_proveedores']['constraints'].append({'name':'UQ_campania_proveedor','definition':'UNIQUE (campania_id, proveedor_id)','status':'NUEVA'})
# Las operaciones que identificaban la finca a través de cxp ahora la indican explícitamente.
for t in ['origen_entrega','origen_carga','analisis_calidad','medicion_mtd']:
    addcol(t,'finca_id','integer NOT NULL','Finca del origen o medición; ya no se obtiene de campania_x_proveedores. El servicio debe validar que pertenece al proveedor de cxp_id.','finca')
for t,cols in [('origen_entrega','coordinacion_entrega_id, cxp_id'),('origen_carga','proveedor_carga_id, cxp_id')]:
    for constraint in M[t]['constraints']:
        if constraint['definition']=='UNIQUE ('+cols+')':constraint['definition']='UNIQUE ('+cols+', finca_id)'
M['acuerdo_compra']['description']='Condiciones de compra por participación de proveedor, variedad y vigencia; no identifica una finca.'

# Decisión de negocio: archivo queda fuera del esquema; sus enlaces son pendientes.
# Análisis previo por campaña/proveedor/finca; cosecha opcional, aprobado el 27/10/2026.
for col in M['analisis_calidad']['columns']:
    if col['name']=='cosecha_id':
        col['definition']='integer'
        col['why']='Vínculo opcional posterior a una operación; el análisis puede registrarse antes de la cosecha. La campaña se obtiene de cxp_id.'
M['analisis_calidad']['description']='Muestreo previo por participación de campaña/proveedor y finca. Puede vincularse a cosecha después; no equivale al examen de admisión.'
M['certificado_campana']['description']='Certificado de campaña y su costo; el backend admite varios, aunque el editor del mockup anuncia uno. Unicidad pendiente de decisión.'
M['empresa_transporte_externo']['description']='Padrón del proveedor logístico externo; datos adicionales previstos para empresas e independientes, con RUC obligatorio actual pendiente de adaptar.'
pending_files=[copy.deepcopy(f) for f in F if f['parent']=='archivo']
for f in pending_files:
    for c in M[f['child']]['columns']:
        if c['name'] in f['cols']:
            c['definition']=c['definition'].replace(' NOT NULL','')
            c['why']='PENDIENTE DE RELACIÓN: referencia documental reservada, opcional y sin FK. No usar identificadores de archivo hasta definir la integración.'
    # No exigir identificadores inexistentes para completar un proceso.
    M[f['child']]['constraints']=[c for c in M[f['child']]['constraints'] if not any(re.search(r'\b'+re.escape(n)+r'\b',c['definition']) for n in f['cols'])]
M['recepcion_planta']['constraints'].append({'definition':'CHECK (hubo_descarte IS DISTINCT FROM true OR descarte_kg > 0)','status':'NUEVA'})
M['factura_venta']['constraints'].append({'definition':"CHECK (estado <> 'EMITIDA' OR (numero_factura IS NOT NULL AND fecha_emision IS NOT NULL))",'status':'NUEVA'})
del M['archivo']
F=[f for f in F if f['child']!='archivo' and f['parent']!='archivo']
for name in list(enums):
    if not any(qi(name) in c['definition'] for t in M.values() for c in t['columns']):del enums[name]

# Ajustes mínimos solicitados para cubrir los formularios y respuestas del usuario.
from cumplimiento_modelo import aplicar
modified_columns=aplicar(M,F,addcol,fk)
from simplificacion_modelo import aplicar as simplificar, seed_sql, REMOVED
simplificar(M,F,addcol)
initial_sql, initial_counts=seed_sql(R)
new=[t for t in new if t in M]

# Las FK compuestas del plan necesitan claves compatibles sin alterar las PK existentes.
for f in F:
    parent=M[f['parent']]
    if len(f['targets'])>1:
        cols=', '.join(f['targets'])
        if not any(c['definition']=='UNIQUE ('+cols+')' for c in parent['constraints']):parent['constraints'].append({'definition':'UNIQUE ('+cols+')','status':'NUEVA'})
for t,table in M.items():
    for col in table['columns']:
        if col['name'].endswith('_id') and col['status']!='ACTUAL' and any(col['name'] in f['cols'] and f['child']==t for f in F):
            assert col['definition'].startswith('integer'),(t,col)
for f in F:
    assert set(f['cols'])<={c['name'] for c in M[f['child']]['columns']},f
    assert set(f['targets'])<={c['name'] for c in M[f['parent']]['columns']},f

sql=['-- MODELO DOCUMENTADO PARA REVISION MANUAL. No modifica entidades TypeORM ni la base desplegada.',
'-- D08 aprobado 2026-10-29: destino de entrega como texto; guía con dirección de llegada histórica; sin catálogo de destinos.',
'-- Actualización funcional FC01-FC14: tipos/borradores, detalle JSON, recepción reconocida, ajustes y cardinalidades autorizadas.',
f'-- Instalación nueva en agro: incluye 19 tablas actuales y {len(new)} propuestas; catálogos iniciales incluidos; archivo queda excluida.',
'-- Conserva los nombres de 173 columnas actuales y adapta tipos/nulabilidad para los formularios; retira archivo y campania_x_proveedores.finca_id. Referencias documentales opcionales, sin FK, pendientes de integración.',
'-- Decisión aprobada 2026-10-27: análisis previo por participación/finca; analisis_calidad.cosecha_id es opcional. Una variedad por finca; fruta se obtiene de la variedad.',
f'-- Participación única campania_x_proveedores; retira puentes derivados y acuerdo_compra. Agrega atributos y {len(new)} tablas propuestas.',
'-- Se modifican tipos y nulabilidad legacy documentados en modified_columns; no es una migración sobre datos existentes.',
'-- No es una migración de producción. Si agro existe, se aborta. Requiere btree_gist para la exclusión actual de choferes.',
'BEGIN;','CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;','CREATE SCHEMA agro;','SET LOCAL search_path = agro, public;']
for name,values in enums.items():sql.append('CREATE TYPE '+qi(name)+' AS ENUM ('+', '.join("'"+v.replace("'","''")+"'" for v in values)+');')
for t,table in M.items():
    lines=[qi(c['name'])+' '+c['definition'] for c in table['columns']]
    for c in table['constraints']:lines.append(('CONSTRAINT '+qi(c['name'])+' ' if c.get('name') else '')+c['definition'])
    sql += [f'-- {"TABLA ACTUAL AMPLIADA" if table["existing"] else "TABLA PROPUESTA"}: {t}',f'CREATE TABLE {qi(t)} (\n  '+',\n  '.join(lines)+'\n);']
for i,f in enumerate(F,1):
    name=f.get('name') or 'fk_revision_'+str(i)
    sql.append(f'ALTER TABLE {qi(f["child"])} ADD CONSTRAINT {qi(name)} FOREIGN KEY ('+', '.join(qi(x) for x in f['cols'])+') REFERENCES '+qi(f['parent'])+' ('+', '.join(qi(x) for x in f['targets'])+') ON DELETE '+f['onDelete']+';')
for t,table in M.items():sql+= [x+';' for x in table['indexes']]
for i,f in enumerate(F,1):
    if f['status']=='NUEVA':sql.append('CREATE INDEX '+qi('ix_revision_'+str(i))+' ON '+qi(f['child'])+' ('+', '.join(qi(c) for c in f['cols'])+');')
# Conserva las funciones y triggers de entrevistas ya implementados en la novena migración.
migs=json.loads((R/'.validation/migraciones_actuales.json').read_text(encoding='utf8'))
for m in migs:
    for query in m['queries']:
        if re.search(r'CREATE\s+(FUNCTION|TRIGGER)',query,re.I):
            query=query.replace('        finca_asignacion integer;\n','')
            query=query.replace('SELECT "tipo_proveedor"::text, "proveedor_id", "finca_id"','SELECT "tipo_proveedor"::text, "proveedor_id"')
            query=query.replace('INTO tipo_asignacion, proveedor_asignacion, finca_asignacion','INTO tipo_asignacion, proveedor_asignacion')
            query=re.sub(r'        IF finca_asignacion IS NOT NULL.*?        END IF;\n','',query,flags=re.S)
            query=re.sub(r'          IF NEW\."finca_id" IS NOT NULL AND EXISTS.*?          END IF;\n','',query,flags=re.S)
            query=query.replace('BEFORE UPDATE OF "tipo_proveedor", "proveedor_id", "finca_id"','BEFORE UPDATE OF "tipo_proveedor", "proveedor_id"')
            query=re.sub(r'LANGUAGE plpgsql', 'LANGUAGE plpgsql SET search_path = agro, pg_temp',query,flags=re.I)
            sql.append(query.strip()+';')
sql += [
'''CREATE VIEW v_saldo_proveedor AS
SELECT l.*, l.importe_compra-coalesce((SELECT sum(p.monto) FROM pago_proveedor p WHERE p.liquidacion_proveedor_id=l.liquidacion_proveedor_id),0) AS saldo
FROM liquidacion_proveedor l;''',
'''CREATE VIEW v_saldo_factura AS
SELECT f.*, f.importe_venta-coalesce((SELECT sum(c.monto) FROM cobro_venta c WHERE c.factura_venta_id=f.factura_venta_id),0) AS saldo
FROM factura_venta f;''',
'''CREATE VIEW v_saldo_transporte AS
SELECT l.*, l.flete+coalesce((SELECT sum(g.monto) FROM gasto_transporte g WHERE g.carga_id=l.carga_id AND g.incluido_en_liquidacion),0)
-coalesce((SELECT sum(p.monto) FROM pago_transporte p WHERE p.liquidacion_transporte_id=l.liquidacion_transporte_id),0)
-coalesce((SELECT sum(a.monto) FROM aplicacion_adelanto a WHERE a.liquidacion_transporte_id=l.liquidacion_transporte_id),0) AS saldo
FROM liquidacion_transporte l;''',
'''CREATE VIEW v_control_uit AS
SELECT l.persona_liquidacion_id, extract(year FROM l.fecha)::integer AS anio, sum(l.importe_compra) AS acumulado,
u.valor,u.limite_uit,u.valor*u.limite_uit-sum(l.importe_compra) AS disponible
FROM liquidacion_proveedor l LEFT JOIN parametro_uit u ON u.anio=extract(year FROM l.fecha)::integer
GROUP BY l.persona_liquidacion_id,extract(year FROM l.fecha)::integer,u.valor,u.limite_uit;''',
'''CREATE VIEW v_estado_despacho AS
SELECT DISTINCT ON (coordinacion_entrega_id) coordinacion_entrega_id,carga_id,id_chofer_transporte_externo,estado,fecha_hora
FROM historial_chofer ORDER BY coordinacion_entrega_id,fecha_hora DESC,historial_chofer_id DESC;''',
'''CREATE VIEW v_programa_semanal AS
SELECT r.campania_id,r.cliente_negocio_id,c.contrato_venta_id,e.entrega_programada_id,e.fecha,
extract(isoyear FROM e.fecha)::integer AS anio_iso,extract(week FROM e.fecha)::integer AS semana_iso,
d.fruta_derivada_id,d.kilos_programados,co.id_vehiculo_externo
FROM entrega_programada e JOIN entrega_x_fruta_derivada d ON d.entrega_programada_id=e.entrega_programada_id
JOIN contrato_venta c ON c.contrato_venta_id=e.contrato_venta_id
JOIN cliente_negocio_campana r ON r.cliente_negocio_campana_id=c.cliente_negocio_campana_id
LEFT JOIN coordinacion_entrega co ON co.entrega_programada_id=e.entrega_programada_id;''']
sql.append((R/'.validation/cumplimiento_reglas.sql').read_text(encoding='utf8'))
sql.append(initial_sql)
sql+=['-- Las reglas de transición, permisos y cierre completo requieren implementación de servicio; las protecciones financieras incluidas se prueban por separado.',
'-- Solo se cargan catálogos iniciales; no se importan históricos ni se calculan pagos/contratos desde URLs o pesos.',
'REVOKE ALL ON SCHEMA agro FROM PUBLIC;','REVOKE ALL ON ALL TABLES IN SCHEMA agro FROM PUBLIC;','REVOKE ALL ON ALL FUNCTIONS IN SCHEMA agro FROM PUBLIC;','COMMIT;']
model={'tables':M,'refs':F,'existing_count':19,'new_count':len(new),'existing_columns':173,'excluded_tables':['archivo','destino_cliente_negocio']+REMOVED,'initial_data':initial_counts,'pending_file_relations':pending_files,'removed_columns':['campania_x_proveedores.finca_id','campania_x_proveedores.participacion_proveedor_campana_id'],'additional_columns':sum(c['status']=='AGREGAR' for t in M.values() for c in t['columns']),'modified_columns':modified_columns,'enums':enums}
(R/'.validation/modelo_revision.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf8')
previous=R/'.validation/03_schema_total_pre_revision_atributos.sql'
if not previous.exists():previous.write_text((R/'03_schema_total.sql').read_text(encoding='utf8'),encoding='utf8')
(R/'03_schema_total.sql').write_text('\n\n'.join(sql)+'\n',encoding='utf8')
print(f'Modelo revisado: {len(M)} tablas = {model["existing_count"]} actuales + {len(new)} propuestas; {model["additional_columns"]} atributos adicionales en tablas actuales; {len(F)} FK; archivo pendiente.')
