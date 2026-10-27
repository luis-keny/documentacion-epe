"""Documentación vigente generada desde el modelo; preserva auditorías previas."""
def ajustar(views, decisions):
    decisions.update({
      'D01':('Compatibilidad conservada','Participación adicional','Se conservan ambas tablas y sus dependencias. El editor usa campania_x_proveedores con precio simple; el servicio mantiene la correspondencia con la cabecera usada en cargas. No se exige consolidar por calidad ni se elimina una tabla sin autorización.'),
      'D05':('Confirmado por el usuario','Autoridad de transporte','coordinacion_entrega es la fuente del viaje. Se conservan las tablas actuales por compatibilidad; ambas asignaciones usan instantes y exclusión [inicio,fin), permitiendo viajes sucesivos en el día.'),
      'D06':('Incorporado al SQL','Vincular antes del acuerdo','acuerdo_transporte admite BORRADOR sin condiciones completas; CONFIRMADO exige monto, tipo y fechas. No hace falta inventar un segundo vínculo.'),
      'D07':('Incorporado al SQL','Incorporación de campaña a Calidad','campana.calidad conserva un objeto por canal con su habilitación/estado, antes de crear cargas o elegir entregas.'),
      'D10':('Incorporado al SQL','Condiciones de compra','El precio simple vive en campania_x_proveedores.precio_compra_kg y moneda PEN. acuerdo_compra queda como compatibilidad opcional sin exigir tarifarios/fechas/variedad nuevas. La liquidación conserva kilos reconocidos y precio aplicados.'),
      'D11':('Incorporado al SQL','Persona de la liquidación','La liquidación referencia persona directamente y admite proveedor principal o persona vinculada activa. Conserva snapshot de identidad; no exige un vínculo ficticio del proveedor consigo mismo. La autenticación operativa sigue en backend futuro.'),
      'D12':('Incorporado al SQL','Examen por etapas','Pendiente y Enviado admiten resultado/documento ausentes. Con resultado requiere resultado explícito. Se mantienen tipos positivo/negativo del backend para el dato final.'),
      'D14':('Confirmado por el usuario','Una carga por entrega','Se conserva un viaje/carga por entrega. Cosecha también es única por entrega. El SQL permite varias facturas de esa carga, con suma de kilos no superior a la recepción, según respuesta explícita del usuario.'),
      'D15':('Incorporado según respuesta del usuario','Varios requerimientos cliente/campaña','Se retira la unicidad cliente/campaña para permitir requerimientos independientes. Cada fila conserva sus contratos y entregas. El editor del prototipo aún debe alinearse con esta decisión.'),
    })
    for v in views:
        name=v['name']
        if 'Exámenes' in name: v['rule']=decisions['D12'][2]
        if name in ['Contratos del cliente en campaña','Contratos — Participaciones comerciales']:v['rule']='Contrato con precio pendiente y condiciones de entrega/notas; cada requerimiento conserva sus contratos. Completar precio antes de facturar.'
        if name=='Proveedores de campaña':v['rule']=decisions['D10'][2]+' '+decisions['D01'][2]
        if name=='Entrevista':v['rule']='Entrevista por participación y finca del mismo proveedor; admite descripciones de distanciamiento/riego sin exigir escalares legacy inventados.'
        if name=='Cosecha y control de calidad':v['rule']=decisions['D07'][2]
        if name in ['Detalle de operación y carga','Cargas por entrega']:v['rule']='Organización, avances por finca/proveedor, cierre e inspección Industria se conservan en JSONB de cosecha. El servicio valida el contenido y las sumas; no se crea una tabla por pantalla.'
        if name=='Guías de remisión' or name=='Preparar guía de remisión':v['rule']='La guía conserva contenido completo en JSONB y cada proveedor_guia conserva sus fincas seleccionadas. Se mantiene guía/carga, kilos y normas. El servicio preserva el contenido al emitir.'
        if name=='Revisar cierre de campaña':v['rule']='Campana conserva fecha, usuario y motivo. Los triggers protegen importes con movimientos y límites de pagos/adelantos; el servicio aún debe verificar todos los pendientes de campaña y permisos antes de cerrar.'
    return views,decisions

def introduccion(M,results):
    modified=sum(c['status']=='MODIFICAR' for t in M['tables'].values() for c in t['columns'])
    return f'''# Base de datos por vista — schema actualizado para cumplir la aplicación

**Versión vigente — 27/10/2026.** Se incorporan los ajustes FC01–FC13 de la auditoría y las respuestas del usuario: compra sobre kilos reconocidos en planta, varios requerimientos por cliente/campaña y varias facturas por carga. No se modifica el prototipo, la web, el backend ni una base desplegada. [SQL completo de instalación nueva](03_schema_total.sql).

**Modelo:** 66 tablas (19 actuales ampliadas y 47 propuestas), {len(M['refs'])} FK y seis vistas. Se conservan por nombre 173 columnas legacy incluidas; **{modified} definiciones de columnas actuales cambian** y se agregan {M['additional_columns']} columnas a tablas actuales. No se afirma compatibilidad de tipos sin migración. Los detalles de formularios se conservan mediante JSONB en las tablas existentes, sin tablas nuevas por pantalla.

**Convenciones:** ACTUAL conserva el campo del backend; MODIFICAR cambia su definición en el objetivo; AGREGAR amplía una tabla actual; TABLA NUEVA pertenece a una entidad propuesta. PK/FK y relaciones corresponden al SQL objetivo. El diccionario de cada tabla aparece en su primera ficha y las siguientes lo reutilizan.

**Alcance:** no es una migración sobre datos existentes. Archivo sigue excluida y sus referencias son opcionales/sin FK. Los triggers nuevos validan recepción reconocida, persona de liquidación, facturación acumulada, sobrepagos y aplicaciones de adelantos; no sustituyen autenticación, permisos, validación completa del JSON, emisión documental ni el servicio de cierre de campaña.

**Verificación nueva:** {len(results['pruebas'])} comprobaciones ejecutadas en PGlite con btree_gist sobre este SQL; resultado y hash en `.validation/resultado_revision.json`. No son una prueba de navegador o de producción. Las auditorías anteriores se conservan al final como historial y describen el SQL anterior.

**Lectura por vistas:** se conserva el recorrido previo de 62 fichas; sus tablas, diccionarios y diagramas se regeneran desde el modelo actualizado. Las notas de observación del recorrido anterior no equivalen a una nueva prueba de la UI.
'''

def cierre(M,results):
    out=['## Schema actualizado tras la auditoría de cumplimiento','','Este apartado prevalece sobre los hallazgos y pendientes históricos conservados arriba. Los cambios se aplican al SQL de revisión, no a una base existente.','','| Auditoría | Persistencia incorporada |','|---|---|',
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
    '| `guia_remision.contenido` | `RemissionGuideDetails` completo y, si procede, lista/snapshot de campos impresos. `emitida_at` distingue emisión. |',
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
    '- Preservar IDs y correspondencia de las dos tablas de participación; no se eliminó ninguna. La coordinación es la fuente operativa del viaje.',
    '- El schema permite varios requerimientos y facturas según las respuestas explícitas; el prototipo todavía bloquea esos casos y liquida compra sobre cargados. El backend/web deben adoptar la base reconocida y esas cardinalidades.',
    '- Validar transiciones, permisos del chofer, sumas de cosecha/guías, inmutabilidad de guías emitidas y pendientes completos de cierre en sus servicios. Los triggers financieros no son una implementación completa de esos procesos.',
    '- La UIT aplicada queda congelada por documento. Si un año contiene parámetros aplicados diferentes, la vista anual separa grupos por esos parámetros; el servicio debe mostrar/conciliar la configuración, no asumir un único grupo.',
    '- Los bloqueos de fila financieros se ejecutaron en PGlite; no se acredita una prueba de concurrencia con varias conexiones de un servidor PostgreSQL.',
    '', f"**Resultado ejecutado:** {len(results['pruebas'])} comprobaciones correctas sobre 66 tablas y {len(M['refs'])} FK. Consultar `resultado_revision.json` para los escenarios y hash exactos.",'']
    return '\n'.join(out)
