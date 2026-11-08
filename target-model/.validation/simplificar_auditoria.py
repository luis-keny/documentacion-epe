from pathlib import Path
import re,json
R=Path(__file__).resolve().parent.parent
APP=R.parent.parent
audit=APP/'epe-backend/docs/auditoria-bd-actual-vs-planificada.md'
text=audit.read_text(encoding='utf8')
actual=json.loads((R/'.validation/modelo_actual.json').read_text(encoding='utf8'))
names={t['table'] for t in actual}
plan=json.loads((R/'.validation/modelo_alineado.json').read_text(encoding='utf8'))
parts=re.split(r'(?m)(?=^## )',text)
sections={p.splitlines()[0]:p for p in parts[1:]}
def find(prefix):return next(v for k,v in sections.items() if k.startswith('## '+prefix))
prefix=parts[0]
intro=[]
for part in parts[1:]:
    if part.startswith('## Archivos ('):break
    if part.startswith('## Cambios de nomenclatura'):
        intro += ['## Nombres de las tablas que ya tienes (Backend > Esquema actual > Nombres oficiales)\n\n',
        'Estos son los **nombres exactos de tus entidades TypeORM**. Se usan así en esta auditoría y en los reportes cuando se habla de tablas existentes. No se están renombrando tablas de tu base.\n\n',
        '| Tabla que ya tienes | Cómo se considera en el plan |\n|---|---|\n']
        for t in actual:
            n=t['table']
            use='Conservar y ampliar según lo que necesite la vista.' if n in plan['tables'] else 'Conservar mientras se define cómo cubrir su información en el flujo completo de transporte.'
            intro.append(f'| `{n}` | {use} |\n')
        intro += ['\n**Tablas propuestas** significa que todavía no aparecen en las entidades revisadas. Por ejemplo, `contrato_venta` y `factura_venta` son propuestas; `cliente_negocio_campana` sí existe. No son nombres alternativos de una misma tabla.\n\n',
        '**Tres nombres que también se conservan:** `trazabilidad_transporte`, `chofer_vehiculo_externo` y `detalle_trazabilidad`. Sus datos se reparten de otra forma en el plan; eso requiere diseño y una migración futura, no cambiarles el nombre para que parezcan tablas nuevas.\n\n']
    else:
        # La primera tabla de inventario también muestra solo la nomenclatura actual.
        part=re.sub(r'Conservar nombre; antes `[^`]+`\. Hay ajustes de estructura\.', 'Existe; se conserva este nombre y se evalúan las ampliaciones necesarias.',part)
        intro.append(part)
out=[prefix]+intro
out += ['**Cómo leer las secciones que siguen:** son la explicación de los hallazgos anteriores. En cada tabla verás **qué tienes hoy**, **qué le falta para cubrir las vistas** y **qué haríamos después**. Son recomendaciones; no cambios ya ejecutados. Los campos y restricciones técnicos quedan en bloques desplegables opcionales.\n\n']
simple={
'archivo':('Guarda los documentos y su ubicación en almacenamiento. Ya controla si el archivo está pendiente o disponible.', 'Que los demás módulos reutilicen este mecanismo cuando adjunten documentos.', 'Aprovechar la tabla y el servicio que ya existen. No crear otra tabla de archivos para cada módulo.'),
'campana':('Guarda una campaña, su fruta, fechas y estado.', 'Responsable, variedades elegidas, lineamientos y una forma de verificar todos los pendientes antes de cerrarla.', 'Ampliar campana. Antes hay que decidir si se mantiene tu regla de una sola campaña activa por fruta.'),
'campania_x_proveedores':('Relaciona una campaña con un proveedor y, cuando se conoce, una finca. Un mismo proveedor puede aparecer varias veces con fincas diferentes.', 'Distinguir los datos de todo el proveedor en la campaña de los datos de cada finca.', 'Conservar este nombre. Si se aprueba separar ambos niveles, agregar una cabecera común y vincular sus fincas. No sumar las cantidades de esas filas sin verificar qué representa cada una.'),
'certificado_campana':('Guarda el certificado, costo, vencimiento y documentos. Permite varios certificados por campaña.', 'Productores cubiertos, kilos certificados, ampliaciones y varios pagos con su historial.', 'Ampliar la tabla y agregar los registros de ampliaciones y pagos. Primero decidir si una campaña tendrá uno o varios certificados.'),
'certificado_proveedor':('Guarda los certificados propios de un proveedor y puede enlazarlos con archivo.', 'Completar los documentos que aún no tengan archivo y mantener clara la diferencia con el certificado de una campaña.', 'Conservar certificado_proveedor para certificados propios. La cobertura de productores de un certificado de campaña sería otra relación propuesta.'),
'chofer_transporte_externo':('Guarda al conductor, su empresa, nombre, teléfono y correo.', 'Documento de identidad, licencia y vínculo con una cuenta si va a ingresar como chofer.', 'Completar esa información y relacionarla con la identidad del usuario. No crear una persona distinta por cada viaje.'),
'chofer_vehiculo_externo':('Asigna chofer y vehículo a una trazabilidad durante un periodo. Ya impide que el chofer tenga fechas superpuestas.', 'Relacionar esa asignación con la entrega comercial que atenderá.', 'Reutilizar las asignaciones existentes y conservar la protección contra cruces de fechas. No descartar esta tabla sin haber trasladado también su historial.'),
'cliente_negocio':('Guarda al cliente, contacto, RUC, correo, ubicación y tipo.', 'Pocos cambios de identidad; principalmente conectarlo con los contratos y entregas del flujo completo.', 'Conservar cliente_negocio y revisar sus reglas de correo único y longitud de datos antes de cambiarlas.'),
'cliente_negocio_campana':('Relaciona al cliente con una campaña y guarda cantidades y documentos. Solo permite un vínculo por cliente y campaña.', 'Que ese mismo vínculo tenga varios contratos y que cada contrato tenga varias entregas.', 'Conservar cliente_negocio_campana y agregar contrato_venta como tabla hija propuesta. Tener dos contratos del mismo cliente no debería obligar a duplicar al cliente.'),
'detalle_trazabilidad':('Guarda guía, flete, SCTR y gastos de transporte.', 'Distinguir el documento de traslado, el monto que debes pagar y el pago que realmente hiciste.', 'Conservar sus datos y separarlos según su finalidad cuando se implemente el flujo nuevo. Un flete de S/ 800 registrado todavía no significa que esos S/ 800 se pagaron.'),
'empresa_transporte_externo':('Guarda a la empresa transportista y su contacto.', 'Diferenciar empresa e independiente y registrar la información adicional del transporte.', 'Mantener el nombre y ampliar los datos. Los registros actuales no se eliminan ni se clasifican solo por cómo se llama el transportista.'),
'entrevista_extencion':('Ya guarda entrevistas de productores por finca, con datos agronómicos y un código único generado por el backend.', 'Alinear el significado de sus datos con el formulario de referencia.', 'Reutilizar entrevista_extencion. Por ejemplo, anio_aplicacion indica un año como 2026; no equivale a decir que hubo cuatro aplicaciones durante el año. Son datos distintos.'),
'examen_proveedor':('Guarda exámenes generales de un proveedor, con resultado positivo o negativo.', 'Identificar la campaña/finca o muestra y permitir que el examen esté pendiente de resultado.', 'Ampliar examen_proveedor. No asignar los exámenes antiguos a una campaña que no esté confirmada.'),
'finca':('Guarda la finca de un proveedor, su ubicación, coordenadas y hectáreas.', 'Códigos y datos adicionales que piden las vistas, además de soportar hectáreas con decimales.', 'Conservar finca como padrón físico. Los cambios agronómicos de una campaña se registran en la entrevista, sin reescribir la historia de las campañas anteriores.'),
'fruta':('Es el catálogo de frutas.', 'Revisar nombres repetidos antes de aplicar la unicidad que propone el plan.', 'Conservar fruta y sus identificadores. No crear otro catálogo llamado frutas.'),
'fruta_derivada':('Representa las variedades de una fruta.', 'Relacionar las variedades que seleccionas para proveedores, campañas y entregas.', 'Usar fruta_derivada como nombre de esa tabla. No crear otra tabla variedades para el mismo catálogo.'),
'proveedor':('Guarda identidad, contacto, sanidad y un perfil agronómico general del proveedor.', 'Compartir la identidad con otros roles cuando corresponda y conservar los datos agronómicos por finca y campaña.', 'Conservar proveedor. Revisar documentos repetidos y pasar documentos/teléfonos a texto si se necesitan ceros iniciales o letras. No eliminar el perfil actual antes de reconciliar sus datos con las entrevistas.'),
'proveedor_x_fruta':('Indica qué frutas tiene asociadas cada proveedor y evita repetir la misma relación.', 'La selección de variedades cuando la vista la necesite.', 'Conservar proveedor_x_fruta. Agregar la asociación con fruta_derivada solo para cubrir esa selección adicional.'),
'trazabilidad_transporte':('Guarda transporte y pesos vinculados a una relación de campaña/proveedor. Una fila parte de un solo proveedor.', 'Representar un mismo viaje que recoge fruta de varios proveedores y termina en una entrega a un cliente.', 'Conservar los datos actuales y definir cómo identificar el viaje común. No cambiar simplemente el nombre a carga: antes hay que resolver cómo reunir varios proveedores sin duplicar kilos.'),
'vehiculo_externo':('Guarda placa, dimensiones, volumen y pesos del vehículo.', 'Aclarar qué significa peso neto y si hace falta registrar aparte la capacidad útil.', 'Conservar vehiculo_externo y sus dimensiones. No reemplazar el peso neto por capacidad sin verificar que significan lo mismo.')}
assert set(simple)==names
for t in actual:
    n=t['table'];old=next(p for p in parts[1:] if f'**Tabla actual:** `{n}`.' in p)
    oldhead=old.splitlines()[0];breadcrumb=oldhead[oldhead.index(' ('):]
    today,missing,action=simple[n]
    src=re.search(r'\*\*Fuente:\*\* (.+)\.',old).group(1)
    technical=old[old.index('**Diccionario comprobado'):].strip()
    longdelta=re.search(r'\*\*Diferencia y acción:\*\* (.*?)\n\n',old,re.S).group(1)
    out += [f'## {n}{breadcrumb}\n\n',f'**Tabla ya mapeada:** `{n}`. **Fuente:** {src}.\n\n',
        f'**Qué tienes hoy:** {today}\n\n',f'**Qué falta para las vistas:** {missing}\n\n',f'**Qué haríamos:** {action}\n\n',
        '<details>\n<summary>Ver campos, restricciones y explicación técnica</summary>\n\n',longdelta+'\n\n'+technical+'\n\n','</details>\n\n']
transform=find('Transformación de relaciones')
out += ['## Cómo cambiarían las relaciones (Plan > Proveedores y transporte > Ejemplo)\n\n',
    'Esta sección responde a **cómo conectaríamos lo que ya tienes para atender una vista más completa**. Hoy una trazabilidad parte de un proveedor; el objetivo permite que un viaje reúna varios. Los diagramas comparan esas dos formas. Las tablas nuevas del diagrama objetivo siguen siendo propuestas.\n\n',
    transform[transform.index('**Actual:'):]]
quality=find('Cosecha y Control de Calidad actualizado')
out += ['## Qué significa la actualización de Calidad (Administrador > Cosecha y Control de Calidad > Persistencia)\n\n',
    '**La pantalla avanzó, pero esos registros todavía no se guardan en tu base.** Selecciona campañas del backend, pero incorpora campañas a Calidad y conserva análisis en memoria del navegador. Por eso una recarga puede perderlos.\n\n',
    'Antes de conectarlo hay que definir qué datos se guardan y a qué campaña, proveedor y finca pertenecen. También se detectó un filtro que, para campaña 1, incluye registros de otras campañas; debe revisarse antes de usar ese almacén con datos reales.\n\n',
    '<details>\n<summary>Ver contraste de Calidad y evidencias del código</summary>\n\n',quality[quality.index('\n\n')+2:].strip()+'\n\n</details>\n\n']
pending=find('Módulos aún no persistidos')
out += ['## Funciones que todavía necesitan guardarse en la base (Plan > Cobertura funcional > Pendientes)\n\n',
    '**Esta lista dice qué funcionalidades todavía no tienen todas sus tablas y operaciones de guardado.** Que exista un formulario o un archivo de ejemplo no significa que sus registros ya estén guardados en PostgreSQL.\n\n',
    pending[pending.index('| Área'):]]
rules=find('Reglas que deben conservarse')
out += ['## Lo que ya funciona y debemos conservar (Plan > Compatibilidad > Protección de datos)\n\n',
    '**El modelo nuevo no debe hacerte perder reglas ni datos que ya tienes.** Por ejemplo: impedir que un chofer atienda dos viajes al mismo tiempo, conservar dimensiones del vehículo, SCTR, documentos y fechas de creación/modificación. Esta sección marca lo que el plan anterior omitía o representaba de otra forma.\n\n',
    '<details>\n<summary>Ver comparación de las reglas actuales con el plan</summary>\n\n',rules[rules.index('| Regla'):].strip()+'\n\n</details>\n\n']
mig=find('Migraciones y datos históricos')
out += ['## Cómo cambiar la estructura sin perder registros (Backend > Migraciones > Datos existentes)\n\n',
    '**Una migración es un cambio controlado de la estructura de la base.** Puede agregar una tabla, cambiar un campo o trasladar registros. La lista técnica describe los cambios que ya programaste; no son nueve tareas nuevas que tengas que repetir.\n\n',
    'La recomendación es verificar dónde quedará cada dato antes de cambiar la estructura. Por ejemplo, si separas contratos de cliente_negocio_campana, cada contrato debe seguir apuntando al cliente y a la campaña correctos. Los valores que hoy no existen no se pueden reconstruir inventándolos.\n\n',
    '<details>\n<summary>Ver migraciones existentes, riesgos y pruebas anteriores</summary>\n\n',mig[mig.index('| Orden'):].strip()+'\n\n</details>\n\n']
out += ['## Por dónde empezar (Plan > Implementación > Orden sugerido)\n\n',
    '**Es una propuesta de orden de trabajo, no una implementación ya realizada.**\n\n',
    '1. **Acordar las reglas que cambian:** campaña activa por fruta, certificados por campaña y cantidades por proveedor/finca.\n',
    '2. **Completar proveedores y campañas:** reutilizar proveedor, finca, campania_x_proveedores y entrevista_extencion.\n',
    '3. **Completar la parte comercial:** conservar cliente_negocio_campana y agregar contratos y entregas cuando se implemente ese flujo.\n',
    '4. **Conectar transporte y calidad:** identificar cada viaje, sus proveedores, sus pesos, sus documentos y su recepción.\n',
    '5. **Agregar liquidaciones, facturas y movimientos de dinero:** distinguir lo acordado, lo que se debe y lo que efectivamente se pagó o cobró.\n',
    '6. **Permitir el cierre de campaña al completar los pendientes:** conservar siempre la historia de los registros.\n\n',
    '**Decisión inmediata:** elegir el primer módulo a completar. Este documento explica qué adaptar; no obliga a reconstruir toda tu base ni indica que debas crear de golpe las 64 tablas del plan.\n']
audit.write_text(''.join(out),encoding='utf8')

# En los dos reportes por vista, separar nombres ya mapeados de nombres aún propuestos.
for filename in ['01_reporte_especifico.md','02_tablas_y_relaciones.md']:
    path=R/filename;s=path.read_text(encoding='utf8')
    def listing(m):
        ts=re.findall(r'`(\w+)`',m.group(1));real=[n for n in ts if n in names];new=[n for n in ts if n not in names]
        lines=[]
        if real:lines.append('**Tablas ya mapeadas en tu backend:** '+', '.join('`'+n+'`' for n in real)+'.')
        if new:lines.append('**Tablas propuestas, todavía no mapeadas:** '+', '.join('`'+n+'`' for n in new)+'.')
        return '\n\n'.join(lines)
    s=re.sub(r'\*\*Tablas(?: usadas)?:\*\* ([^\n]+)',listing,s)
    note='**Lectura de los nombres:** se muestran exactamente los nombres de tus entidades para las tablas existentes. Cada vista separa **tablas ya mapeadas** de **tablas propuestas**. En el reporte específico, los atributos del diccionario pertenecen al diseño objetivo; para ver los campos que tienes hoy, consulta la auditoría.\n\n'
    i=s.index('\n\n')+2;s=s[:i]+note+s[i:]
    path.write_text(s,encoding='utf8')
print('Auditoría simplificada: 20 nombres físicos exactos, explicación por tabla y detalles técnicos opcionales. Reportes por vista distinguen tablas existentes/propuestas.')
