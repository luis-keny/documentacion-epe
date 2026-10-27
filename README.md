# Documentación y acuerdos del esquema agroexportador

Este repositorio contiene la documentación discutida y el SQL de revisión. El primer commit se identifica con el mensaje **v1**. Se actualizan los mismos archivos; las versiones se conservan mediante Git.

## Documentos vigentes

- [Reporte por vista](agro-schema/01_reporte_especifico.md): 62 fichas con navegación, función de cada tabla, atributos, relaciones y decisiones D01–D15.
- [Validación de negocio y 30 preguntas pendientes](agro-schema/01_reporte_especifico.md#validación-de-negocio-y-cuestionario-pendiente): revisión adicional del 27/10/2026; incluye contradicciones entre documentos y código del prototipo y prioridades antes de implementar.
- [Respuestas del usuario y alcance limitado al prototipo](agro-schema/01_reporte_especifico.md#respuestas-y-alcance-limitado-al-prototipo): estado vigente del cuestionario, explicación de la duplicidad, reglas encontradas y diferencias por consultar. Los negocios adicionales solo se reportan y quedan fuera del alcance.
- [Esquema general y relaciones Mermaid por vista](agro-schema/02_tablas_y_relaciones.md): mapa de las 66 tablas, flujo funcional y recortes por vista.
- [SQL total de revisión](agro-schema/03_schema_total.sql): instalación nueva en el esquema PostgreSQL `agro`; no es una migración sobre la base existente.
- [Auditoría del backend frente al modelo previsto](agro-schema/auditoria-bd-actual-vs-planificada.md): comparación, decisiones confirmadas y pendientes. Se incorpora desde la documentación del backend para que también quede en este historial.
- [DBML inicial aportado](agro-schema/referencias/AGRO_SIMPLIFICADO.dbml): referencia original sin modificar; no representa el modelo objetivo corregido.

## Acuerdos confirmados al 27/10/2026

- Esta etapa comprende documentación y SQL para revisión manual; no se modifican entidades TypeORM, migraciones ni bases desplegadas.
- Se conservan los nombres físicos actuales. El modelo revisado incluye 66 tablas: 19 actuales y 47 propuestas. Una propuesta documentada no equivale a aprobación definitiva de implementación.
- `campania_x_proveedores` se mantiene y agrupa al proveedor y sus entrevistas dentro de una campaña. Se retira su vínculo directo a finca en el modelo objetivo.
- Las fincas de esa participación se obtienen mediante `entrevista_extencion`, que reutiliza los datos de finca y agrega los datos de la visita/campaña. Los orígenes de entrega y carga identifican la finca de recojo.
- Cada finca tendrá una sola variedad por ahora. La fruta se obtiene desde `fruta_derivada`; no se añade una tabla de varios cultivos por finca.
- `analisis_calidad` puede registrarse antes de cosecha, por participación y finca. Su vínculo con cosecha es opcional.
- `archivo` queda fuera del SQL y de los diagramas por ahora. Sus 28 referencias documentales quedan opcionales, sin FK y pendientes de relación.
- Se incluyen empresas de transporte, vehículos, choferes y sus asignaciones actuales. No se sustituyen automáticamente por las entidades propuestas del viaje multiproveedor.
- Administrador y Chofer comparten entidades. Los tableros, resúmenes y pestañas no crean una tabla de negocio independiente por pantalla.

## Decisiones pendientes

Las referencias D01–D15 de los reportes describen el estado y las vistas afectadas. Destacan la posible duplicidad de `participacion_proveedor_campana`, la autoridad entre las asignaciones actuales y `coordinacion_entrega`, la vinculación de transporte antes del acuerdo completo, la incorporación manual a Calidad, los destinos, los acuerdos de compra y las reglas de unicidad observadas en el mockup.

No se ha aprobado eliminar `campania_x_proveedores`. Tampoco se ha aprobado retirar automáticamente la cabecera adicional: su función sigue por discutir. La gestión documental se retomará en otra etapa.

## Evidencias y mantenimiento

La carpeta `agro-schema/.validation` conserva modelos, generadores y resultados de las comprobaciones, incluidos antecedentes del diseño. Los documentos vigentes son los enlazados arriba. Los archivos internos `baseline-*`, `modelo.json`, `modelo_alineado.json` y los generadores antiguos son antecedentes, no el esquema final.

El flujo vigente usa `modelo_revision.py`, `verificar_revision.mjs` y `documentar_revision.py`. Los resultados actuales constan en `resultado_revision.json`: 19 comprobaciones temporales con PGlite. No acreditan validación de una base desplegada ni implementación de todos los procesos de negocio. La reconstrucción de la auditoría del código requiere también el checkout del backend referido en sus fuentes.

Cada decisión posterior debe actualizar su ficha, el esquema general, el SQL si corresponde y la auditoría antes del siguiente commit. No ejecutar los generadores históricos para actualizar los documentos vigentes.

## Historial local

Desde esta carpeta:

```sh
git log --oneline
git status
git diff
```

Este repositorio es local. No se configura un remoto ni se publica documentación como parte de su creación.
