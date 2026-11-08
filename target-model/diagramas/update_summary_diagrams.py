"""Sincroniza el resumen Archify conservando sus recortes y composición."""
from pathlib import Path
from collections import defaultdict
import json
import re
import build_view_diagrams as schema

root=Path(__file__).resolve().parent
for path in [root/'schema-global.erd.json', *sorted((root/'views').glob('*.erd.json'))]:
    data=json.loads(path.read_text(encoding='utf-8'))
    data['entities']=[e for e in data['entities'] if e['id'] in schema.tables]
    ids={e['id'] for e in data['entities']}
    for view in data.get('meta',{}).get('views',[]):
        view['focus']=[t for t in view['focus'] if t in ids]
    groups=defaultdict(list)
    for entity in data['entities']:
        name=entity['id']; entity['sublabel']=schema.status[name]
        attrs=[]
        for c in schema.tables[name]['columns']:
            a={'name':c['name'],'type':c['type']}
            if c['keys']:a['key']=[k.lower() for k in c['keys']]
            if c['refs']:a['references']=c['refs'][0]
            attrs.append(a)
        entity['attributes']=attrs
        entity['width']=max(340,len(name)*8+40,*[len(a['name'])*7+len(a['type'])*6+100 for a in attrs])
        groups[(entity.get('tag',''),entity.get('col',0))].append(entity)
    offsets=[0,0]
    for index,group in enumerate(groups.values()):
        col=index if path.name=='schema-global.erd.json' else index%2
        for row,entity in enumerate(sorted(group,key=lambda e:e.get('row',0))):
            entity['row']=row if path.name=='schema-global.erd.json' else offsets[col]+row
            entity['col']=col
        if path.name!='schema-global.erd.json':offsets[col]+=len(group)+1
    data['relationships']=[r for r in data['relationships'] if r['from'] in ids and r['to'] in ids]
    for card in data.get('cards',[]):
        card['items']=[s.replace('65 tablas y 134','60 tablas y 124').replace('61 tablas y 125','60 tablas y 124') for s in card.get('items',[])]
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

path=root/'candidate.archify.md'
s=path.read_text(encoding='utf-8').replace('65 tablas','60 tablas').replace('61 tablas','60 tablas').replace('134 claves','124 claves').replace('125 claves','124 claves').replace('134 FK','124 FK').replace('125 FK','124 FK').replace('46 tablas propuestas','41 tablas propuestas').replace('42 tablas propuestas','41 tablas propuestas').replace('27/10/2026"','29/10/2026"')
s=re.sub(r'^@diagram erd id=global-erd-diagram.*$', '[Abrir el ERD global con los 685 atributos y las 124 FK](source:vistas)',s,flags=re.M)
intro='La decisión D08 del 29/10/2026 retira el catálogo de destinos: no existe CRUD propio en el prototipo. La entrega conserva `destino text NOT NULL` y la guía sus campos de llegada.'
addition='\n\nLa participación queda en `campania_x_proveedores`; se retiran la cabecera duplicada, dos puentes de variedades calculadas y `acuerdo_compra`.\n\nLos catálogos reciben datos iniciales SQL: dos perfiles, cinco normas, cinco frutas, 17 variedades y parámetros anuales del prototipo. La moneda y los demás selectores fijos no generan tablas adicionales.\n\n`guia_x_norma` conserva solo las normas elegidas al guardar cada guía; el catálogo inicial no crea asignaciones. El texto emitido queda como snapshot en `guia_remision.contenido`.'
if addition not in s:s=s.replace(intro,intro+addition)
s=s.replace('693 atributos y las 124 FK','685 atributos y las 124 FK')
note='La tabla `sesion_usuario` se retira por decisión expresa: no se gestionan tokens, vencimientos ni revocaciones mediante sesiones propias. `usuario` y `rol` permanecen.'
if note not in s:s=s.replace('## ¿Qué calculan las seis vistas SQL?',note+'\n\n## ¿Qué calculan las seis vistas SQL?')
lines=s.splitlines()
titles={v['ref']:v['title'] for v in schema.sections}
for i,line in enumerate(lines):
    m=re.match(r'\| \*\*(V\d+) · ',line)
    if not m:continue
    ref=m.group(1);v=schema.view_info[ref];groups=defaultdict(list)
    for r in v['rows']:
        status='A' if r['state']=='Actual' else ('D' if r['state']=='Por discutir' else 'P')
        role='E' if r['usage']=='Escritura esperada' else ('C' if r['usage']=='Consulta' else 'D')
        groups[status+'/'+role].append('`'+r['name']+'`')
    tags='; '.join('**'+key+':** '+', '.join(values) for key,values in groups.items()) or 'Sin tabla de negocio; navegación.'
    brief=lambda text:' '.join(text.replace('|','/').split()[:18])
    lines[i]=f"| **{ref} · {titles[ref]}** | **Acción:** {brief(v['action'])}. **Pantalla:** {brief(v['observed'])}. | {tags} |"
path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Resumen y cuatro fuentes ERD sincronizados: 60 tablas / 124 FK.')
