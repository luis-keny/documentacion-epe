from pathlib import Path
import re,json,copy
R=Path(__file__).resolve().parent.parent
renames={
'personas':'persona','roles':'rol','usuarios':'usuario','archivos':'archivo','sesiones_usuario':'sesion_usuario','parametros_uit':'parametro_uit',
'frutas':'fruta','variedades':'fruta_derivada','campanias':'campana','campania_variedades':'campana_x_fruta_derivada',
'proveedores':'proveedor','personas_proveedor':'proveedor_x_persona','proveedor_frutas':'proveedor_x_fruta','proveedor_variedades':'proveedor_x_fruta_derivada',
'fincas':'finca','certificados_propios':'certificado_proveedor','participaciones_proveedor':'participacion_proveedor_campana',
'participacion_variedades':'participacion_proveedor_x_fruta_derivada','fincas_campania':'campania_x_proveedores',
'entrevistas':'entrevista_extencion','examenes':'examen_proveedor','acuerdos_compra':'acuerdo_compra','normas':'norma',
'certificaciones':'certificado_campana','certificacion_proveedor':'certificado_campana_x_proveedor',
'ampliaciones_certificacion':'ampliacion_certificado_campana','pagos_certificacion':'pago_certificado_campana',
'clientes':'cliente_negocio','destinos_cliente':'destino_cliente_negocio',
'requerimientos_comerciales':'cliente_negocio_campana','requerimiento_variedades':'cliente_negocio_campana_x_fruta_derivada',
'contratos_venta':'contrato_venta','entregas_programadas':'entrega_programada','entrega_variedades':'entrega_x_fruta_derivada',
'empresas_transporte':'empresa_transporte_externo','vehiculos':'vehiculo_externo','choferes':'chofer_transporte_externo',
'solicitudes_transporte':'solicitud_transporte','invitaciones_transporte':'invitacion_transporte','cotizaciones_transporte':'cotizacion_transporte',
'acuerdos_transporte':'acuerdo_transporte','coordinaciones_entrega':'coordinacion_entrega','origenes_entrega':'origen_entrega',
'cosechas':'cosecha','analisis_calidad':'analisis_calidad','mediciones_mtd':'medicion_mtd','cargas':'carga',
'proveedores_carga':'proveedor_carga','origenes_carga':'origen_carga','gastos_carga':'gasto_carga',
'guias_remision':'guia_remision','proveedores_guia':'proveedor_guia','normas_guia':'guia_x_norma','historial_chofer':'historial_chofer',
'recepciones_planta':'recepcion_planta','liquidaciones_proveedor':'liquidacion_proveedor','liquidaciones_transporte':'liquidacion_transporte',
'gastos_transporte':'gasto_transporte','adelantos_transporte':'adelanto_transporte','aplicaciones_adelanto':'aplicacion_adelanto',
'facturas_venta':'factura_venta','pagos_proveedor':'pago_proveedor','pagos_transporte':'pago_transporte','cobros_venta':'cobro_venta'}
original=json.loads((R/'.validation/modelo.json').read_text(encoding='utf8'))
assert set(renames)==set(original['tables'])
assert len(set(renames.values()))==64
(R/'.validation/renombres_tablas.json').write_text(json.dumps(renames,ensure_ascii=False,indent=2),encoding='utf8')
pattern=re.compile(r'\b(?:'+'|'.join(sorted(renames,key=len,reverse=True))+r')\b')
def identifiers(text):return pattern.sub(lambda m:renames[m.group()],text)
def sql_names(sql):
    # Preserva mensajes/comentarios; cambia identificadores y nombres de tabla literales usados por triggers.
    token=re.compile(r"'(?:''|[^'])*'|--[^\n]*|\b(?:"+'|'.join(sorted(renames,key=len,reverse=True))+r')\b')
    def replace(m):
        word=m.group()
        if word.startswith('--'):return word
        if word.startswith("'"):return "'"+renames[word[1:-1]]+"'" if word[1:-1] in renames else word
        return renames.get(word,word)
    return token.sub(replace,sql)
aligned=copy.deepcopy(original)
for key in ['tables','descriptions','checks','uniques']:aligned[key]={renames[t]:v for t,v in original[key].items()}
aligned['refs']=[[renames[t],cols,renames[parent],pk] for t,cols,parent,pk in original['refs']]
(R/'.validation/modelo_alineado.json').write_text(json.dumps(aligned,ensure_ascii=False,indent=2),encoding='utf8')
audit='../../epe-backend/docs/auditoria-bd-actual-vs-planificada.md'
for filename in ['01_reporte_especifico.md','02_tablas_y_relaciones.md']:
    path=R/filename; text=path.read_text(encoding='utf8')
    baseline=R/'.validation'/('baseline-'+filename)
    if not baseline.exists():baseline.write_text(text,encoding='utf8')
    # Mermaid, nombres entre backticks y nombres compuestos en la explicación de diseño.
    text=re.sub(r'```mermaid\n.*?\n```',lambda m:identifiers(m.group()),text,flags=re.S)
    text=re.sub(r'`([^`\n]+)`',lambda m:'`'+identifiers(m.group(1))+'`',text)
    compounds={k:v for k,v in renames.items() if '_' in k}
    cp=re.compile(r'\b(?:'+'|'.join(sorted(compounds,key=len,reverse=True))+r')\b')
    text=cp.sub(lambda m:compounds[m.group()],text)
    text=text.replace('Los nombres son tablas propuestas, no nombres confirmados del backend actual.', 'Los nombres existentes se verificaron en las entidades locales; las tablas adicionales son propuestas. No se afirma que existan en una base desplegada.')
    # La comparación histórica con el DBML mantiene la nomenclatura original en su columna izquierda.
    if filename.startswith('01_'):
        old_dbml=re.findall(r'^Table (\w+) \{',Path('C:/Users/luisl/Downloads/AGRO_SIMPLIFICADO.dbml').read_text(encoding='utf8'),re.M)
        start=text.index('**Verificación de las 42 tablas');end=text.index('**Entidades añadidas',start)
        block=text[start:end];rows=list(re.finditer(r'^\| `[^`]+` \|',block,re.M))
        assert len(rows)==42
        for match,name in reversed(list(zip(rows,old_dbml))):block=block[:match.start()]+f'| `{name}` |'+block[match.end():]
        text=text[:start]+block+text[end:]
    note=f'**Nomenclatura revisada contra el backend local:** se conservan los nombres existentes cuando representan la misma entidad; las tablas nuevas siguen su convención en singular. El esquema objetivo sigue siendo una propuesta, con cambios estructurales pendientes. Consulta la [auditoría de base actual frente al plan]({audit}) para el inventario actual, el mapeo completo y las diferencias que no se resuelven cambiando nombres.\n\n'
    title_end=text.index('\n\n')+2
    text=text[:title_end]+note+text[title_end:]
    path.write_text(text,encoding='utf8')
sqlpath=R/'03_schema_total.sql';sql=sqlpath.read_text(encoding='utf8')
baseline=R/'.validation/baseline-03_schema_total.sql'
if not baseline.exists():baseline.write_text(sql,encoding='utf8')
sql=sql_names(sql)
sql='-- Nombres alineados con las entidades locales; columnas y relaciones representan el MODELO OBJETIVO.\n-- No es una migración ni un reemplazo compatible con las entidades TypeORM actuales.\n'+sql
sqlpath.write_text(sql,encoding='utf8')
current=json.loads((R/'.validation/modelo_actual.json').read_text(encoding='utf8'))
shared=set(renames.values())&{x['table'] for x in current}
print(f'Nomenclatura alineada: {len(shared)} nombres existentes conservados; {64-len(shared)} tablas objetivo nuevas; {len(current)-len(shared)} tablas actuales requieren descomposición, no renombrado directo.')
