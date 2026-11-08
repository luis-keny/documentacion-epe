"""Decisión del 29/10: una participación, catálogos seed y opciones constantes."""
import json
import re

REMOVED = ['campana_x_fruta_derivada', 'participacion_proveedor_x_fruta_derivada',
           'participacion_proveedor_campana', 'acuerdo_compra', 'sesion_usuario']


def aplicar(M, F, addcol):
    # Se preservan la PK legacy y los atributos ya equivalentes: tipo_proveedor,
    # cantidad_proveedor, estado, created_at, precio y observaciones.
    M['campania_x_proveedores']['columns'] = [c for c in M['campania_x_proveedores']['columns']
                                             if c['name'] != 'participacion_proveedor_campana_id']
    addcol('campania_x_proveedores', 'entrevista_aplica', 'boolean NOT NULL DEFAULT true',
           'Consolidación: conserva el indicador de entrevista de la cabecera retirada; el servicio lo confirma según el proveedor.')
    M['campania_x_proveedores']['description'] = 'Única participación proveedor/campaña, identificada por cxp_id; conserva oferta, tipo, evaluación, entrevista aplicable, precio simple PEN y disponibilidad.'
    # Se remapean también los targets de la FK compuesta de cobertura.
    for table in ['certificado_campana_x_proveedor', 'proveedor_carga']:
        for c in M[table]['columns']:
            if c['name'] == 'participacion_proveedor_campana_id':
                c.update(name='cxp_id', why='Participación única en campania_x_proveedores; no existe cabecera duplicada.')
        for c in M[table]['constraints']:
            c['definition'] = c['definition'].replace('participacion_proveedor_campana_id', 'cxp_id')
        M[table]['indexes'] = [i.replace('participacion_proveedor_campana_id','cxp_id') for i in M[table]['indexes']]
    for f in F:
        if f['child'] in ['certificado_campana_x_proveedor', 'proveedor_carga'] and f['parent']=='participacion_proveedor_campana':
            f['parent']='campania_x_proveedores'
            f['cols']=['cxp_id' if c=='participacion_proveedor_campana_id' else c for c in f['cols']]
            f['targets']=['cxp_id' if c=='participacion_proveedor_campana_id' else c for c in f['targets']]
    for table in REMOVED:
        del M[table]
    F[:] = [f for f in F if f['child'] in M and f['parent'] in M]
    addcol('certificado_campana','tipo_certificacion','varchar(80)',
           'Opción fija del formulario, distinta de nombre y de norma_id; nullable para fichas aún incompletas. No se crea tabla de tipos.')
    M['certificado_campana']['constraints'].append({'definition':"CHECK (tipo_certificacion IN ('Global GAP','Orgánico USDA','Orgánico UE','Fairtrade','Rainforest Alliance'))",'status':'NUEVA'})
    addcol('cotizacion_transporte','disponibilidad','text',
           'Texto del editor de respuesta de transporte; sin inventar disponibilidad al registrar la cotización.')
    M['norma']['description']='Catálogo con datos iniciales SQL de códigos de guía; sin CRUD requerido. Se relaciona con guías mediante guia_x_norma y opcionalmente con certificados, sin confundir el tipo de certificado.'
    M['guia_x_norma']['description']='Normas elegidas en el editor de cada guía; se insertan/eliminan sus filas al guardar un borrador, resolviendo norma_id por codigo. No se precargan relaciones para todas las guías. UNIQUE evita duplicar selecciones.'
    M['rol']['description']='Perfiles extensibles con Administrador y Chofer iniciales mediante SQL; no requiere CRUD de perfiles en el alcance actual.'
    M['parametro_uit']['description']='Configuración anual con datos iniciales del prototipo y umbral; ampliable mediante SQL sin CRUD. Cada liquidación conserva los parámetros realmente aplicados.'


def seed_sql(root):
    src = root.parent / 'prototipo/Campaign Management System/src'
    text=(src/'store.tsx').read_text(encoding='utf-8')
    block=text.split('export const FRUIT_CATALOG:',1)[1].split('\n}',1)[0]
    fruit=[]
    for name, values in re.findall(r"^  ([^:]+): \[([^\]]+)\]",block,re.M):
        fruit.append((name.strip(),re.findall(r"'([^']+)'",values)))
    norms = re.findall(r"\{code:'([^']+)',label:'([^']+)'",(src/'remission-model.ts').read_text(encoding='utf-8'))
    uittext=(src/'purchase-uit.ts').read_text(encoding='utf-8')
    years=[(int(y),int(v)) for y,v in re.findall(r'(\d{4}):(\d+)',uittext.split('export const UIT_VALUES',1)[1].split('\n',1)[0])]
    count=int(re.search(r'UIT_COUNT\s*=\s*(\d+)',uittext).group(1))
    assert len(fruit)==5 and sum(len(v) for _,v in fruit)==17 and len(norms)==5 and len(years)==2
    q=lambda s:"'"+str(s).replace("'","''")+"'"
    rows=['-- Catálogos iniciales del prototipo local (29/10/2026), sin usuarios demo ni movimientos.',
          '-- Reejecutable en mantenimiento controlado; no sobrescribe valores existentes.',
          '-- UIT: valores observados en código, no certificación de vigencia normativa. Revisar al habilitar otro año.',
          "INSERT INTO rol(nombre) VALUES ('Administrador'), ('Chofer') ON CONFLICT (nombre) DO NOTHING;",
          'INSERT INTO norma(codigo,nombre) VALUES '+', '.join('('+q(c)+','+q(n)+')' for c,n in norms)+' ON CONFLICT (codigo) DO NOTHING;']
    for name, varieties in fruit:
        rows.append('INSERT INTO fruta(name) SELECT '+q(name)+' WHERE NOT EXISTS (SELECT 1 FROM fruta WHERE name='+q(name)+');')
        for value in varieties:
            rows.append('INSERT INTO fruta_derivada(name,fruta_id) SELECT '+q(value)+', f.fruta_id FROM fruta f WHERE f.name='+q(name)+' AND NOT EXISTS (SELECT 1 FROM fruta_derivada d WHERE d.fruta_id=f.fruta_id AND d.name='+q(value)+');')
    rows.append('INSERT INTO parametro_uit(anio,valor,limite_uit,umbral_alerta) VALUES '+', '.join(f'({y},{v},{count},0.90)' for y,v in years)+' ON CONFLICT (anio) DO NOTHING;')
    rows.append('-- guia_x_norma queda vacía: sus filas nacen de selecciones reales de cada guía, nunca de este seed.')
    body='\n\n'.join(rows)
    (root/'04_datos_iniciales.sql').write_text('BEGIN;\nSET LOCAL search_path = agro, public;\n\n'+body+'\n\nCOMMIT;\n',encoding='utf-8')
    return body, {'roles':2,'normas':len(norms),'frutas':len(fruit),'variedades':sum(len(v) for _,v in fruit),'parametros_anuales':len(years)}
