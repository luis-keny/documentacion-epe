# Modelo objetivo

Entrada para las propuestas de esquema que orientan revisión funcional o una futura decisión de datos. Este modelo no representa el esquema implementado ni una base desplegada.

## Fuentes y cuándo consultarlas

- [01_reporte_especifico.md](01_reporte_especifico.md): diccionario por vista; útil al revisar un campo, relación o regla propuesta.
- [02_tablas_y_relaciones.md](02_tablas_y_relaciones.md): mapa visual; útil para entender relaciones entre dominios.
- [03_schema_total.sql](03_schema_total.sql): SQL de instalación nueva para revisión; no es una migración del backend.
- [04_datos_iniciales.sql](04_datos_iniciales.sql): catálogos demostrativos del modelo objetivo; no sembrar en producción sin revisión.
- [Diagramas y sus fuentes](diagramas/): consultar vistas o regenerar salidas visuales.

Para el modelo implementado, consulta las [entidades y migraciones backend](../../epe-backend/src/database/) y el [ER derivado](../../epe-backend/docs/er-diagram.md). Las auditorías con fecha y salida están catalogadas en [historial](../history/README.md).
