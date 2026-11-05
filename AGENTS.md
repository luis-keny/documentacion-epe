# Reglas de documentación transversal

- Escribe en español claro y directo. Prioriza información accionable; elimina contexto repetido y explicaciones que no cambien una decisión.
- Las solicitudes del desarrollador autorizan ajustar las vistas, reglas de negocio y simulación necesarias dentro de su alcance. Actualiza sus fuentes en el mismo cambio según el [flujo frontend](../epe-web/docs/development.md#cambios-de-vistas-reglas-de-negocio-y-mock); distingue la regla solicitada del comportamiento implementado y de cualquier adaptación backend pendiente. Cierra con una explicación breve y poco técnica del cambio, su impacto y lo verificado.
- Mantén una sola versión vigente por tema y usa nombres estables, sin fecha ni número de versión en el nombre del archivo.
- Pon fecha de revisión dentro del documento solo cuando ayude a evaluar su vigencia; no conviertas cada actualización en otro archivo.
- Crea versiones anteriores únicamente si preservan una decisión, auditoría, aceptación o evidencia que siga teniendo valor.
- Toda versión archivada debe indicar motivo, sucesor vigente y fecha de vencimiento. Como regla general, vence 90 días después de su fecha de revisión o de ser reemplazada, lo que ocurra después; elimínala entonces salvo que una obligación legal, aceptación, incidente o decisión aún vigente justifique conservarla. Documenta esa excepción y su próxima revisión.
- Revisa versiones archivadas al menos cada 90 días. No uses “histórico” como estado permanente sin una fecha de salida.
- Mantén documentación armonizada entre los repositorios involucrados: un cambio de API, modelo, flujo o estado requiere actualizar en el mismo cambio la fuente técnica, los consumidores afectados, sus índices y este resumen central. Si una afirmación deja de aplicar, corrígela o márcala como versión sustituida con vencimiento; nunca la dejes como guía vigente.
- Antes de cerrar un cambio documental, busca referencias cruzadas y verifica que todos los enlaces y resúmenes afectados describan el mismo estado. La fuente canónica puede vivir en un proyecto, pero los lectores de los demás deben encontrar allí la versión vigente.
- Antes de mover o eliminar, busca enlaces y referencias; actualiza los índices en el mismo cambio.
- Selección para agentes: usa el [README](README.md) como mapa cuando la tarea toque procesos compartidos, el modelo objetivo o evidencia histórica. Para cambios propios de `epe-web` o `epe-backend`, consulta solo las reglas y documentos del tema afectado que puedan cambiar una decisión o evitar una contradicción. No es requisito leer ni mencionar esta documentación en solicitudes ajenas a su alcance.
- Mantén solo tres archivos de reglas generales: este, `epe-web/AGENTS.md` y `epe-backend/AGENTS.md`. No crees AGENTS por módulo ni dentro de sus subcarpetas; registra reglas específicas en la sección adecuada del AGENTS general del proyecto.
- No modificar, mover ni añadir archivos a `prototipo/`; se conserva intacto por instrucción del usuario.
- El estado del backend se considera completado según la confirmación del usuario. No reabrir esa conclusión sin nueva evidencia o indicación.
