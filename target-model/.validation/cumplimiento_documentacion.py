"""Documentación vigente generada desde el modelo; preserva auditorías previas."""
def ajustar(views, decisions):
    decisions.update({
      'D01':('Confirmado e incorporado al SQL','Participación única','Decisión del 29/10/2026: se retira la cabecera participacion_proveedor_campana. campania_x_proveedores conserva cxp_id, proveedor/campaña, cantidad, tipo, evaluación, precio y disponibilidad. Cobertura de certificados y proveedor_carga referencian cxp_id; no se mantiene una segunda participación.'),
      'D05':('Confirmado por el usuario','Autoridad de transporte','coordinacion_entrega es la fuente del viaje. Se conservan las tablas actuales por compatibilidad; ambas asignaciones usan instantes y exclusión [inicio,fin), permitiendo viajes sucesivos en el día.'),
      'D06':('Incorporado al SQL','Vincular antes del acuerdo','acuerdo_transporte admite BORRADOR sin condiciones completas; CONFIRMADO exige monto, tipo y fechas. No hace falta inventar un segundo vínculo.'),
      'D07':('Incorporado al SQL','Incorporación de campaña a Calidad','campana.calidad conserva un objeto por canal con su habilitación/estado, antes de crear cargas o elegir entregas.'),
      'D08':('Confirmado e incorporado al SQL','Destino como texto','Decisión del 29/10/2026: no existe CRUD independiente de destinos en el prototipo. Se retira el catálogo propuesto; entrega_programada.destino guarda texto obligatorio. La guía conserva direccion_llegada_snapshot, ubigeo_llegada_snapshot y establecimiento_llegada_snapshot propios, sin FK de destino.'),
      'D10':('Incorporado al SQL','Condiciones de compra','El precio simple vive en campania_x_proveedores.precio_compra_kg y moneda PEN. Se retira acuerdo_compra: no existe un flujo independiente de acuerdos/versiones en el prototipo. La liquidación conserva kilos reconocidos y precio aplicados.'),
      'D11':('Incorporado al SQL','Persona de la liquidación','La liquidación referencia persona directamente y admite proveedor principal o persona vinculada activa. Conserva snapshot de identidad; no exige un vínculo ficticio del proveedor consigo mismo. La autenticación operativa sigue en backend futuro.'),
      'D12':('Incorporado al SQL','Examen por etapas','Pendiente y Enviado admiten resultado/documento ausentes. Con resultado requiere resultado explícito. Se mantienen tipos positivo/negativo del backend para el dato final.'),
      'D14':('Confirmado por el usuario','Una carga por entrega','Se conserva un viaje/carga por entrega. Cosecha también es única por entrega. El SQL permite varias facturas de esa carga, con suma de kilos no superior a la recepción, según respuesta explícita del usuario.'),
      'D17':('Confirmado e incorporado al SQL','Sin sesiones persistidas','Se retira sesion_usuario y su FK a usuario por decisión expresa. Su función era guardar tokens, expiración y revocación, no solo historial. No se administran sesiones/dispositivos en este alcance; usuario y rol permanecen. La autenticación del backend debe resolverse sin depender de esta tabla.'),
      'D16':('Confirmado e incorporado al SQL','Catálogos iniciales y constantes','rol, norma, fruta, fruta_derivada y parametro_uit tienen datos iniciales SQL sin exigir CRUD. guia_x_norma guarda solo normas seleccionadas al guardar una guía, con FK y unicidad. Tipos de certificado, moneda, estados, etapas, métodos y conceptos se mantienen como opciones fijas, sin tablas adicionales. Los puentes de variedades derivadas de campaña/participación se retiran; las selecciones reales de proveedor, cliente y kilos de entrega permanecen.'),
      'D15':('Incorporado según respuesta del usuario','Varios requerimientos cliente/campaña','Se retira la unicidad cliente/campaña para permitir requerimientos independientes. Cada fila conserva sus contratos y entregas. El editor del prototipo aún debe alinearse con esta decisión.'),
    })
    for v in views:
        name=v['name']
        if name=='Entregas programadas':v['rule']='Cada entrega conserva su destino como texto obligatorio, sin seleccionar un catálogo. El servicio valida kilos y distribución por variedad frente al contrato.'
        if 'Exámenes' in name: v['rule']=decisions['D12'][2]
        if name in ['Contratos del cliente en campaña','Contratos — Participaciones comerciales']:v['rule']='Contrato con precio pendiente y condiciones de entrega/notas; cada requerimiento conserva sus contratos. Completar precio antes de facturar.'
        if name=='Proveedores de campaña':v['rule']=decisions['D10'][2]+' '+decisions['D01'][2]
        if name=='Entrevista':v['rule']='Entrevista por participación y finca del mismo proveedor; admite descripciones de distanciamiento/riego sin exigir escalares legacy inventados.'
        if name=='Cosecha y control de calidad':v['rule']=decisions['D07'][2]
        if name in ['Detalle de operación y carga','Cargas por entrega']:v['rule']='Organización, avances por finca/proveedor, cierre e inspección Industria se conservan en JSONB de cosecha. El servicio valida el contenido y las sumas; no se crea una tabla por pantalla.'
        if name=='Guías de remisión' or name=='Preparar guía de remisión':v['rule']='La guía conserva contenido completo en JSONB y cada proveedor_guia conserva sus fincas seleccionadas. Se mantiene guía/carga, kilos y normas. El destino es la dirección de llegada textual de la propia guía, junto a sus snapshots de ubigeo/establecimiento, sin catálogo. El servicio preserva el contenido al emitir.'
        if name=='Revisar cierre de campaña':v['rule']='Campana conserva fecha, usuario y motivo. Los triggers protegen importes con movimientos y límites de pagos/adelantos; el servicio aún debe verificar todos los pendientes de campaña y permisos antes de cerrar.'
    for v in views:
        if v['name']=='Gestión de Campaña':v['rule']='La campaña conserva una fruta. Las variedades disponibles se consultan desde fruta_derivada sin puente propio; la UI multifruta aún debe alinearse con ese acuerdo. Catálogos iniciales por SQL.'
        if v['name'] in ['Guías de remisión','Preparar guía de remisión']:v['rule']+=' Norma usa seed; cada selección del editor se resuelve por codigo y se guarda en guia_x_norma, sin insertar todas las normas. Se conserva standardText histórico en contenido.'
    return views,decisions

def introduccion(M,results):
    modified=sum(c['status']=='MODIFICAR' for t in M['tables'].values() for c in t['columns'])
    return f'''# Base de datos por vista — schema actualizado para cumplir la aplicación

**Versión vigente — 29/10/2026.** Se incorporan los ajustes FC01–FC13 de la auditoría y las respuestas del usuario: compra sobre kilos reconocidos en planta, varios requerimientos por cliente/campaña y varias facturas por carga. No se modifica el prototipo, la web, el backend ni una base desplegada. [SQL completo de instalación nueva](03_schema_total.sql).

**Modelo:** {len(M['tables'])} tablas ({M['existing_count']} actuales ampliadas y {M['new_count']} propuestas), {len(M['refs'])} FK y seis vistas. Se conservan por nombre 173 columnas legacy incluidas; **{modified} definiciones de columnas actuales cambian** y se agregan {M['additional_columns']} columnas a tablas actuales. No se afirma compatibilidad de tipos sin migración. Los detalles de formularios se conservan mediante JSONB en las tablas existentes, sin tablas nuevas por pantalla.

**D08 — Destino como texto (29/10/2026):** se retira el catálogo propuesto de destinos porque el prototipo no tiene CRUD propio. La entrega guarda `destino text NOT NULL`; la guía conserva su dirección/ubigeo/establecimiento de llegada como snapshots.

**Simplificación confirmada — 29/10/2026:** una sola participación en `campania_x_proveedores`; se retiran la cabecera duplicada, los dos puentes de variedades calculadas y `acuerdo_compra`. Se conserva `norma` con datos iniciales y `guia_x_norma` para selecciones reales. [Datos iniciales reejecutables](04_datos_iniciales.sql): dos perfiles, cinco normas, cinco frutas, 17 variedades y parámetros de 2025/2026 tomados del prototipo. El SQL total ya incluye esa carga. No se crean usuarios ni movimientos ficticios.

**D17 — Sesiones fuera del alcance:** se retira `sesion_usuario` (tokens, expiración y revocación). `usuario` y `rol` permanecen; la autenticación no deberá depender de una tabla de sesiones propia.

**Convenciones:** ACTUAL conserva el campo del backend; MODIFICAR cambia su definición en el objetivo; AGREGAR amplía una tabla actual; TABLA NUEVA pertenece a una entidad propuesta. PK/FK y relaciones corresponden al SQL objetivo. El diccionario de cada tabla aparece en su primera ficha y las siguientes lo reutilizan.

**Alcance:** no es una migración sobre datos existentes. Archivo sigue excluida y sus referencias son opcionales/sin FK. Los triggers nuevos validan recepción reconocida, persona de liquidación, facturación acumulada, sobrepagos y aplicaciones de adelantos; no sustituyen autenticación, permisos, validación completa del JSON, emisión documental ni el servicio de cierre de campaña.

**Verificación nueva:** {len(results['pruebas'])} comprobaciones ejecutadas en PGlite con btree_gist sobre este SQL; resultado y hash en `.validation/resultado_revision.json`. No son una prueba de navegador o de producción. Las auditorías anteriores se conservan al final como historial y describen el SQL anterior.

**Lectura por vistas:** se conserva el recorrido previo de 62 fichas; sus tablas, diccionarios y diagramas se regeneran desde el modelo actualizado. Las notas de observación del recorrido anterior no equivalen a una nueva prueba de la UI.
'''

def cierre(M,results):
    out=['## Schema actualizado tras la auditoría de cumplimiento','','Este apartado prevalece sobre los hallazgos y pendientes históricos conservados arriba. Los cambios se aplican al SQL de revisión, no a una base existente.','','| Auditoría | Persistencia incorporada |','|---|---|',
    '| D01/D10/D16 (29/10/2026) | Participación única, cuatro propuestas retiradas, catálogos con seed SQL y normas elegidas en guia_x_norma. Tipo de certificado como opción fija en tipo_certificacion y disponibilidad de cotización textual. |',
    '| D17 (29/10/2026) | Se retira sesion_usuario y su FK; se mantienen usuario y rol. Gestión persistente de sesiones/dispositivos fuera del alcance. |',
    '| D08 (29/10/2026) | Destino de entrega textual; guía con datos de llegada propios. Se excluye el catálogo de destinos y sus tres FK. |',
    '| FC01 | Documentos/teléfonos/códigos como texto, hectáreas decimales, RUC condicionado al tipo y dimensiones opcionales. |',
    '| FC02–FC03 | Precio simple en participación; MTD legacy y escalares agronómicos opcionales; examen por etapas. |',
    '| FC04–FC06 | Vigencia/historial de cobertura, contratos con precio pendiente y vínculo de transporte BORRADOR/CONFIRMADO. |',
    '| FC07 | Flete previo a liquidación, observación, moneda PEN y vencimiento del documento. |',
    '| FC08 | Habilitación de Calidad por canal y organización/avances/cierre/Industria en JSONB. |',
    '| FC09–FC10 | Contenido íntegro de guía, fincas por proveedor de guía, recepción reconocida por proveedor y detalle logístico/checklist. |',
    '| FC11–FC12 | Documento histórico de compra sobre reconocidos, persona principal/vinculada, facturación con ajustes y múltiples documentos por carga. |',
    '| FC13 | Triggers para sobrepago/cobro, aplicaciones disponibles/de la misma empresa-campaña, conservación de documentos con movimientos y suma de kilos facturados. El cierre completo sigue requiriendo servicio. |',
    '| FC14 | Integración documental diferida por acuerdo; no se crea archivo ni se añaden FK a ella. |','',
    '### Contrato mínimo de los objetos JSONB','','Los IDs de relaciones se guardan con los IDs reales del backend (enteros), no con IDs demo. Nombres de propiedades dentro del JSON reutilizan los del prototipo. La forma objeto/lista se comprueba en BD; contenido, permisos y referencias internas se validan en el servicio. No se guardan binarios/base64 en estos objetos.','','| Campo | Contenido que debe conservarse |','|---|---|',
    '| `campana.calidad` | Objeto por `Exportación`/`Industria`, con incorporación, estado y referencias de rechazos. |',
    '| `cosecha.organizacion` | `harvestDate`, `crewLead`, `serviceId`, confirmaciones, capacitación, `evidence`, `mobility`, `supplies`. |',
    '| `cosecha.avances` | Lista con `id`, `providerId`, `fincaId`, `date`, `kilos`, `crates`, `responsible`, `observations`, `evidence`. |',
    '| `cosecha.cierre` / `industria` | Objetos `closure` e `industry` de QualityOperation, incluidas referencias documentales y resultados/correcciones. |',
    '| `guia_remision.contenido` | RemissionGuideDetails completo. standardCodes refleja la selección persistida en guia_x_norma y standardText conserva la frase histórica; el servicio sincroniza ambos al guardar borrador y los congela al emitir. emitida_at distingue emisión. |',
    '| `proveedor_guia.fincas_ids` | Lista de IDs de fincas efectivamente elegidas para ese proveedor en esa guía. |',
    '| `recepcion_planta.compras` | Lista `purchases`: `providerId`, `recognizedQuantity`, referencia, cantidad original, documento, revisión y observación. El trigger comprueba proveedor real y reparto reconocido completo. |',
    '| `recepcion_planta.logistica` | Estado, ventana de llegada/atención, llegada real, espera/reprogramación, evaluación y observaciones de LogisticsDelivery. Inicio/fin de descarga tienen columnas propias. |',
    '| `recepcion_planta.checklist` / `documentos` | Confirmaciones con fecha/chofer y no aplica; metadatos de documentos del recorrido, sin fingir almacenamiento implementado. |',
    '| `liquidacion_proveedor.persona_snapshot` | Nombres, apellidos, tipoDocumento y dni del documento. El trigger lo captura desde la persona real al insertar y conserva después esa identidad histórica. |','',
    '### Definiciones existentes que cambian','','El siguiente inventario es para preparar una migración posterior. El SQL total no transforma históricos ni recupera ceros que ya se perdieron al guardar enteros.','','| Tabla.campo | Definición anterior | Definición objetivo |','|---|---|---|']
    for c in M['modified_columns']:
        out.append(f"| `{c['tabla']}.{c['columna']}` | `{c['antes']}` | `{c['despues']}` |")
    out += ['', '### Límites y trabajo de implementación pendiente','',
    '- Implementar DTO/servicios y adaptadores de la web para los nuevos campos y JSON; la propuesta SQL no conecta pantallas automáticamente.',
    '- Implementar la web/backend sobre cxp_id de campania_x_proveedores. Si existen datos de un diseño anterior, preparar mapeo de IDs antes de migrar; el SQL total solo instala el objetivo nuevo. La coordinación sigue siendo la fuente del viaje.',
    '- El schema permite varios requerimientos y facturas según las respuestas explícitas; el prototipo todavía bloquea esos casos y liquida compra sobre cargados. El backend/web deben adoptar la base reconocida y esas cardinalidades.',
    '- Validar transiciones, permisos del chofer, sumas de cosecha/guías, inmutabilidad de guías emitidas y pendientes completos de cierre en sus servicios. Los triggers financieros no son una implementación completa de esos procesos.',
    '- La UIT aplicada queda congelada por documento. Si un año contiene parámetros aplicados diferentes, la vista anual separa grupos por esos parámetros; el servicio debe mostrar/conciliar la configuración, no asumir un único grupo.',
    '- Los bloqueos de fila financieros se ejecutaron en PGlite; no se acredita una prueba de concurrencia con varias conexiones de un servidor PostgreSQL.',
    '', f"**Resultado ejecutado:** {len(results['pruebas'])} comprobaciones correctas sobre {len(M['tables'])} tablas y {len(M['refs'])} FK. Consultar `resultado_revision.json` para los escenarios y hash exactos.",'']
    return '\n'.join(out)
