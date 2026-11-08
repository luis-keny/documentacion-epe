import {readFileSync,writeFileSync,mkdirSync,readdirSync} from 'node:fs';
import {createRequire} from 'node:module';
import {resolve,relative,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const backend=resolve(root,'epe-backend');
const req=createRequire(resolve(backend,'package.json'));
const ts=req('typescript');
await import(pathToFileURL(req.resolve('reflect-metadata')).href);
const typeormURL=pathToFileURL(req.resolve('typeorm').replace(/index\.js$/,'index.mjs')).href;
const {DataSource}=await import(typeormURL);
const output=resolve(dirname(fileURLToPath(import.meta.url)),'codigo-actual');
mkdirSync(output,{recursive:true});writeFileSync(resolve(output,'package.json'),' {"type":"module"} ');
function walk(dir){return readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(resolve(dir,x.name)):[resolve(dir,x.name)])}
const source=walk(resolve(backend,'src')).filter(p=>p.endsWith('.ts')&&!p.endsWith('.spec.ts')&&(/[/\\]entities[/\\]/.test(p)||p.endsWith('column.transformers.ts')||/[/\\]migrations[/\\]/.test(p)));
const entities=[], migrations=[], files={};
for(const file of source){
 const text=readFileSync(file,'utf8');
 const target=resolve(output,relative(resolve(backend,'src'),file).replace(/\.ts$/,'.js'));
 mkdirSync(dirname(target),{recursive:true});
 const js=ts.transpileModule(text,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022,experimentalDecorators:true,emitDecoratorMetadata:true}}).outputText.replaceAll("from 'typeorm'",`from '${typeormURL}'`).replaceAll('from "typeorm"',`from '${typeormURL}'`);
 writeFileSync(target,js);
 const table=text.match(/@Entity\(\{ name: '([^']+)'/);
 if(table){files[table[1]]=relative(root,file).replaceAll('\\','/');entities.push(target)}
 if(/[/\\]migrations[/\\]/.test(file))migrations.push({source:file,compiled:target});
}
for(const file of entities)await import(pathToFileURL(file).href);
const classes=(await import(typeormURL)).getMetadataArgsStorage().tables.map(t=>t.target);
// Solo construye metadatos: no lee .env, no inicializa conexiones ni ejecuta DDL.
const ds=new DataSource({type:'postgres',entities:classes,synchronize:false});
await ds.buildMetadatas();
const result=ds.entityMetadatas.map(t=>({
 table:t.tableName,source:files[t.tableName],entity:t.name,
 columns:t.columns.map(c=>({name:c.databaseName,property:c.propertyName,type:c.type,length:c.length,precision:c.precision,scale:c.scale,nullable:c.isNullable,primary:c.isPrimary,generated:c.isGenerated,default:c.default,enum:c.enum})),
 foreignKeys:t.foreignKeys.map(f=>({name:f.name,columns:f.columns.map(c=>c.databaseName),parent:f.referencedEntityMetadata.tableName,target:f.referencedColumns.map(c=>c.databaseName),onDelete:f.onDelete})),
 indexes:t.indices.map(i=>({name:i.name,columns:i.columns.map(c=>c.databaseName),unique:i.isUnique,where:i.where})),
 uniques:t.uniques.map(u=>({name:u.name,columns:u.columns.map(c=>c.databaseName)})),
 checks:t.checks.map(c=>({name:c.name,expression:c.expression})),
 exclusions:t.exclusions.map(c=>({name:c.name,expression:c.expression}))
})).sort((a,b)=>a.table.localeCompare(b.table));
writeFileSync(resolve(output,'../modelo_actual.json'),JSON.stringify(result,null,2));
const upSQL=[];
for(const m of migrations.sort((a,b)=>a.source.localeCompare(b.source))){
 const mod=await import(pathToFileURL(m.compiled).href);const cls=Object.values(mod).find(v=>typeof v==='function');
 const instance=new cls(); const queries=[];
 await instance.up({query:async sql=>{queries.push(sql);return []}});
 upSQL.push({file:relative(root,m.source).replaceAll('\\','/'),name:instance.name,queries});
}
writeFileSync(resolve(output,'../migraciones_actuales.json'),JSON.stringify(upSQL,null,2));
writeFileSync(resolve(output,'../fuentes_actuales.json'),JSON.stringify(walk(resolve(backend,'src')).filter(p=>p.endsWith('.ts')).map(p=>({file:relative(root,p).replaceAll('\\','/'),sha256:createHash('sha256').update(readFileSync(p)).digest('hex')})),null,2));
console.log(JSON.stringify({tablas:result.length,columnas:result.reduce((n,t)=>n+t.columns.length,0),foreignKeys:result.reduce((n,t)=>n+t.foreignKeys.length,0),migraciones:upSQL.length,tablasNombres:result.map(x=>x.table)}));
