from pathlib import Path
import re, html, json, collections
script_dir=Path(__file__).resolve().parent
base=script_dir.parents[2]
outdir=script_dir
map_path=base/'docs/agro-schema/02_tablas_y_relaciones.md'
report_path=base/'docs/agro-schema/01_reporte_especifico.md'
sql_path=base/'docs/agro-schema/03_schema_total.sql'
map_text=map_path.read_text(encoding='utf-8')
report_text=report_path.read_text(encoding='utf-8')
sql_text=sql_path.read_text(encoding='utf-8')

# The SQL comments define the 19 existing tables; the rest are proposed in this target schema.
status={m.group(1):('Actual' if 'ACTUAL AMPLIADA' in m.group(0) else 'Propuesta') for m in re.finditer(r'(?m)^-- TABLA (?:ACTUAL AMPLIADA|PROPUESTA): ([^\r\n]+)',sql_text)}

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

def wrap_name(name,max_chars=26):
    # Wrap at underscores while preserving every character of the physical name.
    result=[]; cur=''
    for part in name.split('_'):
        token=part+'_' if part != name.split('_')[-1] else part
        if cur and len(cur)+len(token)>max_chars:
            result.append(cur); cur=token
        else: cur+=token
    if cur: result.append(cur)
    return result or [name]

def layout(nodes,edges):
    if not nodes: return {},400,200
    adj={n:set() for n in nodes}
    for e in edges:
        adj[e['a']].add(e['b']); adj[e['b']].add(e['a'])
    unvisited=set(nodes); placed={}; component_offset=0
    while unvisited:
        root=max(unvisited,key=lambda n:(len(adj[n]),n))
        dist={root:0}; queue=[root]; comp=[]
        while queue:
            n=queue.pop(0); comp.append(n)
            for other in sorted(adj[n]):
                if other not in dist:
                    dist[other]=dist[n]+1; queue.append(other)
        # Isolates and disconnected subgraphs get their own compact band.
        unvisited.difference_update(comp)
        levels=collections.defaultdict(list)
        for n in comp: levels[dist[n]].append(n)
        for d in levels: levels[d].sort(key=lambda n:(-len(adj[n]),n))
        # Barycentric sweeps reduce crossings while retaining the source graph unchanged.
        for _ in range(4):
            for d in range(1,max(levels.keys(),default=0)+1):
                prev={n:i for i,n in enumerate(levels[d-1])}
                levels[d].sort(key=lambda n:(sum(prev[x] for x in adj[n] if x in prev)/max(1,sum(x in prev for x in adj[n])),n))
            for d in range(max(levels.keys(),default=0)-1,-1,-1):
                nxt={n:i for i,n in enumerate(levels[d+1])} if d+1 in levels else {}
                if nxt: levels[d].sort(key=lambda n:(sum(nxt[x] for x in adj[n] if x in nxt)/max(1,sum(x in nxt for x in adj[n])),n))
        maxrows=max((len(v) for v in levels.values()),default=1)
        for d,items in levels.items():
            for row,n in enumerate(items): placed[n]=(72+d*360,72+(component_offset+row)*128)
        component_offset += maxrows+1
    maxx=max(x for x,y in placed.values()); maxy=max(y for x,y in placed.values())
    return placed,maxx+360,maxy+150

def svg_graph(nodes,edges,view=False):
    pos,width,height=layout(nodes,edges)
    W,H=270,82
    out=[f'<svg class="erd" viewBox="0 0 {width} {height}" role="img" aria-label="Diagrama ER con {len(nodes)} tablas y {len(edges)} relaciones">',
         '<defs><filter id="shadow" x="-15%" y="-15%" width="130%" height="150%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#00110e" flood-opacity=".26"/></filter></defs>',
         '<g class="edges">']
    for i,e in enumerate(edges):
        x1,y1=pos[e['a']]; x2,y2=pos[e['b']]
        if x2>x1:
            sx,sy=x1+W,y1+H/2; tx,ty=x2,y2+H/2
            bend=max(42,abs(tx-sx)*0.34); c1=(sx+bend,sy); c2=(tx-bend,ty)
        elif x2<x1:
            sx,sy=x1,y1+H/2; tx,ty=x2+W,y2+H/2
            bend=max(42,abs(tx-sx)*0.34); c1=(sx-bend,sy); c2=(tx+bend,ty)
        elif y2>=y1:
            sx,sy=x1+W/2,y1+H; tx,ty=x2+W/2,y2
            c1=(sx+72,sy+38); c2=(tx+72,ty-38)
        else:
            sx,sy=x1+W/2,y1; tx,ty=x2+W/2,y2+H
            c1=(sx-72,sy-38); c2=(tx-72,ty+38)
        label=e['label'].lower()
        kind='actual' if label=='actual' else 'propuesta'
        title=f"{e['a']} {e['left']} · {label or 'relación'} · {e['right']} {e['b']}"
        d=f'M {sx:.1f},{sy:.1f} C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {tx:.1f},{ty:.1f}'
        out.append(f'<path class="edge {kind}" d="{d}"><title>{html.escape(title)}</title></path>')
        # Preserve the exact source label through color and a small inline badge in view cuts.
        if view and e['label']:
            mx=(sx+tx)/2; my=(sy+ty)/2-7
            out.append(f'<text class="edge-label {kind}" x="{mx:.1f}" y="{my:.1f}">{html.escape(e["label"])}</text>')
        # Mermaid endpoint multiplicity, rendered next to each table.
        for xx,yy,tok,side in [(sx,sy,e['left'],'source'),(tx,ty,e['right'],'target')]:
            lbl=endpoint_label(tok)
            dx=12 if side=='source' and x2>=x1 or side=='target' and x2<x1 else -12
            anchor='start' if dx>0 else 'end'
            out.append(f'<text class="cardinality" x="{xx+dx:.1f}" y="{yy-7:.1f}" text-anchor="{anchor}">{html.escape(lbl)}</text>')
    out.append('</g><g class="nodes">')
    for n in nodes:
        x,y=pos[n]; state=status.get(n,'Propuesta'); kind='actual' if state=='Actual' else 'propuesta'
        out.append(f'<g class="node {kind}" transform="translate({x},{y})"><title>{html.escape(n)} · {state}</title><rect width="{W}" height="{H}" rx="14"/><rect class="node-accent" width="5" height="{H}" rx="2"/>')
        lines=wrap_name(n)
        lineh=16; available=H-30
        shown=lines[:max(1,int(available/lineh))]
        top=27 if len(shown)==1 else 20
        for j,line in enumerate(shown):
            out.append(f'<text class="node-label" x="18" y="{top+j*lineh}">{html.escape(line)}</text>')
        out.append(f'<text class="node-status" x="18" y="{H-9}">{state.upper()}</text></g>')
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
assert sum(1 for v in status.values() if v=='Actual')==19 and sum(1 for v in status.values() if v=='Propuesta')==47, 'El SQL debe contener 19 tablas actuales y 47 propuestas.'
assert len(sections)==62, f'El Markdown debe aportar 62 vistas, halladas {len(sections)}'
assert sum(bool(s['diagram']) for s in sections)==61, 'Se esperaba V02 como la única vista sin diagrama de entidades.'

def tags_html(rows):
    if not rows: return '<span class="tag none">Sin tabla de negocio · navegación del prototipo</span>'
    labels={'Escritura esperada':'Escritura','Consulta':'Consulta','Por discutir':'Por discutir'}
    out=[]
    for r in rows:
        st='actual' if r['state']=='Actual' else ('pending' if r['state']=='Por discutir' else 'propuesta')
        role=labels.get(r['usage'],r['usage'])
        out.append(f'<span class="tag {st}" title="{html.escape(r["state"]+" · "+r["usage"])}"><b>{html.escape(r["state"])}</b><code>{html.escape(r["name"])}</code><small>{html.escape(role)}</small></span>')
    return ''.join(out)

global_svg=svg_graph(*global_graph,view=False)
module_groups=[('01–20','Comercial y campañas'),('21–30','Proveedores y transporte'),('31–40','Cosecha y logística'),('41–52','Facturación y liquidaciones'),('53–62','Aplicación del chofer')]
parts=[]
for item in sections:
    ref,title,diagram=item['ref'],item['title'],item['diagram']; info=view_info.get(ref,{'action':'—','observed':'No se registró interacción.','surface':'Vista','rows':[]})
    group=next(label for rng,label in module_groups if int(ref[1:])<=int(rng.split('–')[1]))
    if diagram:
        nodes,edges=diagram; chart=svg_graph(nodes,edges,view=True)
        diagram_html=f'<div class="diagram-toolbar"><span>{len(nodes)} tablas · {len(edges)} relaciones del Markdown</span><button class="zoom-in" type="button" aria-label="Aumentar diagrama">+</button><button class="zoom-out" type="button" aria-label="Reducir diagrama">−</button><button class="zoom-reset" type="button">Ajustar</button></div><div class="diagram-scroll">{chart}</div>'
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
.edge{{fill:none;stroke-width:2;opacity:.8}}.edge.actual{{stroke:var(--green)}}.edge.propuesta{{stroke:var(--amber);stroke-dasharray:7 6}}.edge-label{{font-size:11px;font-weight:700;paint-order:stroke;stroke:var(--bg);stroke-width:5px;stroke-linejoin:round}}.edge-label.actual{{fill:var(--green)}}.edge-label.propuesta{{fill:var(--amber)}}.cardinality{{font:11px ui-monospace,Consolas,monospace;fill:var(--muted);paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}}.node rect:first-of-type{{fill:var(--panel);stroke:var(--line);stroke-width:1.5;filter:url(#shadow)}}.node.actual .node-accent{{fill:var(--green)}}.node.propuesta .node-accent{{fill:var(--amber)}}.node-label{{font:650 13px ui-monospace,Consolas,monospace;fill:var(--text)}}.node-status{{font:700 9px Inter,Arial,sans-serif;letter-spacing:.12em;fill:var(--muted)}}
#view-list{{display:grid;gap:11px}}.toolbar{{position:sticky;top:0;z-index:5;display:flex;gap:10px;align-items:center;padding:11px 0;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px)}}.toolbar input{{flex:1;min-width:120px;padding:11px 14px;border:1px solid var(--line);background:var(--surface);border-radius:12px}}.view-card{{border:1px solid var(--line);border-radius:17px;background:var(--surface);overflow:hidden}}.view-card[open]{{box-shadow:var(--shadow)}}.view-card summary{{cursor:pointer;list-style:none;display:flex;align-items:center;gap:13px;padding:15px 18px}}.view-card summary::-webkit-details-marker{{display:none}}.view-card summary:after{{content:'+';margin-left:auto;color:var(--green);font-size:20px}}.view-card[open] summary:after{{content:'−'}}.view-number{{font:700 12px ui-monospace,Consolas,monospace;color:var(--green);border:1px solid color-mix(in srgb,var(--green) 35%,var(--line));background:var(--chip);padding:5px 8px;border-radius:8px}}.view-title{{font-size:17px;font-weight:700}}.view-count{{margin-left:auto;color:var(--muted);font-size:12px;white-space:nowrap}}.view-body{{padding:0 18px 19px;border-top:1px solid var(--line)}}.interaction{{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:17px 0 10px}}.interaction p{{margin:5px 0 0;color:var(--muted)}}.eyebrow{{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);font-weight:750}}.table-tags{{padding:8px 0 17px}}.tags{{display:flex;flex-wrap:wrap;gap:7px;margin-top:9px}}.tag{{display:inline-flex;align-items:center;gap:8px;border-radius:9px;padding:5px 8px;background:var(--chip);border:1px solid var(--line);font-size:11px}}.tag b{{text-transform:uppercase;font-size:9px;letter-spacing:.08em;color:var(--green)}}.tag code{{font:600 11px ui-monospace,Consolas,monospace;color:var(--text)}}.tag small{{color:var(--muted)}}.tag.propuesta b{{color:var(--amber)}}.tag.pending b{{color:var(--red)}}.tag.none b{{color:var(--blue)}}.diagram-toolbar{{display:flex;align-items:center;gap:7px;margin:7px 0;color:var(--muted);font-size:12px}}.diagram-toolbar span{{margin-right:auto}}.diagram-toolbar button{{border:1px solid var(--line);background:var(--panel);border-radius:7px;padding:4px 9px;cursor:pointer}}.no-schema{{padding:20px;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}}.no-schema strong{{color:var(--blue)}}.no-schema p{{margin:4px 0 0}}.footer{{margin-top:35px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:13px}}.hidden{{display:none!important}}@media(max-width:760px){{.interaction{{grid-template-columns:1fr}}.view-card summary{{gap:8px;padding:12px}}.view-title{{font-size:15px}}.view-count{{display:none}}.top-actions .button span{{display:none}}}}@media print{{body{{background:white;color:#111}}.toolbar,.top-actions,.diagram-toolbar button{{display:none}}.view-card{{break-inside:avoid}}.view-body{{display:block}}.diagram-scroll{{overflow:visible;max-height:none}}.erd{{width:100%!important;height:auto!important}}}}
</style></head>
<body><main class="shell">
<header><div><div class="brand">Agro · esquema relacional</div><h1>Las relaciones, vista por vista</h1><p class="lead">Cada recorte reproduce la topología y las cardinalidades del Markdown de relaciones. Debajo se indican la acción observada en el prototipo y las tablas que participan en consulta, escritura o revisión.</p></div><div class="top-actions"><button class="button" id="theme">◐ <span>Tema</span></button><a class="button" href="esquema-agro.html">Resumen Archify</a></div></header>
<div class="stats"><span class="stat"><b>66</b> tablas objetivo</span><span class="stat"><b>137</b> FK globales documentadas</span><span class="stat"><b>61</b> ERD por vista</span><span class="stat"><b>V02</b> navegación sin tabla</span></div>
<details class="global" open><summary>Esquema global · mapa completo de relaciones del Markdown</summary><div class="inside"><div class="legend"><span><i class="swatch"></i> Relación actual conservada</span><span><i class="swatch proposed"></i> Relación propuesta</span><span><i class="swatch count"></i> Cardinalidad junto a cada tabla</span><span>Las cajas muestran estado de tabla: actual o propuesta.</span><span>{len(global_graph[1])} relaciones visuales agrupan las 137 FK; las FK compuestas del mismo par aparecen una sola vez.</span></div><div class="diagram-scroll">{global_svg}</div></div></details>
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
document.querySelectorAll('.diagram-toolbar').forEach(toolbar=>{{const svg=toolbar.nextElementSibling.querySelector('svg'); let scale=1; const apply=()=>{{svg.style.width=Math.max(360,parseFloat(svg.getAttribute('viewBox').split(' ')[2])*scale)+'px'; svg.style.height=Math.max(220,parseFloat(svg.getAttribute('viewBox').split(' ')[3])*scale)+'px';}}; toolbar.querySelector('.zoom-in').onclick=()=>{{scale=Math.min(2.5,scale+.15);apply()}}; toolbar.querySelector('.zoom-out').onclick=()=>{{scale=Math.max(.55,scale-.15);apply()}}; toolbar.querySelector('.zoom-reset').onclick=()=>{{scale=1;apply()}}; apply();}});
</script></body></html>'''

out=outdir/'esquema-agro-vistas.html'
out.write_text(html_doc,encoding='utf-8')
print(f'HTML generado: {out}; vistas={len(sections)}, ERD vistas={sum(bool(x["diagram"]) for x in sections)}, ERD global={len(global_graph[0])} tablas/{len(global_graph[1])} relaciones, tamaño={out.stat().st_size} bytes')



