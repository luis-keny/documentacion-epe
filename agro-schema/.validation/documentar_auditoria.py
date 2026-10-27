from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent
APP=R.parent.parent
CURRENT=json.loads((R/'.validation/modelo_actual.json').read_text(encoding='utf8'))
RUN=json.loads((R/'.validation/resultado_actual.json').read_text(encoding='utf8'))
PLAN=json.loads((R/'.validation/modelo_alineado.json').read_text(encoding='utf8'))
RENAME=json.loads((R/'.validation/renombres_tablas.json').read_text(encoding='utf8'))
ACT={x['table']:x for x in CURRENT}
REV=json.loads((R/'.validation/revision_actualizacion.json').read_text(encoding='utf8'))
dest=APP/'epe-backend/docs/auditoria-bd-actual-vs-planificada.md'
def link(path,pattern=None,label=None):
    p=APP/path;line=1
    if pattern:
        for n,text in enumerate(p.read_text(encoding='utf8').splitlines(),1):
            if pattern in text:line=n;break
    return f"[{label or p.name}]({p.as_posix()}:{line})"
def source(t):return link(ACT[t]['source'],'@Entity',t)
def code(text):return '`'+text+'`'

notes={
'archivo':('Archivos','Infraestructura > Archivos',
'Tiene bucket, object_key, nombre original, MIME, tamaño, checksum, estado y auditoría; certificado_proveedor ya utiliza una FK real a archivo. Los demás dominios conservan varias URLs.',
'Se mantiene el nombre archivo. La propuesta anterior tenía ruta_storage, nombre/tipo_mime/bytes, subido_por y fecha_subida; no modelaba bucket ni ciclo de vida. Conservar bucket + object_key y estados PENDIENTE/DISPONIBLE/ELIMINACION_PENDIENTE/ELIMINADO/ERROR. Extender el uploader existente a los demás módulos, en vez de construir otro almacenamiento paralelo. Una URL no se convierte en FK sin resolver y verificar su objeto.'),
'campana':('Gestión de Campaña','Administrador > Gestión de Campaña > Campaña',
'Guarda fruta, fechas, estado y requerimiento_comercial como importe de kg editable. No hay responsable, variedades seleccionadas, temporada, archivo de lineamientos o cierre documentado.',
'Mantener campana y agregar esos campos/relaciones por migración. El plan separa requerimiento original y agregados derivados; no sustituir requerimiento_comercial hasta determinar su significado y reconciliar sus valores. Estado actual planificacion/en proceso/terminado difiere de PLANIFICADO/EN_PROCESO/FINALIZADO. La unicidad parcial UQ_campana_fruta_activa permite solo una campaña no terminada por fruta: el SQL objetivo no la conserva y su retirada requiere decisión de negocio.'),
'campania_x_proveedores':('Proveedores de campaña','Administrador > Gestión de Campaña > Campaña > Proveedores',
'Una fila contiene campaña/proveedor y opcionalmente una finca, cantidad_proveedor, mtd_ceratitis, fruta_convencional_estimado, tipo_proveedor y estado sin validar/validado. Admite varias filas para un mismo proveedor/campaña con fincas diferentes y una fila sin finca.',
'Se reserva campania_x_proveedores para el nivel de finca del objetivo, que antes se llamaba fincas_campania. La nueva participacion_proveedor_campana agrupa campaña/proveedor, rol, oferta y evaluación. No renombrar esta tabla como si ya fuera esa cabecera. Elegir qué hacer con filas sin finca: conservarlas como cabeceras sin detalle, no inventar una finca. Reconciliar cantidades antes de agregarlas porque no está demostrado que cada cantidad sea aditiva por finca. Guardar una equivalencia cxp_id antiguo → participación nueva/detalle nuevo para migrar trazabilidades y entrevistas. El estado actual sin validar/validado no equivale por sí solo a los estados pendientes de examen/entrevista y aprobado/rechazado del objetivo.'),
'certificado_campana':('Certificaciones de campaña','Administrador > Gestión de Campaña > Campaña > Certificaciones',
'Cada certificado tiene nombre, URL del documento, costo, URL de recibo, vencimiento, estado y campaña. No tiene unicidad de campaña: admite varios certificados por campaña.',
'Mantener nombre, pero ampliar organismo, norma, emisión, moneda y productores cubiertos. Crear pago_certificado_campana y ampliacion_certificado_campana. La UI de referencia y el plan dicen uno por campaña; el backend admite varios: revisar datos antes de imponer UNIQUE(campania_id). recibo_url no acredita monto, fecha o pago total. No inferir un movimiento financiero por la sola presencia del recibo.'),
'certificado_proveedor':('Certificados propios','Administrador > Gestión de Proveedores > Proveedor > Certificados',
'Registro propio por proveedor; fecha_revision_senasa obligatoria y documento_archivo_id opcional. La migración de archivos sustituyó documento_url por una FK al storage.',
'Conservar certificado_proveedor; este es el equivalente de certificados_propios, no el de la tabla puente del DBML certificacion_proveedor. La cobertura del certificado de campaña se llama certificado_campana_x_proveedor. El objetivo pide archivo obligatorio y permite fecha opcional: revisar esta inversión de nulabilidad. Completar documentos pendientes sin eliminar certificados históricos.'),
'chofer_transporte_externo':('Choferes','Administrador > Gestión de Transporte > Transportista > Choferes',
'Guarda nombre completo, teléfono y correo y pertenece a empresa_transporte_externo. No hay documento, licencia, persona_id, usuario_id ni cuenta de acceso en esta entidad.',
'Conservar nombre y crear identidad compartida en persona y cuenta en usuario cuando corresponda. No partir un nombre completo automáticamente en nombres/apellidos sin validar. Completar documento y licencia como datos pendientes, sin fabricar identificadores. La FK compuesta del objetivo comprueba empresa común; preservar también las validaciones de asignación actuales.'),
'chofer_vehiculo_externo':('Asignaciones de chofer y vehículo','Administrador > Gestión de Transporte > Asignaciones',
'Relaciona trazabilidad, chofer y vehículo con fechas de inicio/final. Tiene CHECK de fechas y EXCLUDE GiST que impide solapamiento del mismo chofer, con extremos de fecha incluidos.',
'No hay equivalencia 1:1. Su información alimenta coordinacion_entrega; primero hace falta identificar una entrega y su acuerdo. El objetivo anterior no conserva una tabla de historial de reasignaciones ni la exclusión de solapamientos. Preservar esa protección y decidir si las asignaciones históricas seguirán en esta tabla o en una tabla hija nueva. No asumir que llegada significa CIERRE del nuevo checklist.'),
'cliente_negocio':('Clientes','Administrador > Gestión Comercial > Clientes',
'Guarda empresa/contacto/teléfono/RUC/correo/ubicación/tipo; RUC y correo corporativo son únicos. Tiene created_at y updated_at.',
'Es la misma identidad que clientes del plan; conservar cliente_negocio y sus identificadores de origen. La propuesta anterior reducía longitudes y omitía la unicidad de correo. Antes de migrar, comprobar longitudes y decidir mantener unicidad de correo sin romper clientes que comparten una dirección corporativa.'),
'cliente_negocio_campana':('Participación cliente–campaña y contratos','Administrador > Gestión Comercial > Campaña > Cliente > Contratos',
'Tiene UNIQUE(cliente_negocio_id,campania_id), documento_url, ficha_tecnica_url, fecha_registro, cantidad_kg y kilos_acordados. El servicio devuelve estas filas como contratos; no hay tabla contrato independiente.',
'Conservar cliente_negocio_campana como vínculo/requerimiento comercial (antes requerimientos_comerciales). Crear contrato_venta 1:N, y después entrega_programada. Reubicar documento_url y kilos_acordados en el contrato cuando sean datos contractuales; cantidad_kg y ficha técnica siguen en la necesidad original. El plan permite varios requerimientos por cliente/campaña y no conserva la unicidad actual: decidir si se mantiene un vínculo único o se agrega identidad explícita de requerimiento. No crear un contrato vigente a partir de un documento vacío o ambiguo.'),
'detalle_trazabilidad':('Costos y documentos del transporte','Administrador > Gestión de Transporte > Trazabilidad > Detalle',
'Cada trazabilidad puede tener varios detalles con guia_url, flete, sctr, estibas, pasajes y comida. Los costos tienen CHECK no negativo.',
'No es solo gasto_transporte. Separar documento de guía, liquidacion_transporte y gastos por concepto, conservando SCTR. El objetivo anterior no guardaba SCTR y limita una liquidación por carga; agrupar detalles solo después de identificar si representan viajes, versiones o gastos distintos. Un flete registrado no implica que exista pago. Una guía URL tampoco equivale a guía de remisión con campos estructurados.'),
'empresa_transporte_externo':('Transportistas','Administrador > Gestión de Transporte > Transportistas',
'Nombre completo, RUC y correo únicos, y número de contacto. No diferencia empresa/independiente ni guarda ubicación, MTC o persona asociada.',
'Conservar nombre. Agregar tipo/documento genérico y persona_id para independientes, además de ubicación/MTC si el flujo los necesita. El objetivo sustituye ruc por tipo_documento/numero_documento; planificar backfill de RUC existentes y conservar su unicidad para empresas. No clasificar personas jurídicas o independientes solo por el texto del nombre.'),
'entrevista_extencion':('Entrevistas de extensión','Administrador > Gestión de Campaña > Proveedor > Entrevistas',
'Ya existe entidad y migración de entrevista, con FK a campania_x_proveedores y finca; densidad, distanciamiento y frecuencia numéricos; nombre_aplicacion; anio_aplicacion y código único FVV. El servicio genera el código por prefijo normalizado del nombre de campaña con advisory lock transaccional. La migración valida productor/finca con triggers y protege las asignaciones con entrevistas.',
'Conservar el nombre físico exacto entrevista_extencion, incluida su escritura actual, en lugar de crear entrevista_finca_campana paralela. El plan usa codigo_fyv, fecha explícita de registro, densidad_plantacion, distanciamiento_m textual, frecuencia_riego textual y aplicaciones_anio. anio_aplicacion es año calendario y no número de aplicaciones al año: no convertir 2026 en 2026 aplicaciones. Un valor escalar de distanciamiento no equivale automáticamente a una separación 5 x 4. El código FVV actual y FYV del prototipo difieren; preservar los códigos históricos y definir la nueva convención antes de migrar. Si se conserva la separación cabecera/fincas, reubicar sus FK con equivalencia de IDs; el vínculo actual permite una asignación sin finca que tenga entrevistas a distintas fincas del proveedor.'),
'examen_proveedor':('Exámenes','Administrador > Gestión de Campaña > Proveedor > Exámenes',
'Se relaciona directamente a proveedor, sin campaña ni finca. Exige resultado positivo/negativo y documento_url; tiene fecha, tipo_examen, origen y observacion.',
'Conservar nombre, pero ampliar alcance con participación y finca opcional, código de muestra, fecha de envío, pendiente de resultado y archivo. No asignar retrospectivamente todos los exámenes a una campaña arbitraria; mantener registros generales o una cola de revisión. positivo/negativo no se mapea automáticamente a aprobado/rechazado: depende del tipo de análisis.'),
'finca':('Fincas','Administrador > Gestión de Proveedores > Proveedor > Fincas',
'Pertenece a proveedor; guarda nombre, geografía y coordenadas obligatorias, hectáreas enteras y CHECK de hectáreas válidas.',
'Conservar finca. El objetivo usa hectáreas decimales, códigos SENASA/catastro/establecimiento, ubigeo, dirección, variedad y edad, además de coordenadas opcionales. Permitir decimales es ampliación de precisión, pero el objetivo exige hectáreas totales > 0 donde hoy se acepta cero. Separar padrón físico de entrevista_extencion; no copiar un perfil agronómico global como si fuera medición histórica de cada finca.'),
'fruta':('Catálogo de frutas','Administrador > Gestión de Campaña > Catálogos > Frutas',
'Clave fruta_id int y nombre en columna name. No existe unicidad del nombre en la entidad/migración.',
'Conservar fruta y mapear name → nombre si se adopta el diccionario del objetivo. El plan agrega unicidad y reduce longitud 150 → 80: detectar duplicados, mayúsculas/espacios y textos largos antes de aplicarlo. No deduplicar IDs sin actualizar las FK y los consumidores.'),
'fruta_derivada':('Variedades','Administrador > Gestión de Campaña > Catálogos > Variedades',
'Clave fruta_derivada_id, nombre name y FK a fruta. El código de API expone subrecurso de frutas; no tiene UNIQUE(fruta_id,name).',
'Conservar fruta_derivada como nombre físico para el concepto de variedad del plan. Agregar selección de campaña/proveedor y controles de fruta compatible. La compatibilidad de nombre no significa que variedad_id del objetivo sea ya la PK del backend: se requiere una correspondencia explícita de columnas.'),
'proveedor':('Proveedores','Administrador > Gestión de Proveedores > Proveedor',
'Contiene identidad y contacto directamente: nombres, apellido, tipo_documento enum, nmr_documento int, teléfono int, email, documento URL y código de producción int. También conserva el perfil agronómico global y sanidad.',
'Conservar proveedor como identidad comercial, extraer persona sin duplicar al mismo individuo y mantener una tabla de equivalencias. Convertir documento/teléfono/códigos a texto para soportar ceros iniciales, prefijos y letras. Agregar unicidad documental en persona tras depurar duplicados; el SQL actual acepta proveedores con documento/email repetidos. Crear proveedor_x_persona y reutilizar entrevista_extencion para la agronomía histórica, reconciliando sus campos con el perfil global. No eliminar los campos globales antes de verificar el traslado y sus consumidores.'),
'proveedor_x_fruta':('Frutas del proveedor','Administrador > Gestión de Proveedores > Proveedor > Frutas',
'Tabla puente con pxf_id y UNIQUE(proveedor_id,fruta_id); FK en CASCADE a ambos extremos.',
'Conservar nombre y relación. El objetivo cambia las bajas a RESTRICT y añade vínculo a variedades en proveedor_x_fruta_derivada. Mantener la unicidad existente. La eliminación de asociaciones del catálogo no debe borrar compras, guías o documentos financieros.'),
'trazabilidad_transporte':('Trazabilidad de transporte','Administrador > Gestión de Transporte > Trazabilidad',
'Una fila depende de un solo cxp_id; tiene contrato_url, kg_comprados, kg_planta y estado planificado/en recojo/despachado/llegada. Puede tener varias asignaciones y detalles. No identifica contrato de venta, cliente, entrega o carga multiproveedor.',
'Descomponer entre coordinacion_entrega, carga, proveedor_carga, recepcion_planta e historial_chofer, vinculando al contrato/cliente correcto. No renombrarla directamente como carga: su grano es una relación de proveedor/campaña/finca, mientras que una carga del prototipo reúne proveedores. No agrupar registros solo por fecha/placa/chofer; se necesita una clave de viaje aprobada. kg_planta puede ser un dato histórico de recepción, pero no prueba resultado, reporte, descarte o cierre.'),
'vehiculo_externo':('Vehículos','Administrador > Gestión de Transporte > Transportista > Vehículos',
'Placa única; volumen, ancho, altura y profundidad obligatorios y positivos; peso_neto y peso_bruto con control de orden. Pertenece a una empresa.',
'Conservar nombre. El plan anterior guardaba volumen_m3, capacidad_kg y peso_bruto_kg, omitiendo dimensiones. No convertir peso_neto en capacidad sin definir si es tara, carga útil u otro dato. Conservar dimensiones y pesos originales; añadir capacidad_kg como dato independiente cuando se confirme. Las conversiones de t/kg se deben documentar y comprobar.'),
}
assert set(notes)==set(ACT)

out=['# Auditoría de la base programada frente al esquema planificado','',
f'Fecha: **2026-10-25 (America/Lima)**. **Reauditoría solicitada tras actualizar los repositorios.** Alcance: código local de `epe-backend`, sus entidades TypeORM, {len(RUN["migraciones"])} migraciones y servicios relevantes. Revisión de código: `{REV["revision"]}`. Se utilizó también el esquema propuesto a partir del prototipo, con nomenclatura actualizada.','',
'**Conclusión:** el backend actual cubre la base de campañas, proveedores, fincas, catálogos, clientes, certificados y un modelo inicial de transporte. No equivale al flujo completo del prototipo. La diferencia no es solo de nombres: cambian granularidad, obligatoriedad, estados, documentos y procesos financieros. La prioridad es reutilizar lo implementado y ampliarlo con migraciones, evitando crear tablas duplicadas para conceptos que ya existen.','',
'**Entregables actualizados:** [reporte específico](../../docs/agro-schema/01_reporte_especifico.md), [tablas y relaciones Mermaid](../../docs/agro-schema/02_tablas_y_relaciones.md) y [SQL objetivo](../../docs/agro-schema/03_schema_total.sql). El reporte compara aquí el **código actual** con el **objetivo**; el DBML original es una referencia histórica distinta.','',
'**Límite de verificación:** no se leyó `.env`, no se inspeccionaron filas de la base del usuario y no se conectó a una instancia desplegada. “Actual” significa programado en estas fuentes y reproducido en una base temporal; no significa que las migraciones estén aplicadas en producción. No se renombró ninguna tabla real, entidad, DTO o endpoint. El SQL entregado sigue siendo una instalación nueva en `agro`, no un script de upgrade sobre las tablas existentes.','',
'## Reauditoría de las actualizaciones (Backend y frontend > Actualizaciones > Comparación)','',
f'**Resultado de esta nueva pasada:** se recalcularon los hashes SHA-256 de los {REV["fuentes_revisadas"]} archivos TypeScript del backend y se reconstruyeron sus metadatos TypeORM. No se encontraron archivos nuevos, modificados ni eliminados respecto de la auditoría anterior. Los metadatos y las sentencias `up` de las nueve migraciones también coinciden. La rama local `master` y la referencia local `origin/master` apuntan a `{REV["revision"][:7]}`; no se ejecutó un fetch ni se afirma que esa referencia local refleje cambios todavía no descargados del servidor remoto.','',
'La auditoría anterior **ya había incorporado `entrevista_extencion` y la novena migración** en su comprobación final. Por eso el inventario sigue siendo 20 tablas, 184 columnas y 23 FK, y se mantienen los 17 nombres compartidos con las 64 tablas objetivo. No hay nuevos renombrados de tablas que aplicar en esta pasada.','',
f'**Cambio visible en el frontend:** su HEAD es `{REV["frontend_revision"][:7]}` (`feat: nuevo módulo de cosecha y control de calidad`). Se revisaron los modelos y almacenes locales de ese módulo para distinguir funcionalidad visual de persistencia relacional. El catálogo del modal consulta `GET /campanas`; agregar campañas al módulo usa memoria y las acciones Análisis/Carga/Guías muestran avisos de preparación. Esto no añade tablas o endpoints de calidad al backend. Se documentan dos hallazgos adicionales A17–A18 y un contraste detallado de estos datos con el plan más abajo.','',
'**Procedencia de las pruebas:** las 16 comprobaciones PGlite del esquema actual y las 29 del SQL objetivo son evidencia de la pasada anterior sobre las mismas fuentes. En esta pasada no se repitieron instalaciones ni se afirma una nueva ejecución de esas pruebas; se verificó que sus fuentes, sentencias de migración y metadatos no cambiaron. No se modificó código funcional.','',
'## Inventario y método (Backend > Esquema actual > Verificación)','',
'| Elemento | Resultado verificado |','|---|---|',
f'| Entidades de dominio | {len(CURRENT)} tablas |',
f'| Columnas, incluidas auditoría y FK | {len(RUN["columns"])} |',
f'| Claves foráneas de las entidades | {sum(len(t["foreignKeys"]) for t in CURRENT)} |',
f'| Migraciones `up` reproducidas | {len(RUN["migraciones"])} |',
'| Esquema objetivo | 64 tablas, 151 FK y 6 vistas SQL |',
'| Nombres existentes conservados en el objetivo | 17 |',
'| Tablas objetivo sin tabla homónima actual | 47; no es porcentaje de trabajo restante |',
'| Tablas actuales sin equivalencia 1:1 | 3, todas de transporte |',
'| Tablas técnicas de TypeORM | `typeorm_migrations` configurada, excluida del inventario de dominio |','',
'**Fuentes de verdad:** '+link('epe-backend/src/config/typeorm.datasource.ts','entities:','registro de entidades y migraciones')+', '+link('epe-backend/src/config/database.config.ts','return {','configuración de runtime')+' y '+link('epe-backend/AGENTS.md','fuente de verdad','convención del repositorio')+f'. Se construyeron los metadatos de TypeORM sin inicializar una conexión. Se ejecutaron las {len(RUN["migraciones"])} migraciones en PGlite (PostgreSQL WASM, con `btree_gist`), y se contrastaron nombres y nulabilidad de sus {len(RUN["columns"])} columnas: no hubo diferencias con las entidades en ese contraste. No se afirma equivalencia exhaustiva de defaults, precisión, nombres de constraints, planes de consulta o configuración del servidor.','',
'El runtime utiliza `autoLoadEntities` y recibe `DB_SYNCHRONIZE` de configuración; su valor por defecto es false. La CLI tiene `synchronize: false` y registra las migraciones. Debe conservarse el uso de migraciones sin habilitar sincronización automática para desplegar este plan. No se verificó el valor efectivo de una instancia.','',
'| Tabla física actual | PK actual | Columnas | Equivalencia con el plan | Fuente |','|---|---|---:|---|---|']
inverse={v:k for k,v in RENAME.items()}
legacy={
'trazabilidad_transporte':'Descomponer en coordinación, carga, detalles de proveedor, recepción y eventos.',
'chofer_vehiculo_externo':'Reutilizar datos en coordinación; conservar historial/restricciones de asignación.',
'detalle_trazabilidad':'Separar guía, flete, gastos y SCTR; no registrar pagos por inferencia.'}
for t in CURRENT:
    name=t['table'];pk=', '.join(c['name'] for c in t['columns'] if c['primary'])
    action=f"Conservar nombre; antes `{inverse[name]}`. Hay ajustes de estructura." if name in inverse else legacy[name]
    out.append(f'| `{name}` | `{pk}` | {len(t["columns"])} | {action} | {source(name)} |')
out+=['','**Auditoría transversal existente:** todas las entidades heredan `created_at` y `updated_at` desde '+link('epe-backend/src/common/entities/auditable.entity.ts','export abstract','AuditableEntity')+'. El plan anterior no las incluía de forma uniforme. Deben conservarse al diseñar migraciones; una fecha de subida o emisión no reemplaza la auditoría de cambios.','',
'## Relaciones implementadas (Backend > Esquema actual > Relaciones Mermaid)','',
'Diagrama derivado de las FK reales de las entidades. Las cajas son tablas actuales. `||` = uno; `o|` = cero o uno; `o{` = cero o muchos. No muestra atributos ni confunde relaciones del plan con relaciones implementadas.','', '```mermaid','erDiagram']
for t in CURRENT:
    for fk in t['foreignKeys']:
        nullable=any(next(c for c in t['columns'] if c['name']==field)['nullable'] for field in fk['columns'])
        out.append(f"    {fk['parent']} {'o|' if nullable else '||'}..o{{ {t['table']} : referencia")
out+=['```','',
'## Cambios de nomenclatura (Plan > Tablas propuestas > Nombres alineados)','',
'Se mantienen los nombres ya usados en `@Entity({ name: ... })` cuando corresponden al mismo concepto. Las tablas nuevas siguen nombres singulares. La alineación se aplicó a ambos reportes, sus diagramas y las referencias del SQL objetivo; las columnas y las relaciones siguen siendo las propuestas y deben migrarse explícitamente.','',
'**Distinción de mayor impacto:** `participaciones_proveedor` no se cambió directamente a `campania_x_proveedores`. La tabla actual es de campaña/proveedor/finca, así que su nombre se reserva para el detalle antes llamado `fincas_campania`; la cabecera nueva es `participacion_proveedor_campana`. Esto evita una equivalencia falsa y preserva el vínculo de las trazabilidades actuales a `cxp_id`.','',
'| Nombre del plan anterior | Nombre objetivo actualizado | Situación frente al código actual |','|---|---|---|']
for old,new in RENAME.items():
    state='Existe con otro alcance; requiere separar cabecera y finca' if new=='campania_x_proveedores' else ('Existe; ampliar o ajustar, no recrear en paralelo' if new in ACT else 'Nueva tabla propuesta; no implementada en las entidades auditadas')
    out.append(f'| `{old}` | `{new}` | {state} |')
out+=['',
'**No hay un renombrado físico simple:** aun compartiendo nombre, las tablas actuales usan PK `int`/SERIAL con nombres propios (`campania_id`, `cxp_id`, etc.); el SQL objetivo usa `id bigint` identity. Lo mismo ocurre con FK como `fruta_derivada_id` frente al identificador lógico `variedad_id`. No ejecutar el SQL objetivo como si TypeORM pudiera usarlo sin cambios: hacen falta migraciones, mappers, DTO y pruebas de compatibilidad. No se debe reiniciar o reasignar arbitrariamente IDs históricos.','',
'## Diferencias prioritarias (Plan > Auditoría > Hallazgos)','',
'Prioridad **Alta**: puede perder identidad, trazabilidad, historial o compatibilidad. **Media**: impide completar el flujo o cambia reglas que deben reconciliarse. **Decisión**: diferencia entre reglas válidas que necesita definirse antes de migrar; se documenta sin resolverla arbitrariamente.','',
'| ID | Prioridad | Diferencia comprobada | Efecto y acción requerida |','|---|---|---|',
'| A01 | Alta | Proveedor mezcla persona y perfil agronómico global; documento/teléfono/código son enteros. | Separar identidad y agronomía por finca/campaña; convertir identificadores a texto, depurar duplicados y preservar equivalencias. |',
'| A02 | Alta | `campania_x_proveedores` admite varias fincas y fila sin finca, distinto de la cabecera del plan. | Crear cabecera, migrar hijos sin inventar fincas y no sumar oferta repetida sin validar. |',
'| A03 | Alta | `trazabilidad_transporte` depende de un solo `cxp_id`; una carga objetivo puede incluir muchos proveedores. | Identificar viajes reales y crear coordinación/carga/detalle; no agrupar por similitud de fechas. |',
'| A04 | Alta | Endpoints llamados contratos devuelven vínculos cliente/campaña. | Crear contratos independientes y entregas 1:N; conservar referencias de los vínculos existentes. |',
'| A05 | Alta | Campos documentales y financieros están unidos en detalle de trazabilidad y recibos. | Separar documento, obligación y movimiento de dinero; no fabricar pagos/cobros con una URL. |',
'| A06 | Alta | Varias FK actuales usan CASCADE sobre certificados, cliente/campaña, exámenes y detalles. | Revisar política de bajas al añadir documentos financieros; el objetivo propone RESTRICT y protección del historial. |',
'| A07 | Media | Exámenes son generales del proveedor y solo aceptan positivo/negativo. | Añadir muestra, campaña/finca y pendiente; no reinterpretar resultados ni asignar campaña por suposición. |',
'| A08 | Media | MTD actual es un único valor en la participación y no tiene historial/captura. | Añadir medicion_mtd y mantener procedencia de valores anteriores. |',
'| A09 | Decisión | Una campaña activa por fruta en código; el objetivo permite más de una. | Mantener la regla actual hasta decidir; retirarla requiere migración explícita y revisión del servicio. |',
'| A10 | Decisión | Cliente/campaña único en código; el plan permite múltiples requerimientos. | Elegir vínculo único con contratos múltiples, o requerimiento identificable múltiple. No retirar el índice por accidente. |',
'| A11 | Decisión | Certificados de campaña múltiples en código; objetivo/UI de referencia pide uno. | Revisar datos y alcance por norma antes de poner UNIQUE(campania_id). |',
'| A12 | Alta | El objetivo omite restricciones y datos que ya existen: exclusión de chofer, dimensiones, SCTR, auditoría y estado/bucket de archivo. | Incorporarlos al diseño de migración; el plan anterior no sustituye el backend sin regresiones. |',
'| A13 | Media | Longitudes, nulabilidad, escala y enums difieren aun en tablas con mismo nombre. | Ejecutar prevalidaciones; no truncar cadenas, rellenar NULL con datos ficticios ni castear enums a ciegas. |',
'| A14 | Alta | No hay entidades de facturas, cobros, liquidaciones, adelantos ni checklist/cierre completo. | Implementar esos procesos con transacciones y permisos; las reglas del SQL nuevo aún no son parte del backend. |',
'| A15 | Media | El objetivo cambia toda PK a bigint y un nombre genérico. | Decidir si conservar PK actuales es preferible; revisar contratos API y serialización antes de ampliar rango. |',
'| A16 | Alta | entrevista_extencion ya existe; su anio_aplicacion es un año y no la cantidad de aplicaciones del plan. | Reutilizar la entidad y conservar códigos FVV; reconciliar semántica de año, frecuencia y distanciamiento. No crear una tabla de entrevistas duplicada. |',
'| A17 | Decisión | El frontend incorpora campañas manualmente a Calidad y guarda alcances Exportador/Industria en un array local. | Decidir si esa incorporación es un estado propio persistente o una consulta derivada; no duplicar campana ni asumir que el contrato ya representa esta selección. |',
'| A18 | Alta | El almacén de análisis usa nombres de productor/finca y permite leer todos los registros al consultar campaña 1. | Mantener IDs reales al persistir y corregir el filtro antes de integrar; el problema está en el almacén local, no en una FK de la base actual. |','',
'**Evidencias de servicios:** '+link('epe-backend/src/cliente-negocio-campana/services/cliente-negocio-campana.service.ts','async findContratosByCliente','consulta denominada contratos')+'; '+link('epe-backend/src/campana-proveedor/services/campania-proveedor.service.ts','private validateFinca','coherencia finca/proveedor en servicio')+'; '+link('epe-backend/src/transporte/services/chofer-vehiculo-externo.service.ts','private async saveAssignment','asignación transaccional con bloqueo del chofer')+'; '+link('epe-backend/src/campana/services/campana.service.ts','private async validateActiveCampaign','una campaña activa por fruta')+'.','']

for name in [x['table'] for x in CURRENT]:
    title,breadcrumb,current,delta=notes[name]; t=ACT[name]
    out += [f'## {title} ({breadcrumb})','',f'**Tabla actual:** `{name}`. **Fuente:** {source(name)}.','',f'**Lo programado:** {current}','',f'**Diferencia y acción:** {delta}','',
    '**Diccionario comprobado de la entidad actual:**','', '| Columna actual | Tipo en TypeORM | Nulabilidad / clave |','|---|---|---|']
    for col in t['columns']:
        dtype=str(col['type'])
        if col.get('length'):dtype+='('+str(col['length'])+')'
        if col.get('precision') is not None:dtype+='('+str(col['precision'])+','+str(col.get('scale',0))+')'
        if col.get('enum'):dtype+=': '+', '.join(str(e) for e in col['enum'])
        flag='PK autogenerada' if col['primary'] else ('NULL permitido' if col['nullable'] else 'NOT NULL')
        fk=[f"FK a `{f['parent']}` (`{','.join(f['target'])}`); ON DELETE {f['onDelete']}" for f in t['foreignKeys'] if col['name'] in f['columns']]
        out.append(f"| `{col['name']}` | {dtype} | {flag}"+('; '+'; '.join(fk) if fk else '')+' |')
    out+=['']
    constraints=[]
    for idx in t['indexes']:
        if idx['unique']:constraints.append('UNIQUE '+code(', '.join(idx['columns']))+(' WHERE '+code(idx['where']) if idx.get('where') else ''))
    constraints += ['UNIQUE '+code(', '.join(idx['columns'])) for idx in t['uniques']]
    constraints += ['CHECK '+code(c['expression']) for c in t['checks']]
    constraints += ['EXCLUDE '+code(c['expression']) for c in t['exclusions']]
    out+=['**Restricciones observadas:** '+('; '.join(constraints) if constraints else 'sin UNIQUE, CHECK o EXCLUDE adicionales declarados; conserva PK y las FK descritas.')+'.','']

out+=['## Transformación de relaciones (Plan > Proveedores y transporte > Integración)','',
'La comparación separa relaciones actuales de relaciones objetivo; una flecha de los diagramas ER no representa una migración ya realizada.','',
'**Actual: participación de finca como origen único de trazabilidad.**','',
'```mermaid','erDiagram',
'    campana ||..o{ campania_x_proveedores : incluye',
'    proveedor ||..o{ campania_x_proveedores : participa',
'    finca o|..o{ campania_x_proveedores : ubica',
'    campania_x_proveedores ||..o{ trazabilidad_transporte : origina',
'    trazabilidad_transporte ||..o{ chofer_vehiculo_externo : asigna',
'    trazabilidad_transporte ||..o{ detalle_trazabilidad : detalla',
'```','',
'**Objetivo: cabecera de participación, varias fincas y carga multiproveedor.**','',
'```mermaid','erDiagram',
'    campana ||..o{ participacion_proveedor_campana : incluye',
'    proveedor ||..o{ participacion_proveedor_campana : participa',
'    participacion_proveedor_campana ||..o{ campania_x_proveedores : vincula',
'    finca ||..o{ campania_x_proveedores : ubica',
'    cliente_negocio_campana ||..o{ contrato_venta : acuerda',
'    contrato_venta ||..o{ entrega_programada : programa',
'    entrega_programada ||..o| coordinacion_entrega : coordina',
'    coordinacion_entrega ||..o{ origen_entrega : selecciona',
'    campania_x_proveedores ||..o{ origen_entrega : provee_origen',
'    coordinacion_entrega ||..o| carga : ejecuta',
'    carga ||..o{ proveedor_carga : agrupa',
'    participacion_proveedor_campana ||..o{ proveedor_carga : aporta',
'    carga ||..o| recepcion_planta : recibe',
'```','',
'## Cosecha y Control de Calidad actualizado (Administrador > Cosecha y Control de Calidad > Contraste con el backend)','',
'Esta sección contrasta el código local nuevo con el esquema objetivo y conserva la separación respecto del recorrido previo del prototipo publicado. No se vuelve a presentar como implementación local completa cada vista que existía en aquel prototipo.','',
'| Dato o acción del frontend actual | Estado observado en código | Diferencia frente al plan y acción de diseño |','|---|---|---|',
'| Listado e incorporación de campañas | QualityPage consume quality.store.ts; el modal lee GET /campanas y agrega una fila en memoria. | campana ya existe; falta decidir cómo conservar la incorporación al módulo. No crear otro padrón de campañas. |',
'| Alcances Exportador/Industria | QualityCampaign.scope es un array; puede incorporar la misma campaña a ambos. | El plan usa canal de contrato/operación; eso no prueba que represente una incorporación manual independiente al módulo. Resolver antes de crear asociación nueva o derivarlo. |',
'| Identidad de la campaña incorporada | quality.store.ts identifica coincidencia por campaniaId o por nombre. | El nombre no debe sustituir al ID al persistir, porque dos campañas distintas podrían compartirlo. |',
'| Muestreos y resultados | QualityAnalysisRecord contiene campaña, productorNombre, fincaNombre, fecha, tipo, resultado/unidad, estado y observaciones. | analisis_calidad y medicion_mtd siguen siendo propuestas. Resolver finca y productor mediante IDs; no guardar solo el nombre como relación. |',
'| MTD y trampa | mtd numérico y mtdTrampa opcional en el modelo local. | El plan conserva valor/fecha/límite/evidencia en medicion_mtd, pero no representa explícitamente mtdTrampa. Definir si es referencia textual o entidad de trampa; no inventar catálogo. |',
'| Archivo de análisis | File en memoria y documentoNombre opcional. | Para persistir hace falta el objeto confirmado en archivo y la FK; un File o su nombre no es un identificador de almacenamiento. |',
'| Análisis/Carga/Guías de la tabla | Los handlers de QualityPage muestran avisos de próximamente disponible. | No contabilizar esas acciones como CRUD o tablas de backend ya implementados. |',
'| Aislamiento por campaña | useQualityAnalysis y getQualityAnalysis filtran con r.campaniaId === campaniaId || campaniaId === 1. | Para campaniaId=1 el filtro acepta todas las campañas. Ejemplo estático: registros de campañas 1 y 2 se incluyen ambos al consultar 1. Resolver antes de usarlo con datos reales. |','',
'**Evidencia:** '+link('epe-web/src/modules/quality/quality.store.ts','export function addQualityCampaign','incorporación y deduplicación local')+', '+link('epe-web/src/modules/quality/qualityAnalysis.store.ts','export function getQualityAnalysis','almacén/filtro de análisis')+', '+link('epe-web/src/modules/quality/qualityAnalysis.utils.ts','export interface QualityAnalysisRecord','contrato local de análisis')+', '+link('epe-web/src/modules/quality/pages/QualityPage.tsx','const handleSelectAction','acciones todavía informativas')+' y '+link('epe-web/src/modules/quality/components/QualityAddCampaignModal.tsx','void getCampanas','lectura del catálogo de campañas')+'.','',
'**Alcance de la observación:** es una inspección estática. No se abrió la app local ni se enviaron datos. Los almacenes declaran TODO(api) y sus demos se habilitan solo en desarrollo; no se atribuye al backend una fuga de datos que no está persistiendo. Los estados de conexión se registran únicamente en '+link('epe-web/docs/reporte-conexion-vistas.md',None,'reporte de conexión de vistas')+', conservando su historial.','',
'## Módulos aún no persistidos (Plan > Cobertura funcional > Pendientes)','',
'La ausencia indicada es de entidades/migraciones de este backend auditado. No equivale a afirmar que una pantalla del prototipo no exista ni que los datos no puedan estar en un almacén de frontend. La auditoría no conecta ni modifica vistas.','',
'| Área | Capacidad existente | Persistencia adicional requerida por el plan |','|---|---|---|',
'| Acceso administrativo/chofer | No hay entidad de usuario/rol/sesión en el registro auditado. | persona, usuario, rol, sesion_usuario y autorización real. |',
'| Proveedores por campaña | Vínculo a proveedor/finca, perfil global y entrevista_extencion persistida con validación de productor/finca. | Cabecera de participación, variedades e historia MTD; ampliar semántica/campos de la entrevista existente. |',
'| Comercial | Cliente y vínculo único con campaña. | contrato_venta, destinos, variedades requeridas, entrega_programada y distribución por variedad. |',
'| Certificaciones | Certificado de campaña con costo/recibo y certificado propio con archivo. | Cobertura por productor, norma/organismo/moneda, ampliaciones y pagos parciales. |',
'| Transporte | Empresas, choferes, vehículos, trazabilidad, asignaciones y detalle. | Solicitudes/invitaciones/cotizaciones, acuerdo, coordinación multiorigen y flete separado de pagos. |',
'| Calidad y carga | MTD y kg comprados/planta en una trazabilidad. | Cosecha/operación, muestreos, detalle real por proveedor/variedad, bultos y costos de carga. |',
'| Logística y despacho | Estado resumido de trazabilidad. | Eventos ordenados, guías estructuradas, recepción documentada, descarte, checklist y cierre. |',
'| Facturación/cobros | No hay factura/cobro persistidos en entidades. | factura_venta, cobro_venta y reglas de saldo/moneda. |',
'| Liquidación de compra | Flete/costos en detalle de trazabilidad; no documentos de liquidación ni pagos. | liquidacion_proveedor/transporte, pago_proveedor/transporte, adelantos, aplicaciones y control anual por persona. |','',
'## Reglas que deben conservarse (Plan > Compatibilidad > Evitar regresiones)','',
'| Regla o dato actual | Estado en el SQL objetivo anterior, mantenido salvo nombres | Recomendación para implementación |','|---|---|---|',
'| Auditoría created_at/updated_at de todas las entidades | No está de forma transversal. | Heredar AuditableEntity en nuevas entidades; preservar fechas actuales. |',
'| EXCLUDE de solapamiento de chofer | No está en coordinacion_entrega. | Mantener restricción equivalente; decidir fechas inclusivas frente a horarios. El control del servicio por sí solo no sustituye exclusión concurrente. |',
'| Bloqueo transaccional del chofer y viaje previo terminado | No queda resuelto por el estado de carga solamente. | Conservar bloqueo; definir nuevo final CIERRE frente al actual llegada. |',
'| Una campaña activa por fruta | No está en el objetivo. | Decidir expresamente si se conserva o elimina; modificar índice y servicio conjuntamente. |',
'| Cliente/campaña único | No está en el objetivo. | Conservar vínculo único con contratos múltiples, o definir identidad de requerimiento múltiple. |',
'| Correo de cliente y transportista únicos | El objetivo no conserva ambas unicidades. | Revisar la regla, no retirarla accidentalmente. |',
'| Dimensiones vehiculares y pesos originales | Ancho/altura/profundidad y semántica de peso neto no se conservan. | Mantener los datos originales y agregar capacidad separada. |',
'| SCTR en detalle_trazabilidad | No tiene destino explícito en las 64 tablas. | Incorporar respaldo o dato SCTR al servicio/viaje antes de retirar la tabla legacy. |',
'| Bucket y estados del archivo | Faltan en el objetivo simplificado. | Extender el servicio S3 actual y mantener estados, confirmación y política de borrado. |',
'| Registro sin finca permitido en código | El detalle objetivo exige finca. | Cabecera sin detalles hasta completar entrevista; no endurecer el detalle sin separar antes la cabecera. |',
'| Código de entrevista FVV único y generación con advisory lock | El objetivo usa codigo_fyv sin unicidad/generación equivalente. | Conservar unicidad y generación atómica, preservando códigos históricos. |',
'| Triggers de productor/finca y protección de asignación con entrevistas | El objetivo no tiene todas esas reglas de entrevista. | Preservar coherencia de finca y rol de productor al reubicar las FK. |','',
'**Estas observaciones no se aplicaron como cambios de esquema en esta tarea.** El SQL objetivo se actualizó en nomenclatura, no se reescribió para resolver decisiones nuevas de producto. Los puntos de esta tabla son condiciones de aceptación para la migración futura.','',
'## Migraciones y datos históricos (Backend > Migraciones > Auditoría)','',
'| Orden | Migración | Alcance que afecta la comparación |','|---:|---|---|']
migrationnotes=[
'Crea el núcleo de campañas, proveedor, cliente, certificados, catálogos y exámenes.',
'Crea seis tablas de transporte, costos y asignaciones; agrega btree_gist y exclusión por chofer.',
'Agrega estado_examen_sanidad_agraria al proveedor.',
'Crea archivo y migra certificado_proveedor desde documento_url a documento_archivo_id.',
'Mueve agronomía desde campaña/proveedor al proveedor usando DISTINCT ON por proveedor, tomando el registro más recientemente actualizado.',
'Crea finca a partir de ubicaciones de campaña/proveedor y agrega finca_id; cambia unicidades a campaña/finca y vínculo sin finca.',
'Elimina campos legacy agronómicos y de ubicación de campaña/proveedor.',
'Elimina la exigencia de finca para productor; down revisa previamente productores sin finca y falla si existen.',
'Agrega estado sin validar/validado al vínculo de campaña y crea entrevista_extencion, sus índices y triggers de productor/finca y protección de la asignación.']
migrations=json.loads((R/'.validation/migraciones_actuales.json').read_text(encoding='utf8'))
for i,(mig,note) in enumerate(zip(migrations,migrationnotes),1):out.append(f'| {i} | {link(mig["file"],"public async up",mig["name"])} | {note} |')
out+=['',
'**Riesgos de datos al migrar:** la migración que toma el último perfil agronómico por proveedor no conserva por sí sola todas las diferencias de campañas anteriores. El código permite identificar ese riesgo, pero no demuestra que se hayan perdido datos de una instancia real. Revisar respaldos antes de reconstruir un historial. La creación de finca genera una finca por fila CXP que tenía ubicación completa; filas históricas de distintas campañas podrían corresponder al mismo lugar físico: no deduplicarlas sin validar identidad de finca. El paso a archivo elimina documento_url del certificado propio sin un backfill de archivos en ese script; revisar certificados cuyo documento_archivo_id siga nulo y rescatar URLs de respaldos si fuera necesario.','',
'**Pruebas realizadas en la reproducción temporal:**','',
'| Caso | Comportamiento observado |','|---|---|']
for test in RUN['tests']:out.append(f"| {test['prueba']} | {test['resultado']} |")
out+=['',
'El caso de finca ajena fue aceptado por SQL directo porque las FK actuales comprueban cada padre por separado. El servicio CampaniaProveedorService sí valida pertenencia: no se presenta como un fallo de ese servicio. La FK compuesta del objetivo traslada esa coherencia a la base. Los casos de duplicidad de documento y borrado CASCADE se ejecutaron solamente sobre filas sintéticas de la base temporal.','',
'En la pasada anterior, el SQL objetivo con nombres actualizados se instaló y pasó **29 pruebas funcionales locales**. Esta reauditoría mantiene esa evidencia porque el esquema no cambió; no presenta las pruebas como recién ejecutadas. La comprobación de renombrado no convierte las estructuras actuales en las nuevas ni prueba una migración real. No se ejecutaron migraciones sobre la base del usuario ni una prueba de carga/concurrencia contra PostgreSQL desplegado.','',
'## Secuencia de implementación recomendada (Plan > Migración > Etapas)','',
'1. **Fijar la línea base.** En una revisión posterior contra la instancia autorizada, comprobar typeorm_migrations y catálogo; respaldar y medir filas, longitudes, duplicados y documentos nulos. Conservar el diagrama actual como línea base.','',
'2. **Resolver las decisiones de compatibilidad.** Una campaña activa por fruta, vínculo único cliente/campaña, certificados múltiples, significado de cantidades por finca, peso neto/capacidad y alcance de asignación histórica. Los nombres actualizados no resuelven esas decisiones.','',
'3. **Ampliar sin retirar.** Agregar persona y sus equivalencias, mantener PK antiguas o mapearlas, crear cabecera de participación y ampliar/reutilizar entrevista_extencion. Agregar campos y tablas con transición nullable cuando haga falta; endurecer restricciones después del backfill validado.','',
'4. **Separar contrato y programación.** Reutilizar cliente_negocio_campana, crear contrato_venta y entregas, migrar documentos/condiciones con procedencia. Adaptar DTO y servicios sin romper clientes actuales.','',
'5. **Separar viaje y carga multiproveedor.** Reconciliar trazabilidad_transporte con entregas reales; conservar chofer_vehiculo_externo y detalle_trazabilidad hasta comprobar la nueva cobertura. Mantener exclusiones, dimensiones, SCTR y costos de origen.','',
'6. **Completar calidad, documentos y recepción.** Registrar mediciones y archivos reales; no reconstruir reportes de recepción a partir de una factura ni crear guías estructuradas desde nombres de PDF.','',
'7. **Agregar obligaciones y dinero.** Implementar liquidaciones/facturas separadas de pagos/cobros, adelantos y aplicaciones; conservar referencia a datos antiguos sin fabricar desembolsos.','',
'8. **Activar cierre y retirar legacy por último.** Reconciliar totales e IDs, probar estados, saldos y permisos; retirar columnas/tablas antiguas solo después de validar equivalencias y consumidores. Cada cambio físico requiere una migración TypeORM y actualizar docs/er-diagram.md en el mismo cambio, según AGENTS.md.','',
'**Alcance de esta entrega:** auditoría y alineación documental. No se implementaron las etapas anteriores ni se cambiaron reglas o tablas de producción. El documento debe guiar las migraciones siguientes, no sustituirlas.','']
dest.write_text('\n'.join(out),encoding='utf8')
print(f'Auditoría: {dest}; {len(CURRENT)} tablas actuales, 64 correspondencias, 18 hallazgos; evidencia previa de {len(RUN["tests"])} pruebas de esquema actual.')
