import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

// Inspección estática: no ejecuta SQL ni se conecta a una base.
const sql = readFileSync(new URL('../03_schema_total.sql', import.meta.url), 'utf8');
const tables = new Map([...sql.matchAll(/CREATE TABLE "([^"]+)" \(([\s\S]*?)\n\);/g)].map(([, name, body]) => [name, new Set([...body.matchAll(/^  "([^"]+)" /gm)].map(m => m[1]))]));
const fks = [...sql.matchAll(/ALTER TABLE "([^"]+)" ADD CONSTRAINT "([^"]+)" FOREIGN KEY \(([^)]+)\) REFERENCES "([^"]+)" \(([^)]+)\)/g)];
const errors = [];
for (const [, child, name, childCols, parent, parentCols] of fks) {
  const children = [...childCols.matchAll(/"([^"]+)"/g)].map(m => m[1]);
  const parents = [...parentCols.matchAll(/"([^"]+)"/g)].map(m => m[1]);
  if (children.length !== parents.length) errors.push(`${name}: aridad distinta`);
  for (const [table, cols] of [[child, children], [parent, parents]]) {
    for (const col of cols) if (!tables.get(table)?.has(col)) errors.push(`${name}: falta ${table}.${col}`);
  }
}
const views = [...sql.matchAll(/CREATE VIEW (\w+) AS/g)].map(m => m[1]);
if (tables.size !== 60 || fks.length !== 124 || views.length !== 6) errors.push('Inventario diferente del documentado');
if (tables.has('destino_cliente_negocio') || /"destino_id"/.test(sql)) errors.push('D08: catálogo o FK de destino reintroducidos');
if (!/"destino" text NOT NULL/.test(sql)) errors.push('D08: falta destino textual obligatorio');
const result = {
  metodo: 'Inspección estática de declaraciones SQL; no valida ejecución, restricciones ni transacciones',
  schema_sha256: createHash('sha256').update(sql).digest('hex'),
  tablas: tables.size, claves_foraneas: fks.length, vistas: views,
  errores_referencias: errors,
  columnas_financieras: Object.fromEntries(['acuerdo_transporte', 'liquidacion_proveedor', 'liquidacion_transporte', 'factura_venta'].map(t => [t, [...tables.get(t)]])),
};
writeFileSync(new URL('./resultado_inventario_negocio.json', import.meta.url), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({ tablas: tables.size, claves_foraneas: fks.length, vistas: views.length, errores: errors }));
if (errors.length) process.exitCode = 1;
