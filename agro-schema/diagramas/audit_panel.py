"""Renderiza los dictámenes de la auditoría junto al esquema, sin alterar el ERD."""
from pathlib import Path
import hashlib
import html
import json
from urllib.parse import quote

SHORT = {'simplificar':'Simplificar', 'conservar':'Conservar', 'configurar':'Seed/configuración',
         'tecnica':'Función técnica', 'diferir':'Revisar autenticación'}


def load_audit(base, sql_path):
    path = Path(base) / 'auditoria-tablas-propuestas.json'
    if not path.exists():
        return {}, ''
    audit = json.loads(path.read_text(encoding='utf-8'))
    records = {r['table']:r for r in audit['tables']}
    esc = html.escape
    counts = ''.join(f'<span class="audit-stat"><b>{n}</b> {esc(audit["labels"][k])}</span>' for k,n in audit['counts'].items())
    options = ''.join(f'<option value="{k}">{esc(v)} ({audit["counts"][k]})</option>' for k,v in audit['labels'].items() if audit['counts'].get(k))
    removed = ''.join(f'<span class="audit-tag">{esc(r["table"])} · {esc(r["outcome"])}</span>' for r in audit.get('removed_tables',[]))
    count=len(records)
    stale = audit['sql_sha256'] != hashlib.sha256(Path(sql_path).read_bytes()).hexdigest()
    warning = '<p class="audit-warning">El SQL cambió después de esta auditoría. Revisar los dictámenes antes de aplicarlos.</p>' if stale else ''
    items = []
    for r in audit['tables']:
        sources = []
        for key in r['evidence']:
            e = audit['evidence'][key]
            href = '../../prototipo/Campaign%20Management%20System/src/'+quote(e['file'])+'#L'+str(e['line'])
            sources.append(f'<a href="{href}">{esc(e["file"])}:{e["line"]}</a>')
        views = ' '.join(f'<a href="#{v.lower()}">{v}</a>' for v in r['views']) or 'Sin ficha específica'
        inbound = '; '.join(f['child']+'.'+','.join(f['cols']) for f in r['inbound_fks']) or 'Ninguna FK entrante'
        dependency = f'<p><b>Pendiente de autenticación:</b> justificar la persistencia de sesión propia; dependencias actuales: <code>{esc(inbound)}</code>. Regenerar SQL, fichas y diagramas en conjunto.</p>' if r['decision'] in ('simplificar','diferir') else ''
        search = esc((r['table']+' '+r['ui']+' '+r['finding']+' '+' '.join(r['views'])).lower(),quote=True)
        items.append(f'''<details class="audit-table" id="audit-{r['table']}" data-decision="{r['decision']}" data-search="{search}">
<summary><code>{r['table']}</code><span class="audit-tag verdict-{r['decision']}">{esc(SHORT[r['decision']])}</span></summary>
<div class="audit-table-body"><p><b>Interfaz:</b> {esc(r['ui'])}.</p><p>{esc(r['finding'])}</p>
<p><b>Decisión y persistencia:</b> {esc(r['proposal'])}</p><p><b>Predeterminados:</b> {esc(r['defaults'])}</p>{dependency}
<p class="audit-evidence"><b>Fuente actual:</b> {', '.join(sources)}. <b>Fichas:</b> {views}.</p></div></details>''')
    constants = ''.join(f'<tr><th scope="row">{esc(c["name"])}</th><td>{esc(c["storage"])}</td><td>{esc(c["proposal"])}</td></tr>' for c in audit['constants'])
    panel = f'''<details class="global audit-panel" id="auditoria" open><summary>Auditoría aplicada · {count} propuestas vigentes · 29/10/2026</summary><div class="inside">
<p class="audit-intro"><b>Cinco simplificaciones incorporadas al SQL objetivo.</b> Se retira sesion_usuario; usuario y rol permanecen. Se conserva norma con datos iniciales y guia_x_norma para selecciones reales. Modelo: 60 tablas y 124 FK; no se ha modificado una base desplegada.</p>
<div class="audit-stats">{counts}</div>{warning}
<p class="audit-evidence">Auditoría estática del código local actual y las fichas V01–V62. No prueba ejecución ni persistencia normalizada del backend. Los editores actuales de cotización y kilos por variedad justifican conservar sus tablas. D08 (destino como texto) ya está resuelto y no se cuenta entre las 46 propuestas originales. Ahora quedan {count} vigentes.</p>
<p><b>Retiradas o consolidadas:</b></p><div class="audit-candidates">{removed}</div><p class="audit-evidence"><b>Normas de guía:</b> el selector consulta norma; al guardar borrador el servicio resolverá los códigos elegidos y sincronizará solo esas filas en guia_x_norma. Sin selección: cero filas. El seed carga el catálogo, no asignaciones. Se conserva el texto histórico de cada guía.</p><p><a href="../04_datos_iniciales.sql">SQL de datos iniciales</a> · Incluido en el SQL total: 2 perfiles, 5 normas, 5 frutas, 17 variedades y parámetros de 2025/2026 del prototipo.</p>
<details class="audit-constants"><summary>Selectores fijos y configuración sin CRUD · moneda, roles, normas y otros</summary><div class="dictionary-scroll"><table><thead><tr><th>Selector</th><th>Persistencia</th><th>Recomendación</th></tr></thead><tbody>{constants}</tbody></table></div></details>
<div class="audit-controls"><input id="audit-search" type="search" aria-label="Buscar tabla auditada" placeholder="Buscar tabla o función auditada…"><select id="audit-filter" aria-label="Filtrar dictamen"><option value="all">Todos los dictámenes ({count})</option>{options}</select><span id="audit-count" aria-live="polite">{count} tablas</span></div>
<div id="audit-tables">{''.join(items)}</div><p id="audit-empty" class="hidden">Sin tablas para este filtro.</p>
<p class="audit-evidence"><a href="../auditoria-tablas-propuestas-vs-prototipo.md">Informe completo y orden de modificación</a> · <a href="../auditoria-tablas-propuestas.json">Datos, dependencias y huellas de las fuentes</a></p></div></details>'''
    return records, panel


def audit_tag(record):
    if not record:
        return ''
    return f'<a class="audit-tag verdict-{record["decision"]}" href="#audit-{record["table"]}" title="{html.escape(record["proposal"],quote=True)}">{html.escape(SHORT[record["decision"]])}</a>'


CSS = '''
.audit-intro{font-size:15px;max-width:100ch}.audit-stats,.audit-candidates{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.audit-stat{border:1px solid var(--line);background:var(--chip);border-radius:9px;padding:7px 10px;font-size:12px}.audit-stat b{font-size:16px;margin-right:5px}.audit-tag{font-size:10px;font-weight:700;display:inline-block;border:1px solid var(--line);border-radius:6px;padding:3px 6px;text-decoration:none;white-space:normal;overflow-wrap:anywhere;color:var(--muted);background:var(--chip)}.verdict-simplificar,.verdict-diferir{color:var(--amber);border-color:var(--amber)}.verdict-configurar{color:var(--blue)}.audit-controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:20px 0 12px}.audit-controls input,.audit-controls select{font:inherit;font-size:13px;color:var(--text);background:var(--panel);border:1px solid var(--line);padding:10px;border-radius:9px;min-width:0;max-width:100%}.audit-controls input{flex:1;min-width:180px}.audit-controls span{font-size:12px;color:var(--muted)}.audit-table{border:1px solid var(--line);border-radius:10px;margin:7px 0;scroll-margin-top:20px}.audit-table>summary{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:11px 12px;cursor:pointer;font-size:13px}.audit-table>summary code{overflow-wrap:anywhere;white-space:normal}.audit-table-body{padding:0 14px 7px;border-top:1px solid var(--line);font-size:13px}.audit-evidence{color:var(--muted);font-size:12px;line-height:1.7;overflow-wrap:anywhere}.audit-constants{margin:20px 0}.audit-constants>summary{cursor:pointer;margin-bottom:12px;font-size:14px}.audit-constants table{white-space:normal;min-width:620px}.audit-constants td{vertical-align:top;min-width:190px;max-width:600px;line-height:1.6}.audit-warning{color:var(--amber)}.audit-panel a:focus-visible,.audit-panel summary:focus-visible{outline:2px solid var(--blue);outline-offset:3px}@media(max-width:600px){.audit-table>summary{align-items:flex-start;flex-direction:column}.audit-controls select{width:100%}}
'''

JS = '''
const auditRows=[...document.querySelectorAll('.audit-table')];
function filterAudit(){const term=q('#audit-search').value.toLowerCase().trim(),decision=q('#audit-filter').value;let n=0;auditRows.forEach(row=>{const hit=(!term||row.dataset.search.includes(term))&&(decision==='all'||row.dataset.decision===decision);row.classList.toggle('hidden',!hit);if(hit){n++;if(term)row.open=true}});q('#audit-count').textContent=n+' tablas';q('#audit-empty').classList.toggle('hidden',n!==0)}
if(q('#audit-search')){q('#audit-search').addEventListener('input',filterAudit);q('#audit-filter').addEventListener('change',filterAudit)}
function openAnchor(){const id=decodeURIComponent(location.hash.slice(1));if(!id)return;const target=document.getElementById(id);if(!target)return;if(target.classList.contains('audit-table')){q('#audit-search').value='';q('#audit-filter').value='all';filterAudit()}if(target.classList.contains('view-card')){q('#search').value='';cards.forEach(c=>c.classList.remove('hidden'))}for(let el=target;el;el=el.parentElement){if(el.tagName==='DETAILS')el.open=true}requestAnimationFrame(()=>target.scrollIntoView({block:'start'}))}
addEventListener('hashchange',openAnchor);openAnchor();
'''
