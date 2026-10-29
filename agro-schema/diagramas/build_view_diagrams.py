from pathlib import Path
import re, html, json, collections
from audit_panel import load_audit, audit_tag, CSS as audit_css, JS as audit_js
script_dir=Path(__file__).resolve().parent
base=script_dir.parents[2]
outdir=script_dir
map_path=base/'docs/agro-schema/02_tablas_y_relaciones.md'
report_path=base/'docs/agro-schema/01_reporte_especifico.md'
sql_path=base/'docs/agro-schema/03_schema_total.sql'
map_text=map_path.read_text(encoding='utf-8')
report_text=report_path.read_text(encoding='utf-8')
sql_text=sql_path.read_text(encoding='utf-8')
audit_rows,audit_panel=load_audit(report_path.parent,sql_path)

# The SQL comments define the 19 existing tables; the rest are proposed in this target schema.
status={m.group(1):('Actual' if 'ACTUAL AMPLIADA' in m.group(0) else 'Propuesta') for m in re.finditer(r'(?m)^-- TABLA (?:ACTUAL AMPLIADA|PROPUESTA): ([^\r\n]+)',sql_text)}

# Read the complete physical column definitions from the current SQL.
# View topology remains sourced from the per-view Mermaid blocks.
tables={}
for match in re.finditer(r'(?m)^CREATE TABLE "([^"]+)" \(\n(.*?)^\);',sql_text,re.S):
    name,body=match.groups()
    columns=[]; primary=[]; unique_groups=[]
    for line in body.splitlines():
        text=line.strip().rstrip(',')
        cm=re.match(r'"([^"]+)"\s+(.+)',text)
        if cm:
            column,definition=cm.groups()
            sqltype=re.split(r'\s+(?=NOT NULL\b|NULL\b|DEFAULT\b|GENERATED\b|PRIMARY KEY\b|UNIQUE\b|CHECK\b|REFERENCES\b)',definition,1)[0]
            default=re.search(r'\bDEFAULT\s+(.+)',definition)
            columns.append({'name':column,'type':sqltype,'required':'NOT NULL' in definition or 'PRIMARY KEY' in definition,'definition':definition,'default':default.group(1) if default else ('IDENTITY' if 'GENERATED' in definition else '—'),'keys':[],'refs':[],'unique_groups':[]})
            if 'PRIMARY KEY' in definition: primary.append(column)
            if re.search(r'\bUNIQUE\b',definition): unique_groups.append([column])
        pm=re.search(r'PRIMARY KEY\s*\(([^)]+)\)',text)
        if pm: primary.extend(x.strip().strip('"') for x in pm.group(1).split(','))
        for um in re.finditer(r'UNIQUE\s*\(([^)]+)\)',text):
            unique_groups.append([x.strip().strip('"') for x in um.group(1).split(',')])
    tables[name]={'columns':columns,'primary':set(primary),'unique_groups':unique_groups}

for match in re.finditer(r'CREATE UNIQUE INDEX "([^"]+)" ON (?:agro\.)?"?([A-Za-z_][A-Za-z_0-9]*)"? USING btree \(([^)]+)\)([^;]*);',sql_text):
    index,table,fields,condition=match.groups()
    if table in tables:
        group=[x.strip().strip('"') for x in fields.split(',')]
        tables[table]['unique_groups'].append(group)
        for c in tables[table]['columns']:
            if c['name'] in group and condition.strip(): c['unique_groups'].append(index+': '+condition.strip())

fk_count=0
for match in re.finditer(r'ALTER TABLE "([^"]+)" ADD CONSTRAINT "([^"]+)" FOREIGN KEY \(([^)]+)\) REFERENCES "([^"]+)" \(([^)]+)\)',sql_text):
    source,constraint,fields,target,target_fields=match.groups(); fk_count+=1
    for field,target_field in zip(re.findall(r'"([^"]+)"',fields),re.findall(r'"([^"]+)"',target_fields)):
        column=next(c for c in tables[source]['columns'] if c['name']==field)
        ref=f'{target}.{target_field}'
        if ref not in column['refs']: column['refs'].append(ref)
for table,data in tables.items():
    for column in data['columns']:
        if column['name'] in data['primary']:
            column['keys'].append('PK'); column['required']=True
        if column['refs']: column['keys'].append('FK')
        for group in data['unique_groups']:
            if column['name'] in group:
                if 'UK' not in column['keys']: column['keys'].append('UK')
                text='UNIQUE ('+', '.join(group)+')'
                if text not in column['unique_groups']: column['unique_groups'].append(text)
assert len(tables)==60 and fk_count==124, 'El inventario SQL cambió: revisar el lector de columnas y FK.'
column_count=sum(len(t['columns']) for t in tables.values())

def column_height(column):
    return 38+14*len(column['refs'])

def table_size(name):
    columns=tables[name]['columns']
    lengths=[len(name)*7+36]
    for c in columns:
        lengths.extend([len(c['name'])*7+120,len(c['type']+' · '+('NOT NULL' if c['required'] else 'NULL'))*6.1+36])
        lengths.extend(len('→ '+ref)*6.1+36 for ref in c['refs'])
    width=int(max(510,*lengths))
    return width,76+sum(column_height(c) for c in columns)+9

def attributes_html(nodes):
    sections=[]
    for name in sorted(nodes):
        rows=[]
        for c in tables[name]['columns']:
            refs='<br>'.join(html.escape(ref) for ref in c['refs']) or '—'
            keys=' · '.join(c['keys']) or '—'
            unique='; '.join(c['unique_groups'])
            rows.append(f'<tr><th scope="row"><code>{html.escape(c["name"])}</code></th><td><code>{html.escape(c["type"])}</code></td><td>{"NOT NULL" if c["required"] else "NULL"}</td><td title="{html.escape(unique)}">{keys}</td><td><code>{refs}</code></td><td><code>{html.escape(c["default"])}</code></td></tr>')
        sections.append(f'<h4><code>{html.escape(name)}</code> <small>{len(tables[name]["columns"])} atributos</small></h4><div class="dictionary-scroll"><table><thead><tr><th>Atributo</th><th>Tipo SQL</th><th>Nulabilidad</th><th>Claves</th><th>Referencia FK</th><th>Default / generación</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    return '<details class="attribute-dictionary"><summary>Consultar el diccionario completo de atributos de esta vista</summary>'+''.join(sections)+'</details>'

def parse_er(block):
    lines=block.splitlines()
    nodes=set(); edges=[]
    pattern=re.compile(r'^\s*([A-Za-z_][A-Za-z_0-9]*)\s+(\|\||o\||\|o|\|\{|\}\||o\{|\}o)\.\.(\|\||o\||\|o|\|\{|\}\||o\{|\}o)\s+([A-Za-z_][A-Za-z_0-9]*)(?:\s*:\s*(.*?))?\s*$')
    for line in lines[1:]:
        s=line.strip()
        if not s: continue
        m=pattern.match(line)
        if m:
            a,left,right,b,label=m.groups()
            nodes.update((a,b))
            edges.append({'a':a,'b':b,'left':left,'right':right,'label':(label or '').strip()})
        elif re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',s):
            nodes.add(s)
    return sorted(nodes),edges

def endpoint_label(tok):
    return {'||':'1','o|':'0..1','|o':'0..1','|{':'1..N','}|':'1..N','o{':'0..N','}o':'0..N'}.get(tok,tok)

def layout(nodes,edges):
    if not nodes: return {},400,200
    adj={n:set() for n in nodes}
    for e in edges:
        adj[e['a']].add(e['b']); adj[e['b']].add(e['a'])
    unvisited=set(nodes); cells={}; component_offset=0
    while unvisited:
        root=max(unvisited,key=lambda n:(len(adj[n]),n))
        dist={root:0}; queue=[root]; comp=[]
        while queue:
            n=queue.pop(0); comp.append(n)
            for other in sorted(adj[n]):
                if other not in dist: dist[other]=dist[n]+1; queue.append(other)
        unvisited.difference_update(comp)
        levels=collections.defaultdict(list)
        for n in comp: levels[dist[n]].append(n)
        for d in levels: levels[d].sort(key=lambda n:(-len(adj[n]),n))
        for _ in range(4):
            for d in range(1,max(levels.keys(),default=0)+1):
                prev={n:i for i,n in enumerate(levels[d-1])}
                levels[d].sort(key=lambda n:(sum(prev[x] for x in adj[n] if x in prev)/max(1,sum(x in prev for x in adj[n])),n))
            for d in range(max(levels.keys(),default=0)-1,-1,-1):
                nxt={n:i for i,n in enumerate(levels[d+1])} if d+1 in levels else {}
                if nxt: levels[d].sort(key=lambda n:(sum(nxt[x] for x in adj[n] if x in nxt)/max(1,sum(x in nxt for x in adj[n])),n))
        maxrows=max((len(v) for v in levels.values()),default=1)
        for d,items in levels.items():
            for row,n in enumerate(items): cells[n]=(d,component_offset+row)
        component_offset+=maxrows+1
    widths={}; heights={}
    for n,(col,row) in cells.items():
        w,h=table_size(n); widths[col]=max(widths.get(col,0),w); heights[row]=max(heights.get(row,0),h)
    xs={}; cursor=70
    for col in range(max(widths)+1): xs[col]=cursor; cursor+=widths.get(col,0)+140
    ys={}; bottom=70
    for row in range(max(heights)+1): ys[row]=bottom; bottom+=heights.get(row,0)+90
    return {n:(xs[col],ys[row]) for n,(col,row) in cells.items()},cursor,bottom

def svg_graph(nodes,edges,view=False):
    assert all(n in tables for n in nodes), 'Hay tablas de la vista que no existen en el SQL.'
    pos,width,height=layout(nodes,edges)
    out=[f'<svg class="erd" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Diagrama ER con {len(nodes)} tablas, todos sus atributos y {len(edges)} relaciones">','<g class="edges">']
    for e in edges:
        x1,y1=pos[e['a']]; x2,y2=pos[e['b']]
        w1,h1=table_size(e['a']); w2,h2=table_size(e['b'])
        if x2>x1:
            sx,sy=x1+w1,y1+38; tx,ty=x2,y2+38
            bend=max(42,abs(tx-sx)*.34); c1=(sx+bend,sy); c2=(tx-bend,ty)
        elif x2<x1:
            sx,sy=x1,y1+38; tx,ty=x2+w2,y2+38
            bend=max(42,abs(tx-sx)*.34); c1=(sx-bend,sy); c2=(tx+bend,ty)
        elif y2>=y1:
            sx,sy=x1+w1,y1+38; tx,ty=x2+w2,y2+38
            corridor=max(sx,tx)+65; c1=(corridor,sy); c2=(corridor,ty)
        else:
            sx,sy=x1,y1+38; tx,ty=x2,y2+38
            corridor=min(sx,tx)-50; c1=(corridor,sy); c2=(corridor,ty)
        label=e['label'].lower(); kind='actual' if label=='actual' else 'propuesta'
        title=f"{e['a']} {e['left']} · {label or 'relación'} · {e['right']} {e['b']}"
        d=f'M {sx:.1f},{sy:.1f} C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {tx:.1f},{ty:.1f}'
        out.append(f'<path class="edge {kind}" d="{d}"><title>{html.escape(title)}</title></path>')
        if view and e['label']:
            out.append(f'<text class="edge-label {kind}" x="{(sx+tx)/2:.1f}" y="{(sy+ty)/2-8:.1f}">{html.escape(e["label"])}</text>')
        for xx,yy,tok,side in [(sx,sy,e['left'],'source'),(tx,ty,e['right'],'target')]:
            dx=12 if side=='source' and x2>=x1 or side=='target' and x2<x1 else -12
            out.append(f'<text class="cardinality" x="{xx+dx:.1f}" y="{yy-8:.1f}" text-anchor="{"start" if dx>0 else "end"}">{html.escape(endpoint_label(tok))}</text>')
    out.append('</g><g class="nodes">')
    for n in nodes:
        x,y=pos[n]; w,h=table_size(n); data=tables[n]; state=status[n]; kind='actual' if state=='Actual' else 'propuesta'
        out.append(f'<g class="node {kind}" data-table="{n}" transform="translate({x},{y})"><title>{html.escape(n)} · {len(data["columns"])} atributos</title><rect width="{w}" height="{h}" rx="12"/><rect class="node-accent" width="5" height="{h}" rx="2"/><text class="node-label" x="18" y="28">{html.escape(n)}</text><text class="node-status" x="18" y="49">{state.upper()} · {len(data["columns"])} ATRIBUTOS</text><text class="column-hint" x="18" y="66">ATRIBUTO / TIPO SQL Y NULABILIDAD</text>')
        cy=76
        for i,c in enumerate(data['columns']):
            rh=column_height(c); required='NOT NULL' if c['required'] else 'NULL'
            detail=c['definition']
            if c['refs']: detail+=' | FK: '+', '.join(c['refs'])
            if c['unique_groups']: detail+=' | '+'; '.join(c['unique_groups'])
            out.append(f'<g class="attribute-row" data-column="{html.escape(c["name"])}"><title>{html.escape(detail)}</title><rect class="attribute-background {"alternate" if i%2==0 else ""}" x="7" y="{cy}" width="{w-14}" height="{rh}"/><text class="attribute-name" x="18" y="{cy+14}">{html.escape(c["name"])}</text><text class="attribute-keys" x="{w-16}" y="{cy+14}" text-anchor="end">{" · ".join(c["keys"])}</text><text class="attribute-type" x="18" y="{cy+29}">{html.escape(c["type"])} · {required}</text>')
            for j,ref in enumerate(c['refs']): out.append(f'<text class="attribute-reference" x="18" y="{cy+43+j*14}">→ {html.escape(ref)}</text>')
            out.append('</g>'); cy+=rh
        assert cy+9==h, f'Altura incorrecta de {n}'
        out.append('</g>')
    out.append('</g></svg>')
    return ''.join(out)

def split_sections(text):
    return re.split(r'(?m)^## ',text)[1:]

# Prototype screen descriptions and per-table usage tags.
view_info={}
for part in split_sections(report_text):
    refm=re.search(r'\*\*Referencia de revisión:\*\*\s*(V\d+)',part)
    if not refm: continue
    ref=refm.group(1)
    actionm=re.search(r'\*\*Entrada, acciones y salida:\*\*\s*(.*)',part)
    obsm=re.search(r'\*\*Observado en la aplicación de referencia:\*\*\s*(.*)',part)
    block=re.search(r'\*\*Funcionalidad esperada de cada tabla en esta vista:\*\*\s*\n\n(.*?)(?:\n\n\*\*Esquema de relaciones|\n\n## |\Z)',part,re.S)
    rows=[]
    if block:
        for line in block.group(1).splitlines():
            if not line.startswith('|') or line.startswith('| Tabla') or line.startswith('|---') or line.startswith('| ---'): continue
            cells=[x.strip() for x in line.strip().strip('|').split('|')]
            if len(cells)<4: continue
            nm=re.search(r'`([^`]+)`',cells[0])
            if not nm: continue
            usage=cells[1]; status_text=cells[3].lower()
            if 'actual incluida' in status_text: state='Actual'
            elif 'discutir' in status_text or 'por discutir' in usage.lower(): state='Por discutir'
            else: state='Propuesta'
            rows.append({'name':nm.group(1),'state':state,'usage':usage})
    obs=obsm.group(1).strip() if obsm else 'La ficha no describe un modal o formulario de datos.'
    if 'modal' in obs.lower(): surface='Modal observado'
    elif 'formulario' in obs.lower(): surface='Formulario observado'
    else: surface='Vista observada'
    view_info[ref]={'action':actionm.group(1).strip() if actionm else '—','observed':obs,'surface':surface,'rows':rows}

sections=[]
global_match=re.search(r'```mermaid\s*\n(.*?)```',map_text,re.S)
global_graph=parse_er(global_match.group(1)) if global_match else None
for part in split_sections(map_text):
    heading=part.splitlines()[0]
    blocks=re.findall(r'```mermaid\s*\n(.*?)```',part,re.S)
    refm=re.search(r'\*\*Referencia:\*\*\s*(V\d+)',part)
    if not refm:
        for block in blocks:
            if block.splitlines()[0].strip()=='erDiagram': global_graph=parse_er(block)
        continue
    ref=refm.group(1)
    title=heading.split(' (')[0]
    diagram=None
    for block in blocks:
        if block.splitlines()[0].strip()=='erDiagram':
            diagram=parse_er(block); break
    sections.append({'ref':ref,'title':title,'diagram':diagram})

assert global_graph is not None, 'No se encontró el ERD global en el Markdown.'
assert sum(1 for v in status.values() if v=='Actual')==19 and sum(1 for v in status.values() if v=='Propuesta')==41, 'El SQL debe contener 19 tablas actuales y 41 propuestas.'
assert len(sections)==62, f'El Markdown debe aportar 62 vistas, halladas {len(sections)}'
assert sum(bool(s['diagram']) for s in sections)==61, 'Se esperaba V02 como la única vista sin diagrama de entidades.'

def tags_html(rows):
    if not rows: return '<span class="tag none">Sin tabla de negocio · navegación del prototipo</span>'
    labels={'Escritura esperada':'Escritura','Consulta':'Consulta','Por discutir':'Por discutir'}
    out=[]
    for r in rows:
        st='actual' if r['state']=='Actual' else ('pending' if r['state']=='Por discutir' else 'propuesta')
        role=labels.get(r['usage'],r['usage'])
        out.append(f'<span class="tag {st}" title="{html.escape(r["state"]+" · "+r["usage"])}"><b>{html.escape(r["state"])}</b><code>{html.escape(r["name"])}</code><small>{html.escape(role)}</small>{audit_tag(audit_rows.get(r["name"]))}</span>')
    return ''.join(out)

global_svg=svg_graph(*global_graph,view=False)
module_groups=[('01–20','Comercial y campañas'),('21–30','Proveedores y transporte'),('31–40','Cosecha y logística'),('41–52','Facturación y liquidaciones'),('53–62','Aplicación del chofer')]
parts=[]
for item in sections:
    ref,title,diagram=item['ref'],item['title'],item['diagram']; info=view_info.get(ref,{'action':'—','observed':'No se registró interacción.','surface':'Vista','rows':[]})
    group=next(label for rng,label in module_groups if int(ref[1:])<=int(rng.split('–')[1]))
    if diagram:
        nodes,edges=diagram; chart=svg_graph(nodes,edges,view=True)
        diagram_html=f'<div class="diagram-toolbar"><span>{len(nodes)} tablas · {len(edges)} relaciones del Markdown</span><button class="zoom-in" type="button" aria-label="Aumentar diagrama">+</button><button class="zoom-out" type="button" aria-label="Reducir diagrama">−</button><button class="zoom-reset" type="button">100%</button><button class="zoom-fit" type="button">Ajustar ancho</button></div><div class="diagram-scroll">{chart}</div>{attributes_html(nodes)}'
    else:
        diagram_html='<div class="no-schema"><strong>Sin ERD de negocio en el Markdown base.</strong><p>V02 describe navegación entre módulos y permisos; no define tablas propias para esa pantalla.</p></div>'
    parts.append(f'''<details class="view-card" id="{ref.lower()}" data-group="{html.escape(group)}" data-title="{html.escape((ref+' '+title).lower())}" {'open' if ref=='V01' else ''}>
<summary><span class="view-number">{ref}</span><span class="view-title">{html.escape(title)}</span><span class="view-count">{len(diagram[0]) if diagram else 0} tablas</span></summary>
<div class="view-body"><div class="interaction"><div><span class="eyebrow">Ruta y acción</span><p>{html.escape(info['action'])}</p></div><div><span class="eyebrow">{html.escape(info['surface'])}</span><p>{html.escape(info['observed'])}</p></div></div><div class="table-tags"><span class="eyebrow">Tablas usadas por esta vista, modal o formulario</span><div class="tags">{tags_html(info['rows'])}</div></div>{diagram_html}</div></details>''')

html_doc=f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark light"><title>Esquema agroexportador · por vistas</title>
<style>
:root{{--bg:#091311;--surface:#0f201c;--panel:#122620;--line:#25453a;--text:#e6f1eb;--muted:#9bb1a6;--green:#47d2a3;--amber:#f0bc67;--blue:#76bde8;--red:#d78f75;--chip:#1a342c;--shadow:0 20px 60px #0005}}
:root.light{{--bg:#f0f5f1;--surface:#fff;--panel:#f7faf8;--line:#d9e5dd;--text:#183128;--muted:#587067;--green:#087f5b;--amber:#98620e;--blue:#276f9c;--red:#9c4f37;--chip:#eef5f0;--shadow:0 14px 40px #17443012}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at top left,#12352b 0,transparent 42%),var(--bg);color:var(--text);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}}a{{color:var(--green)}}button,input{{font:inherit;color:inherit}}.shell{{max-width:1500px;margin:auto;padding:24px clamp(16px,4vw,56px) 80px}}header{{display:flex;justify-content:space-between;align-items:center;gap:20px}}.brand{{font-size:12px;text-transform:uppercase;letter-spacing:.18em;color:var(--green);font-weight:750}}h1{{font-size:clamp(32px,4.5vw,58px);line-height:1.04;letter-spacing:-.04em;margin:14px 0}}.lead{{max-width:850px;color:var(--muted);font-size:17px}}.top-actions{{display:flex;gap:8px;align-items:center}}.button{{border:1px solid var(--line);background:var(--panel);padding:9px 13px;border-radius:10px;cursor:pointer}}.button:hover{{border-color:var(--green)}}.stats{{display:flex;flex-wrap:wrap;gap:10px;margin:25px 0}}.stat{{border:1px solid var(--line);background:var(--surface);padding:9px 13px;border-radius:12px;color:var(--muted)}}.stat b{{color:var(--text)}}.global{{margin:28px 0 42px;border:1px solid var(--line);border-radius:20px;background:var(--surface);box-shadow:var(--shadow);overflow:hidden}}.global summary{{cursor:pointer;padding:18px 22px;font-size:20px;font-weight:700}}.global .inside{{padding:0 18px 22px}}.legend{{display:flex;flex-wrap:wrap;gap:9px;color:var(--muted);font-size:12px;padding:4px 0 12px}}.legend span{{display:inline-flex;align-items:center;gap:6px}}.swatch{{display:inline-block;width:20px;height:3px;border-radius:2px;background:var(--green)}}.swatch.proposed{{background:var(--amber);background-image:linear-gradient(90deg,var(--amber) 50%,transparent 50%);background-size:8px 3px}}.swatch.count{{height:10px;width:10px;border-radius:50%;background:var(--blue)}}.global .diagram-scroll{{height:min(76vh,850px)}}.erd{{display:block;max-width:none;overflow:visible}}.diagram-scroll{{overflow:auto;max-height:70vh;border:1px solid var(--line);border-radius:13px;background:linear-gradient(135deg,#0d201b,#0b1714);padding:8px}}:root.light .diagram-scroll{{background:#f6faf7}}
.edge{{fill:none;stroke-width:2;opacity:.8}}.edge.actual{{stroke:var(--green)}}.edge.propuesta{{stroke:var(--amber);stroke-dasharray:7 6}}.edge-label{{font-size:11px;font-weight:700;paint-order:stroke;stroke:var(--bg);stroke-width:5px;stroke-linejoin:round}}.edge-label.actual{{fill:var(--green)}}.edge-label.propuesta{{fill:var(--amber)}}.cardinality{{font:11px ui-monospace,Consolas,monospace;fill:var(--muted);paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}}.node > rect:first-of-type{{fill:var(--panel);stroke:var(--line);stroke-width:1.5;filter:url(#shadow)}}.node.actual .node-accent{{fill:var(--green)}}.node.propuesta .node-accent{{fill:var(--amber)}}.node-label{{font:650 13px ui-monospace,Consolas,monospace;fill:var(--text)}}.node-status{{font:700 9px Inter,Arial,sans-serif;letter-spacing:.12em;fill:var(--muted)}}
#view-list{{display:grid;gap:11px}}.toolbar{{position:sticky;top:0;z-index:5;display:flex;gap:10px;align-items:center;padding:11px 0;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px)}}.toolbar input{{flex:1;min-width:120px;padding:11px 14px;border:1px solid var(--line);background:var(--surface);border-radius:12px}}.view-card{{border:1px solid var(--line);border-radius:17px;background:var(--surface);overflow:hidden}}.view-card[open]{{box-shadow:var(--shadow)}}.view-card summary{{cursor:pointer;list-style:none;display:flex;align-items:center;gap:13px;padding:15px 18px}}.view-card summary::-webkit-details-marker{{display:none}}.view-card summary:after{{content:'+';margin-left:auto;color:var(--green);font-size:20px}}.view-card[open] summary:after{{content:'−'}}.view-number{{font:700 12px ui-monospace,Consolas,monospace;color:var(--green);border:1px solid color-mix(in srgb,var(--green) 35%,var(--line));background:var(--chip);padding:5px 8px;border-radius:8px}}.view-title{{font-size:17px;font-weight:700}}.view-count{{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap}}.view-body{{padding:0 18px 19px;border-top:1px solid var(--line)}}.interaction{{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:17px 0 10px}}.interaction p{{margin:5px 0 0;color:var(--muted)}}.eyebrow{{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);font-weight:750}}.table-tags{{padding:8px 0 17px}}.tags{{display:flex;flex-wrap:wrap;gap:7px;margin-top:9px}}.tag{{display:inline-flex;align-items:center;gap:8px;border-radius:9px;padding:5px 8px;background:var(--chip);border:1px solid var(--line);font-size:11px}}.tag b{{text-transform:uppercase;font-size:9px;letter-spacing:.08em;color:var(--green)}}.tag code{{font:600 11px ui-monospace,Consolas,monospace;color:var(--text)}}.tag small{{color:var(--muted)}}.tag.propuesta b{{color:var(--amber)}}.tag.pending b{{color:var(--red)}}.tag.none b{{color:var(--blue)}}.diagram-toolbar{{display:flex;align-items:center;gap:7px;margin:7px 0;color:var(--muted);font-size:12px}}.diagram-toolbar span{{margin-right:auto}}.diagram-toolbar button{{border:1px solid var(--line);background:var(--panel);border-radius:7px;padding:4px 9px;cursor:pointer}}.no-schema{{padding:20px;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}}.no-schema strong{{color:var(--blue)}}.no-schema p{{margin:4px 0 0}}.footer{{margin-top:35px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:13px}}.hidden{{display:none!important}}@media(max-width:760px){{.interaction{{grid-template-columns:1fr}}.view-card summary{{gap:8px;padding:12px}}.view-title{{font-size:15px}}.view-count{{display:none}}.top-actions .button span{{display:none}}}}@media print{{body{{background:white;color:#111}}.toolbar,.top-actions,.diagram-toolbar button{{display:none}}.view-card{{break-inside:avoid}}.view-body{{display:block}}.diagram-scroll{{overflow:visible;max-height:none}}.erd{{width:100%!important;height:auto!important}}}}
.attribute-background{{fill:transparent;stroke:none}}.attribute-background.alternate{{fill:var(--chip);opacity:.62}}.attribute-name{{font:600 12px ui-monospace,Consolas,monospace;fill:var(--text)}}.attribute-keys{{font:700 10px ui-monospace,Consolas,monospace;fill:var(--green)}}.attribute-type{{font:11px ui-monospace,Consolas,monospace;fill:var(--muted)}}.attribute-reference{{font:10px ui-monospace,Consolas,monospace;fill:var(--blue)}}.column-hint{{font:8px Inter,Arial,sans-serif;letter-spacing:.13em;fill:var(--muted)}}.attribute-dictionary{{border:1px solid var(--line);border-radius:12px;padding:12px;margin-top:14px}}.attribute-dictionary summary{{font-size:13px!important;font-weight:600;cursor:pointer}}.attribute-dictionary summary:after{{content:none!important}}.attribute-dictionary h4{{margin:22px 0 8px}}.attribute-dictionary h4 small{{font-weight:400;color:var(--muted)}}.dictionary-scroll{{overflow:auto}}.dictionary-scroll table{{border-collapse:collapse;width:100%;font-size:12px;white-space:nowrap}}.dictionary-scroll th,.dictionary-scroll td{{border:1px solid var(--line);padding:7px 9px;text-align:left}}.dictionary-scroll thead{{background:var(--chip)}}.dictionary-scroll tbody th{{font-weight:600}}
{audit_css}
</style></head>
<body><main class="shell">
<header><div><div class="brand">Agro · esquema relacional</div><h1>Las relaciones, vista por vista</h1><p class="lead">Cada tabla incluye todos sus atributos, tipos SQL, nulabilidad y claves. Las FK muestran su destino incluso cuando queda fuera del recorte. Las relaciones entre tablas conservan el Markdown de cada vista.</p></div><div class="top-actions"><button class="button" id="theme">◐ <span>Tema</span></button><a class="button" href="esquema-agro.html">Resumen Archify</a></div></header>
<div class="stats"><span class="stat"><b>{len(tables)}</b> tablas objetivo</span><span class="stat"><b>{column_count}</b> atributos del SQL</span><span class="stat"><b>{fk_count}</b> FK globales documentadas</span><span class="stat"><b>61</b> ERD por vista</span><span class="stat"><b>V02</b> navegación sin tabla</span></div>
<p class="lead">D08 · 29/10/2026: el prototipo no tiene CRUD de destinos. La entrega guarda <code>destino</code> como texto obligatorio y la guía conserva su dirección de llegada histórica.</p>
{audit_panel}
<details class="global" open><summary>Esquema global · mapa completo de relaciones del Markdown</summary><div class="inside"><div class="legend"><span><i class="swatch"></i> Relación actual conservada</span><span><i class="swatch proposed"></i> Relación propuesta</span><span><i class="swatch count"></i> Cardinalidad junto a cada tabla</span><span>PK = primaria · FK = foránea · UK = participa en unicidad (puede ser compuesta o parcial).</span><span>NULL = opcional · NOT NULL = obligatorio. Pasa el cursor sobre un atributo para ver su definición SQL y restricciones de unicidad.</span><span>{len(global_graph[1])} relaciones visuales agrupan las {fk_count} FK; las FK compuestas del mismo par aparecen una sola vez.</span></div><div class="diagram-toolbar"><span>{len(tables)} tablas con todos sus atributos</span><button class="zoom-in" type="button">+</button><button class="zoom-out" type="button">−</button><button class="zoom-reset" type="button">100%</button><button class="zoom-fit" type="button">Ajustar ancho</button></div><div class="diagram-scroll">{global_svg}</div></div></details>
<div class="toolbar"><input type="search" id="search" placeholder="Filtrar por código, vista o tabla…" aria-label="Filtrar vistas"><button class="button" id="expand">Abrir todas</button><button class="button" id="collapse">Cerrar todas</button></div>
<div id="view-list">{''.join(parts)}</div>
<footer class="footer">Fuente de relaciones: <a href="../02_tablas_y_relaciones.md">02_tablas_y_relaciones.md</a>. Fuente de acciones y uso por tabla: <a href="../01_reporte_especifico.md">01_reporte_especifico.md</a>. Tabla actual/propuesta según <a href="../03_schema_total.sql">03_schema_total.sql</a>. El esquema es objetivo de revisión; las propuestas no implican despliegue.</footer>
</main>
<script>
const q=s=>document.querySelector(s), cards=[...document.querySelectorAll('.view-card')];
q('#theme').addEventListener('click',()=>document.documentElement.classList.toggle('light'));
q('#expand').addEventListener('click',()=>cards.filter(c=>!c.classList.contains('hidden')).forEach(c=>c.open=true));
q('#collapse').addEventListener('click',()=>cards.forEach(c=>c.open=false));
q('#search').addEventListener('input',e=>{{const val=e.target.value.toLowerCase().trim(); cards.forEach(c=>{{const hit=!val||c.dataset.title.includes(val)||c.textContent.toLowerCase().includes(val); c.classList.toggle('hidden',!hit); if(hit&&val)c.open=true;}})}});
document.querySelectorAll('.diagram-toolbar').forEach(toolbar=>{{const svg=toolbar.nextElementSibling.querySelector('svg'); let scale=1; const apply=()=>{{svg.style.width=Math.max(360,parseFloat(svg.getAttribute('viewBox').split(' ')[2])*scale)+'px'; svg.style.height=Math.max(220,parseFloat(svg.getAttribute('viewBox').split(' ')[3])*scale)+'px';}}; toolbar.querySelector('.zoom-in').onclick=()=>{{scale=Math.min(2.5,scale+.15);apply()}}; toolbar.querySelector('.zoom-out').onclick=()=>{{scale=Math.max(.08,scale-.15);apply()}}; toolbar.querySelector('.zoom-reset').onclick=()=>{{scale=1;apply()}}; toolbar.querySelector('.zoom-fit').onclick=()=>{{scale=Math.min(1,(toolbar.nextElementSibling.clientWidth-20)/parseFloat(svg.getAttribute('viewBox').split(' ')[2]));apply()}}; apply();}});
{audit_js}
</script></body></html>'''

out=outdir/'esquema-agro-vistas.html'
out.write_text(html_doc,encoding='utf-8')
print(f'HTML generado: {out}; atributos SQL={column_count}; vistas={len(sections)}, ERD vistas={sum(bool(x["diagram"]) for x in sections)}, ERD global={len(global_graph[0])} tablas/{len(global_graph[1])} relaciones, tamaño={out.stat().st_size} bytes')
