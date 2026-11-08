import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

// Contraste estático posterior a la corrección; no sustituye verificar_revision.mjs.
const schemaUrl = new URL('../03_schema_total.sql', import.meta.url);
const protoRoot = new URL('../../prototipo/Campaign%20Management%20System/src/', import.meta.url);
const sql = readFileSync(schemaUrl, 'utf8');
const tables = new Map([...sql.matchAll(/CREATE TABLE "([^"]+)" \(([\s\S]*?)\n\);/g)].map(([, name, body]) => [name, body]));
const evidence = [];
const sourceFiles = new Map();
function source(file) {
  if (!sourceFiles.has(file)) sourceFiles.set(file, readFileSync(new URL(file, protoRoot), 'utf8'));
  return sourceFiles.get(file);
}
function inspect(id, file, sourcePattern, table, sqlPattern, scenario) {
  const sourceMatch = sourcePattern.test(source(file));
  const schemaMatch = sqlPattern.test(tables.get(table) || '');
  if (!sourceMatch || !schemaMatch) throw Error(`Revisar evidencia de ${id}: source=${sourceMatch}, schema=${schemaMatch}`);
  evidence.push({ id, archivo: file, tabla: table, escenario: scenario, resultado: 'Ajuste de persistencia presente; comprobar comportamiento con verificar_revision.mjs' });
}
inspect('CF01', 'store.tsx', /dni: string/, 'proveedor', /"nmr_documento" varchar\(30\) NOT NULL/, 'Un documento alfanumérico o con cero inicial no se conserva como integer.');
inspect('CF02', 'store.tsx', /haCultivo: '3\.5'/, 'finca', /"ha_cultivo" numeric\(12,3\) NOT NULL/, 'El demo usa 3.5 ha; el esquema exige hectáreas enteras.');
inspect('CF03', 'store.tsx', /resultado\?: 'Negativo' \| 'Positivo'/, 'examen_proveedor', /"resultado" "examen_proveedor_resultado_enum",/, 'Guardar examen pendiente sin resultado queda bloqueado.');
inspect('CF04', 'store.tsx', /paymentAgreement\?:/, 'acuerdo_transporte', /"monto_acordado" numeric\(14,2\),/, 'El vínculo inicial del transportista no puede representarse únicamente como acuerdo completo.');
inspect('CF05', 'business-integrity.ts', /row\.tipo === 'Privado' \? 'documentoIdentidad' : 'ruc'/, 'empresa_transporte_externo', /"ruc" varchar\(11\),/, 'El transportista privado identificado sin RUC no tiene un alta equivalente directa.');
inspect('CF06', 'finance-model.ts', /item\.kilos \* item\.price - item\.discount \+ item\.charges/, 'factura_venta', /CHECK \(importe_venta = round\(kilos_facturados \* precio_kg_aplicado - descuento \+ cargos, 2\)\)/, '100 kg × 2 menos descuento 10 da 190; el CHECK obliga 200.');
inspect('CF07', 'store.tsx', /recognizedQuantity\?: number/, 'recepcion_planta', /"compras" jsonb NOT NULL/, 'Existe peso global en SQL; no hay un desglose reconocido por proveedor en sus tablas declaradas.');
inspect('CF08', 'store.tsx', /advances: \{ id: string; providerId\?: string; fincaId\?: string;/, 'cosecha', /"avances" jsonb NOT NULL/, 'La cabecera conserva el total; no conserva las filas de avance de la aplicación.');
inspect('CF09', 'store.tsx', /unloading: \{ start: string; end: string;/, 'recepcion_planta', /"descarga_inicio_at" timestamptz/, 'La aplicación registra inicio y fin de descarga; SQL solo tiene una fecha de descarga.');
inspect('CF10', 'finance-model.ts', /due: string/, 'liquidacion_proveedor', /"kilos_reconocidos" numeric\(14,3\) NOT NULL/, 'La liquidación no guarda vencimiento, kilos y precio aplicado para reproducir el documento.');

// Resultado actual: los escenarios del campo escenario conservan la motivación histórica.
const hash = text => createHash('sha256').update(text).digest('hex');
const result={metodo:'Contraste estático posterior a correcciones; pruebas de ejecución en resultado_revision.json',schema_sha256:hash(sql),fuentes:Object.fromEntries([...sourceFiles].map(([file,data])=>[file,hash(data)])),ajustes:evidence};
writeFileSync(new URL('./resultado_cumplimiento_app.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({ajustes_estaticos:evidence.length}));
