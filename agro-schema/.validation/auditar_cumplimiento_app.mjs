import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

// Evidencia estática de incompatibilidades concretas; no ejecuta PostgreSQL.
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
  evidence.push({ id, archivo: file, tabla: table, escenario: scenario, resultado: 'Incompatibilidad corroborada por lectura estática' });
}
inspect('CF01', 'store.tsx', /dni: string/, 'proveedor', /"nmr_documento" integer NOT NULL/, 'Un documento alfanumérico o con cero inicial no se conserva como integer.');
inspect('CF02', 'store.tsx', /haCultivo: '3\.5'/, 'finca', /"ha_cultivo" integer NOT NULL/, 'El demo usa 3.5 ha; el esquema exige hectáreas enteras.');
inspect('CF03', 'store.tsx', /resultado\?: 'Negativo' \| 'Positivo'/, 'examen_proveedor', /"resultado" "examen_proveedor_resultado_enum" NOT NULL/, 'Guardar examen pendiente sin resultado queda bloqueado.');
inspect('CF04', 'store.tsx', /paymentAgreement\?:/, 'acuerdo_transporte', /"monto_acordado" numeric\(14,2\) NOT NULL/, 'El vínculo inicial del transportista no puede representarse únicamente como acuerdo completo.');
inspect('CF05', 'business-integrity.ts', /row\.tipo === 'Privado' \? 'documentoIdentidad' : 'ruc'/, 'empresa_transporte_externo', /"ruc" varchar\(11\) NOT NULL/, 'El transportista privado identificado sin RUC no tiene un alta equivalente directa.');
inspect('CF06', 'finance-model.ts', /item\.kilos \* item\.price - item\.discount \+ item\.charges/, 'factura_venta', /CHECK \(importe_venta = round\(kilos_facturados \* precio_kg_aplicado, 2\)\)/, '100 kg × 2 menos descuento 10 da 190; el CHECK obliga 200.');
inspect('CF07', 'store.tsx', /recognizedQuantity\?: number/, 'recepcion_planta', /"peso_planta_kg" numeric\(14,3\)/, 'Existe peso global en SQL; no hay un desglose reconocido por proveedor en sus tablas declaradas.');
inspect('CF08', 'store.tsx', /advances: \{ id: string; providerId\?: string; fincaId\?: string;/, 'cosecha', /"kilos_cosechados" numeric\(14,3\)/, 'La cabecera conserva el total; no conserva las filas de avance de la aplicación.');
inspect('CF09', 'store.tsx', /unloading: \{ start: string; end: string;/, 'recepcion_planta', /"descarga_at" timestamptz/, 'La aplicación registra inicio y fin de descarga; SQL solo tiene una fecha de descarga.');
inspect('CF10', 'finance-model.ts', /due: string/, 'liquidacion_proveedor', /"importe_compra" numeric\(14,2\) NOT NULL/, 'La liquidación no guarda vencimiento, kilos y precio aplicado para reproducir el documento.');

// Ausencias revisadas en todo el SQL, no solo en una tabla cabecera.
const columns = [...sql.matchAll(/^  "([^"]+)" /gm)].map(m => m[1]);
const semanticReview = {
  avance_cosecha: ![...tables.keys()].some(n => /avance.*cosecha|cosecha.*avance/.test(n)),
  kilos_reconocidos: !columns.some(n => /kilos_reconocidos|peso_reconocido|cantidad_reconocida/.test(n)),
  descuento_factura: !/"(?:descuento|descuentos|cargos|descuento_venta|cargos_venta)"/.test(tables.get('factura_venta')),
};
if (Object.values(semanticReview).some(v => !v)) throw Error('Cambió el esquema: revisar ausencias funcionales.');
const hash = text => createHash('sha256').update(text).digest('hex');
const result = { metodo: 'Lectura estática de campos, tipos y restricciones; sin ejecución de SQL ni prueba de UI', schema_sha256: hash(sql), fuentes: Object.fromEntries([...sourceFiles].map(([file, data]) => [file, hash(data)])), incompatibilidades: evidence, ausencias_por_nombres_y_revision_manual: semanticReview, nota: 'Los nombres ausentes no prueban por sí solos falta de representación; el reporte explica la revisión semántica y las alternativas mínimas.' };
writeFileSync(new URL('./resultado_cumplimiento_app.json', import.meta.url), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ evidencias_corroboradas: evidence.length, comprobaciones_ausencia: Object.keys(semanticReview).length, ejecucion_sql: false }));
