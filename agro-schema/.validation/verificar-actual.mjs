import {PGlite} from '@electric-sql/pglite';
import {btree_gist} from '@electric-sql/pglite/contrib/btree_gist';
import {readFileSync,writeFileSync} from 'node:fs';
const db=new PGlite({extensions:{btree_gist}});
const migrations=JSON.parse(readFileSync(new URL('./migraciones_actuales.json',import.meta.url),'utf8'));
const metadata=JSON.parse(readFileSync(new URL('./modelo_actual.json',import.meta.url),'utf8'));
for(const migration of migrations){
 await db.exec('BEGIN');for(const sql of migration.queries)await db.exec(sql);await db.exec('COMMIT');
}
const columns=(await db.query("SELECT table_name,column_name,data_type,udt_name,is_nullable,column_default,numeric_precision,numeric_scale,character_maximum_length FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")).rows;
const constraints=(await db.query("SELECT c.relname AS table_name,k.conname,k.contype,pg_get_constraintdef(k.oid) AS definition FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY c.relname,k.conname")).rows;
const indexes=(await db.query("SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' ORDER BY tablename,indexname")).rows;
const mismatches=[];
for(const t of metadata){
 const current=columns.filter(c=>c.table_name===t.table);
 if(current.length!==t.columns.length)mismatches.push({table:t.table,issue:'Cantidad columnas',entity:t.columns.length,migration:current.length});
 for(const c of t.columns){const actual=current.find(x=>x.column_name===c.name);if(!actual)mismatches.push({table:t.table,missing:c.name});else if((actual.is_nullable==='YES')!==c.nullable)mismatches.push({table:t.table,column:c.name,issue:'nullable distinto'});}
}
const tests=[];
async function reject(name,sql,pattern){await db.exec('BEGIN');try{await db.exec(sql);await db.exec('ROLLBACK');throw Error('Aceptado inesperadamente: '+name)}catch(e){await db.exec('ROLLBACK');if(String(e).includes('Aceptado inesperadamente'))throw e;if(pattern&&!pattern.test(e.message))throw e;tests.push({prueba:name,resultado:'rechazado',mensaje:e.message})}}
await db.exec(`INSERT INTO fruta(fruta_id,name) VALUES(1,'Mango'),(2,'Palta');
 INSERT INTO campana(campania_id,nombre,fecha_inicio,fecha_fin,estado,requerimiento_comercial,fruta_id) VALUES(1,'Mango','2026-01-01','2026-12-31','en proceso',100,1),(2,'Palta','2026-01-01','2026-12-31','en proceso',100,2);
 INSERT INTO proveedor(proveedor_id,nombres,apellido,tipo_documento,nmr_documento,identidad_doc_url,zona,telefono,email,codigo_lugar_produccion) VALUES(1,'Uno','Prueba','DNI',123,'test.pdf','Piura',123,'p@test.com',123),(2,'Dos','Prueba','DNI',123,'test.pdf','Piura',123,'p@test.com',123);
 INSERT INTO finca(finca_id,proveedor_id,nombre_finca,departamento,provincia,distrito,latitud,longitud,ha_total_finca,ha_cultivo) VALUES(1,1,'Uno','Piura','Piura','Piura',-5,-80,10,8),(2,1,'Dos','Piura','Piura','Piura',-5,-80,10,8),(3,2,'Tres','Piura','Piura','Piura',-5,-80,10,8);
 INSERT INTO campania_x_proveedores(cxp_id,campania_id,proveedor_id,finca_id,cantidad_proveedor,mtd_ceratitis,tipo_proveedor) VALUES(1,1,1,1,100,0.2,'productor'),(2,1,1,2,100,0.2,'productor'),(3,1,1,NULL,100,0.2,'productor');
 INSERT INTO cliente_negocio(cliente_negocio_id,nombre_empresa,nombre_contacto,telefono,ruc,correo_corporativo,ubicacion,tipo_cliente) VALUES(1,'Cliente','Contacto','123','20100000001','c@test.com','Lima','industria');
 INSERT INTO cliente_negocio_campana(cliente_negocio_id,campania_id,documento_url,fecha_registro,ficha_tecnica_url,kilos_acordados) VALUES(1,1,'c.pdf','2026-01-01','f.pdf',100);
 INSERT INTO empresa_transporte_externo(id_empresa_transporte_externo,nombre_completo,ruc,correo,numero) VALUES(1,'Empresa','20100000002','t@test.com','123');
 INSERT INTO vehiculo_externo(id_vehiculo_externo,id_empresa_transporte_externo,placa,volumen,ancho,altura,profundidad,peso_neto,peso_bruto) VALUES(1,1,'AAA-001',10,2,2,2,100,200);
 INSERT INTO chofer_transporte_externo(id_chofer_transporte_externo,id_empresa_transporte_externo,nombre,telefono,correo) VALUES(1,1,'Conductor','123','ch@test.com');
 INSERT INTO trazabilidad_transporte(id_trazabilidad_transporte,cxp_id,contrato_url,kg_comprados,kg_planta,estado) VALUES(1,1,'c.pdf',100,95,'planificado');
 INSERT INTO chofer_vehiculo_externo(id_vehiculo_externo,id_chofer_transporte_externo,id_trazabilidad_transporte,fecha_asignacion_inicio,fecha_asignacion_final) VALUES(1,1,1,'2026-02-01','2026-02-02');`);
for(const table of metadata){const pk=table.columns.find(c=>c.primary);await db.query(`SELECT setval(pg_get_serial_sequence($1,$2),coalesce((SELECT max("${pk.name}") FROM "${table.table}"),0)+1,false)`,[table.table,pk.name]);}
tests.push({prueba:'Varias fincas y vínculo sin finca del mismo proveedor/campaña',resultado:'aceptado'});
tests.push({prueba:'Documento y email repetidos en proveedores por SQL directo',resultado:'aceptado; sin unicidad en BD'});
await reject('Segunda campaña activa de la misma fruta',"INSERT INTO campana(nombre,fecha_inicio,fecha_fin,estado,requerimiento_comercial,fruta_id) VALUES('Duplicada','2026-01-01','2026-12-31','en proceso',1,1)",/UQ_campana_fruta_activa/);
await reject('Segunda vinculación del cliente a la misma campaña',"INSERT INTO cliente_negocio_campana(cliente_negocio_id,campania_id,documento_url,fecha_registro,ficha_tecnica_url,kilos_acordados) VALUES(1,1,'c.pdf','2026-01-01','f.pdf',100)",/UQ_cliente_negocio_campania/);
await reject('Finca repetida en campaña',"INSERT INTO campania_x_proveedores(campania_id,proveedor_id,finca_id,cantidad_proveedor,mtd_ceratitis,tipo_proveedor) VALUES(1,1,1,100,0.2,'productor')",/UQ_campania_finca/);
await reject('Segundo vínculo sin finca',"INSERT INTO campania_x_proveedores(campania_id,proveedor_id,finca_id,cantidad_proveedor,mtd_ceratitis,tipo_proveedor) VALUES(1,1,NULL,100,0.2,'productor')",/UQ_campania_proveedor_sin_finca/);
await reject('Solapamiento de chofer en fecha inclusiva',"INSERT INTO chofer_vehiculo_externo(id_vehiculo_externo,id_chofer_transporte_externo,id_trazabilidad_transporte,fecha_asignacion_inicio,fecha_asignacion_final) VALUES(1,1,1,'2026-02-02','2026-02-03')",/EX_chofer_sin_rangos_superpuestos/);
await reject('Examen con resultado pendiente',"INSERT INTO examen_proveedor(proveedor_id,fecha,tipo_examen,resultado,origen,observacion,documento_url) VALUES(1,'2026-02-01','Muestra','pendiente','Finca','test','e.pdf')",/invalid input value for enum/);
await db.exec('BEGIN');
await db.exec("INSERT INTO campania_x_proveedores(campania_id,proveedor_id,finca_id,cantidad_proveedor,mtd_ceratitis,tipo_proveedor) VALUES(1,1,3,100,0.2,'productor')");
await db.exec('ROLLBACK');tests.push({prueba:'Finca de otro proveedor por SQL directo',resultado:'aceptado por BD; el servicio sí lo rechaza'});
await db.exec('BEGIN');
await db.exec("INSERT INTO certificado_campana(nombre,document_url,costo,recibo_url,fecha_vencimiento,campania_id,estado) VALUES('Certificado','c.pdf',100,'r.pdf','2026-12-31',2,'vigente'); DELETE FROM campana WHERE campania_id=2");
const left=(await db.query('SELECT count(*)::int AS n FROM certificado_campana WHERE campania_id=2')).rows[0].n;
if(left!==0)throw Error('CASCADE no observado');
await db.exec('ROLLBACK');tests.push({prueba:'Eliminar campaña sin otros bloqueos elimina certificado por CASCADE',resultado:'confirmado en base temporal'});
await db.exec(`INSERT INTO campania_x_proveedores(cxp_id,campania_id,proveedor_id,finca_id,cantidad_proveedor,mtd_ceratitis,tipo_proveedor) VALUES(1000,1,2,3,100,0.2,'acopio');
INSERT INTO entrevista_extencion(cam_x_prov_id,finca_id,densidad,distanciamiento,frecuencia,nombre_aplicacion,anio_aplicacion,codigo) VALUES(1,1,400,5,4,'Programa',2026,'FVV-TEST-1')`);
tests.push({prueba:'Entrevista de productor en su finca con código FVV',resultado:'aceptado'});
await reject('Entrevista de acopiador',"INSERT INTO entrevista_extencion(cam_x_prov_id,finca_id,densidad,distanciamiento,frecuencia,nombre_aplicacion,anio_aplicacion,codigo) VALUES(1000,3,400,5,4,'Programa',2026,'FVV-TEST-2')",/Solo los productores/);
await reject('Entrevista con finca de otro proveedor',"INSERT INTO entrevista_extencion(cam_x_prov_id,finca_id,densidad,distanciamiento,frecuencia,nombre_aplicacion,anio_aplicacion,codigo) VALUES(3,3,400,5,4,'Programa',2026,'FVV-TEST-2')",/no pertenece/);
await reject('Entrevista con finca distinta de la asignada',"INSERT INTO entrevista_extencion(cam_x_prov_id,finca_id,densidad,distanciamiento,frecuencia,nombre_aplicacion,anio_aplicacion,codigo) VALUES(1,2,400,5,4,'Programa',2026,'FVV-TEST-2')",/no coincide/);
await reject('Código FVV duplicado',"INSERT INTO entrevista_extencion(cam_x_prov_id,finca_id,densidad,distanciamiento,frecuencia,nombre_aplicacion,anio_aplicacion,codigo) VALUES(1,1,400,5,4,'Programa',2026,'FVV-TEST-1')",/UQ_entrevista_extencion_codigo/);
await reject('Cambiar a acopio una asignación con entrevistas',"UPDATE campania_x_proveedores SET tipo_proveedor='acopio' WHERE cxp_id=1",/permanecer como productor/);
writeFileSync(new URL('./resultado_actual.json',import.meta.url),JSON.stringify({motor:'PGlite PostgreSQL WASM con btree_gist',migraciones:migrations.map(m=>m.name),tables:[...new Set(columns.map(c=>c.table_name))],columns,constraints,indexes,mismatches,tests},null,2));
console.log(JSON.stringify({migraciones:migrations.length,tablas:metadata.length,columnas:columns.length,diferenciasEntidadMigracion:mismatches,pruebas:tests.length}));
await db.close();
