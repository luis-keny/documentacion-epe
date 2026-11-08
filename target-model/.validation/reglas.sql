-- Validaciones estructurales entre módulos. Bloqueos en filas padre serializan consumos.
CREATE FUNCTION agro.validar_contexto() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE camp bigint; expected bigint; fruit bigint; otherfruit bigint; part bigint; prov bigint; ent bigint; coord bigint; drv bigint;
BEGIN
  IF TG_TABLE_NAME='campania_variedades' THEN
    SELECT fruta_id INTO fruit FROM campanias WHERE id=NEW.campania_id;
    SELECT fruta_id INTO otherfruit FROM variedades WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Variedad ajena a la fruta de campaña'; END IF;
  ELSIF TG_TABLE_NAME IN ('participacion_variedades','requerimiento_variedades') THEN
    IF TG_TABLE_NAME='participacion_variedades' THEN SELECT campania_id INTO camp FROM participaciones_proveedor WHERE id=NEW.participacion_id;
    ELSE SELECT campania_id INTO camp FROM requerimientos_comerciales WHERE id=NEW.requerimiento_id; END IF;
    SELECT c.fruta_id INTO fruit FROM campanias c WHERE c.id=camp;
    SELECT fruta_id INTO otherfruit FROM variedades WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Variedad incompatible con campaña'; END IF;
  ELSIF TG_TABLE_NAME='choferes' THEN
    IF NEW.usuario_id IS NOT NULL THEN
      IF NOT EXISTS(SELECT 1 FROM usuarios WHERE id=NEW.usuario_id AND persona_id=NEW.persona_id) THEN RAISE EXCEPTION 'Cuenta y chofer deben identificar a la misma persona'; END IF;
    END IF;
  ELSIF TG_TABLE_NAME='entregas_programadas' THEN
    SELECT r.cliente_id INTO expected FROM contratos_venta c JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE c.id=NEW.contrato_id;
    IF NOT EXISTS(SELECT 1 FROM destinos_cliente WHERE id=NEW.destino_id AND cliente_id=expected) THEN RAISE EXCEPTION 'Destino de otro cliente'; END IF;
  ELSIF TG_TABLE_NAME='entrega_variedades' THEN
    SELECT r.campania_id INTO camp FROM entregas_programadas e JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE e.id=NEW.entrega_id;
    SELECT fruta_id INTO fruit FROM campanias WHERE id=camp;
    SELECT fruta_id INTO otherfruit FROM variedades WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Distribución de variedad incompatible'; END IF;
  ELSIF TG_TABLE_NAME='coordinaciones_entrega' THEN
    SELECT r.campania_id INTO camp FROM entregas_programadas e JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE e.id=NEW.entrega_id;
    IF NOT EXISTS(SELECT 1 FROM acuerdos_transporte WHERE id=NEW.acuerdo_transporte_id AND campania_id=camp) THEN RAISE EXCEPTION 'Acuerdo de transporte de otra campaña'; END IF;
  ELSIF TG_TABLE_NAME='origenes_entrega' THEN
    SELECT r.campania_id INTO camp FROM coordinaciones_entrega co JOIN entregas_programadas e ON e.id=co.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE co.id=NEW.coordinacion_id;
    SELECT campania_id INTO expected FROM fincas_campania WHERE id=NEW.finca_campania_id;
    IF camp IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Finca de otra campaña'; END IF;
    IF EXISTS(SELECT 1 FROM coordinaciones_entrega co JOIN entregas_programadas e ON e.id=co.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id WHERE co.id=NEW.coordinacion_id AND c.canal='EXPORTACION') AND NOT EXISTS(SELECT 1 FROM fincas_campania f JOIN participaciones_proveedor p ON p.id=f.participacion_id WHERE f.id=NEW.finca_campania_id AND p.tipo_fruta='ORGANICA') THEN RAISE EXCEPTION 'Exportación exige origen orgánico según el prototipo'; END IF;
  ELSIF TG_TABLE_NAME='proveedores_carga' THEN
    SELECT coordinacion_id INTO coord FROM cargas WHERE id=NEW.carga_id;
    IF NOT EXISTS(SELECT 1 FROM origenes_entrega o JOIN fincas_campania f ON f.id=o.finca_campania_id WHERE o.coordinacion_id=coord AND f.participacion_id=NEW.participacion_id) THEN RAISE EXCEPTION 'Proveedor no coordinado para esta carga'; END IF;
    IF NOT EXISTS(SELECT 1 FROM participacion_variedades WHERE participacion_id=NEW.participacion_id AND variedad_id=NEW.variedad_id) THEN RAISE EXCEPTION 'Variedad no vinculada al proveedor en campaña'; END IF;
  ELSIF TG_TABLE_NAME='origenes_carga' THEN
    SELECT p.participacion_id,c.coordinacion_id INTO part,coord FROM proveedores_carga p JOIN cargas c ON c.id=p.carga_id WHERE p.id=NEW.proveedor_carga_id;
    IF NOT EXISTS(SELECT 1 FROM fincas_campania f JOIN origenes_entrega o ON o.finca_campania_id=f.id WHERE f.id=NEW.finca_campania_id AND f.participacion_id=part AND o.coordinacion_id=coord) THEN RAISE EXCEPTION 'Origen ajeno al proveedor o a su coordinación'; END IF;
  ELSIF TG_TABLE_NAME='analisis_calidad' THEN
    SELECT r.campania_id INTO camp FROM cosechas h JOIN entregas_programadas e ON e.id=h.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE h.id=NEW.cosecha_id;
    IF NOT EXISTS(SELECT 1 FROM fincas_campania WHERE id=NEW.finca_campania_id AND campania_id=camp) THEN RAISE EXCEPTION 'Análisis de finca ajena a campaña'; END IF;
  ELSIF TG_TABLE_NAME='recepciones_planta' THEN
    SELECT co.chofer_id INTO drv FROM cargas ca JOIN coordinaciones_entrega co ON co.id=ca.coordinacion_id WHERE ca.id=NEW.carga_id;
    IF drv IS DISTINCT FROM NEW.chofer_id THEN RAISE EXCEPTION 'Recepción de otro chofer'; END IF;
  ELSIF TG_TABLE_NAME='historial_chofer' THEN
    SELECT chofer_id INTO drv FROM coordinaciones_entrega WHERE id=NEW.coordinacion_id;
    IF drv IS DISTINCT FROM NEW.chofer_id THEN RAISE EXCEPTION 'Despacho de otro chofer'; END IF;
  END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['campania_variedades','participacion_variedades','requerimiento_variedades','choferes','entregas_programadas','entrega_variedades','coordinaciones_entrega','origenes_entrega','proveedores_carga','origenes_carga','analisis_calidad','recepciones_planta','historial_chofer'] LOOP
 EXECUTE format('CREATE TRIGGER contexto BEFORE INSERT OR UPDATE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.validar_contexto()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_programacion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE parent bigint; total numeric; limite numeric;
BEGIN
  IF TG_TABLE_NAME='entregas_programadas' THEN
    parent:=NEW.contrato_id;
    SELECT kilos_acordados INTO limite FROM contratos_venta WHERE id=parent FOR UPDATE;
    SELECT coalesce(sum(kilos_programados),0) INTO total FROM entregas_programadas WHERE contrato_id=parent AND id<>NEW.id;
    IF total+NEW.kilos_programados>limite THEN RAISE EXCEPTION 'Kilos programados exceden contrato'; END IF;
  ELSE
    SELECT coalesce(sum(kilos_programados),0) INTO total FROM entregas_programadas WHERE contrato_id=NEW.id;
    IF total>NEW.kilos_acordados THEN RAISE EXCEPTION 'Contrato menor que su programación'; END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER programacion BEFORE INSERT OR UPDATE ON agro.entregas_programadas FOR EACH ROW EXECUTE FUNCTION agro.validar_programacion();
CREATE TRIGGER programacion BEFORE UPDATE ON agro.contratos_venta FOR EACH ROW EXECUTE FUNCTION agro.validar_programacion();

-- La distribución por variedad debe ser completa; se puede crear cabecera y detalle en una transacción.
CREATE FUNCTION agro.validar_distribucion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE e bigint; total numeric; esperado numeric;
BEGIN
  IF TG_TABLE_NAME='entregas_programadas' THEN e:=coalesce(NEW.id,OLD.id);
  ELSE e:=coalesce(NEW.entrega_id,OLD.entrega_id); END IF;
  SELECT kilos_programados INTO esperado FROM entregas_programadas WHERE id=e;
  IF esperado IS NULL THEN RETURN NULL; END IF;
  SELECT coalesce(sum(kilos_programados),0) INTO total FROM entrega_variedades WHERE entrega_id=e;
  IF total<>esperado THEN RAISE EXCEPTION 'Distribución por variedades no coincide con entrega %',e; END IF;
  IF TG_TABLE_NAME='entrega_variedades' THEN
    IF TG_OP='UPDATE' THEN
      IF OLD.entrega_id<>NEW.entrega_id THEN RAISE EXCEPTION 'No reasignar detalle; quitar y crear en transacción'; END IF;
    END IF;
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER distribucion AFTER INSERT OR UPDATE ON agro.entregas_programadas DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION agro.validar_distribucion();
CREATE CONSTRAINT TRIGGER distribucion AFTER INSERT OR UPDATE OR DELETE ON agro.entrega_variedades DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION agro.validar_distribucion();

CREATE FUNCTION agro.validar_asignacion_guia() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE limite numeric; usado numeric; origen bigint;
BEGIN
  SELECT kilos_cargados INTO limite FROM proveedores_carga WHERE id=NEW.proveedor_carga_id FOR UPDATE;
  SELECT coalesce(sum(kilos_asignados),0) INTO usado FROM proveedores_guia WHERE proveedor_carga_id=NEW.proveedor_carga_id AND id<>NEW.id;
  IF usado+NEW.kilos_asignados>limite THEN RAISE EXCEPTION 'Kilos de proveedor duplicados entre guías'; END IF;
  SELECT finca_partida_id INTO origen FROM guias_remision WHERE id=NEW.guia_id;
  IF NOT EXISTS(SELECT 1 FROM origenes_carga o JOIN fincas_campania f ON f.id=o.finca_campania_id WHERE o.proveedor_carga_id=NEW.proveedor_carga_id AND f.finca_id=origen) THEN RAISE EXCEPTION 'Proveedor sin trazabilidad al punto de partida de la guía'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER asignacion_guia BEFORE INSERT OR UPDATE ON agro.proveedores_guia FOR EACH ROW EXECUTE FUNCTION agro.validar_asignacion_guia();

CREATE FUNCTION agro.validar_liquidacion_compra() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE calculado numeric; faltan bigint;
BEGIN
  SELECT round(sum(pc.kilos_cargados*pc.precio_compra_kg_aplicado),2),count(*) FILTER(WHERE pc.precio_compra_kg_aplicado IS NULL)
  INTO calculado,faltan FROM proveedores_carga pc JOIN participaciones_proveedor p ON p.id=pc.participacion_id
  WHERE pc.carga_id=NEW.carga_id AND p.proveedor_id=NEW.proveedor_id;
  IF calculado IS NULL OR faltan>0 OR calculado<>NEW.importe_compra THEN RAISE EXCEPTION 'Compra debe coincidir con kilos y precios de ese proveedor'; END IF;
  IF NOT EXISTS(SELECT 1 FROM personas_proveedor WHERE proveedor_id=NEW.proveedor_id AND persona_id=NEW.persona_liquidacion_id AND activo) THEN RAISE EXCEPTION 'Persona no vinculada activamente al proveedor'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER importe_compra BEFORE INSERT OR UPDATE ON agro.liquidaciones_proveedor FOR EACH ROW EXECUTE FUNCTION agro.validar_liquidacion_compra();

CREATE FUNCTION agro.validar_factura() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE peso numeric; precio numeric; divisa text; resultado text; respaldo bigint;
BEGIN
  SELECT rp.peso_planta_kg,rp.resultado,rp.reporte_recepcion_id INTO peso,resultado,respaldo FROM recepciones_planta rp WHERE rp.carga_id=NEW.carga_id FOR UPDATE;
  IF peso IS NULL OR resultado IS NULL OR respaldo IS NULL THEN RAISE EXCEPTION 'Facturación requiere recepción documentada, resultado y peso'; END IF;
  SELECT c.precio_kg,c.moneda INTO precio,divisa FROM cargas ca JOIN coordinaciones_entrega co ON co.id=ca.coordinacion_id JOIN entregas_programadas e ON e.id=co.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id WHERE ca.id=NEW.carga_id FOR UPDATE OF c;
  IF NEW.kilos_facturados<>peso OR NEW.precio_kg_aplicado<>precio OR NEW.moneda<>divisa THEN RAISE EXCEPTION 'Factura debe capturar peso recibido y condiciones de contrato'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER factura_consistente BEFORE INSERT OR UPDATE ON agro.facturas_venta FOR EACH ROW EXECUTE FUNCTION agro.validar_factura();

CREATE FUNCTION agro.validar_saldos() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE limite numeric; usado numeric; extra numeric:=0; aid bigint; expected bigint;
BEGIN
  IF TG_TABLE_NAME='pagos_proveedor' THEN
    SELECT importe_compra INTO limite FROM liquidaciones_proveedor WHERE id=NEW.liquidacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pagos_proveedor WHERE liquidacion_id=NEW.liquidacion_id;
  ELSIF TG_TABLE_NAME='cobros_venta' THEN
    SELECT importe_venta INTO limite FROM facturas_venta WHERE id=NEW.factura_id AND estado='EMITIDA' FOR UPDATE;
    IF limite IS NULL THEN RAISE EXCEPTION 'No cobrar una preparación sin factura emitida'; END IF;
    SELECT coalesce(sum(monto),0) INTO usado FROM cobros_venta WHERE factura_id=NEW.factura_id;
  ELSIF TG_TABLE_NAME='pagos_certificacion' THEN
    SELECT costo INTO limite FROM certificaciones WHERE id=NEW.certificacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pagos_certificacion WHERE certificacion_id=NEW.certificacion_id;
  ELSIF TG_TABLE_NAME='adelantos_transporte' THEN
    SELECT monto_acordado INTO limite FROM acuerdos_transporte WHERE id=NEW.acuerdo_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM adelantos_transporte WHERE acuerdo_id=NEW.acuerdo_id;
  ELSE
    SELECT l.flete+coalesce((SELECT sum(g.monto) FROM gastos_transporte g WHERE g.carga_id=l.carga_id AND g.incluido_en_liquidacion),0)
    INTO limite FROM liquidaciones_transporte l WHERE l.id=NEW.liquidacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pagos_transporte WHERE liquidacion_id=NEW.liquidacion_id;
    SELECT coalesce(sum(monto),0) INTO extra FROM aplicaciones_adelanto WHERE liquidacion_id=NEW.liquidacion_id;
    IF TG_TABLE_NAME='aplicaciones_adelanto' THEN
      SELECT co.acuerdo_transporte_id INTO expected FROM liquidaciones_transporte l JOIN cargas c ON c.id=l.carga_id JOIN coordinaciones_entrega co ON co.id=c.coordinacion_id WHERE l.id=NEW.liquidacion_id;
      SELECT acuerdo_id INTO aid FROM adelantos_transporte WHERE id=NEW.adelanto_id FOR UPDATE;
      IF aid IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Adelanto de otro acuerdo'; END IF;
      IF NEW.monto+(SELECT coalesce(sum(monto),0) FROM aplicaciones_adelanto WHERE adelanto_id=NEW.adelanto_id)>(SELECT monto FROM adelantos_transporte WHERE id=NEW.adelanto_id) THEN RAISE EXCEPTION 'Adelanto agotado'; END IF;
    END IF;
  END IF;
  IF NEW.monto+usado+extra>limite THEN RAISE EXCEPTION 'Movimiento excede saldo disponible'; END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['pagos_proveedor','pagos_transporte','cobros_venta','pagos_certificacion','adelantos_transporte','aplicaciones_adelanto'] LOOP
 EXECUTE format('CREATE TRIGGER saldo BEFORE INSERT ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.validar_saldos()',t);
END LOOP; END $$;

-- Historial financiero inmutable. Correcciones contables requieren un futuro flujo de reversos.
CREATE FUNCTION agro.no_alterar_historial() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Historial protegido: no editar ni eliminar; implementar reverso explícito'; END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['pagos_proveedor','pagos_transporte','cobros_venta','pagos_certificacion','adelantos_transporte','aplicaciones_adelanto','historial_chofer','ampliaciones_certificacion','mediciones_mtd'] LOOP
 EXECUTE format('CREATE TRIGGER inmutable BEFORE UPDATE OR DELETE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.no_alterar_historial()',t);
END LOOP; END $$;

-- Se congelan cabeceras y orígenes utilizados por documentos. Impide vaciar sus detalles.
CREATE FUNCTION agro.proteger_documentos() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE cid bigint; protegido boolean:=false;
BEGIN
  IF TG_TABLE_NAME IN ('liquidaciones_proveedor','liquidaciones_transporte') THEN
    RAISE EXCEPTION 'Liquidación registrada protegida; registrar corrección mediante un flujo de reverso';
  ELSIF TG_TABLE_NAME='facturas_venta' THEN
    protegido:=OLD.estado='EMITIDA';
    IF NOT protegido AND TG_OP='UPDATE' THEN
      IF (to_jsonb(NEW)-ARRAY['estado','numero_factura','fecha_emision','fecha_vencimiento','archivo_id']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['estado','numero_factura','fecha_emision','fecha_vencimiento','archivo_id']) THEN RAISE EXCEPTION 'Preparación solo admite completar datos de emisión'; END IF;
    END IF;
  ELSIF TG_TABLE_NAME='contratos_venta' THEN
    SELECT EXISTS(SELECT 1 FROM entregas_programadas e JOIN coordinaciones_entrega co ON co.entrega_id=e.id JOIN cargas ca ON ca.coordinacion_id=co.id JOIN facturas_venta f ON f.carga_id=ca.id WHERE e.contrato_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='requerimientos_comerciales' THEN
    SELECT EXISTS(SELECT 1 FROM contratos_venta WHERE requerimiento_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='certificaciones' THEN
    SELECT EXISTS(SELECT 1 FROM pagos_certificacion WHERE certificacion_id=OLD.id) OR EXISTS(SELECT 1 FROM ampliaciones_certificacion WHERE certificacion_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='acuerdos_transporte' THEN
    SELECT EXISTS(SELECT 1 FROM adelantos_transporte WHERE acuerdo_id=OLD.id) OR EXISTS(SELECT 1 FROM coordinaciones_entrega co JOIN cargas ca ON ca.coordinacion_id=co.id JOIN liquidaciones_transporte l ON l.carga_id=ca.id WHERE co.acuerdo_transporte_id=OLD.id) INTO protegido;
  ELSE
    CASE TG_TABLE_NAME
      WHEN 'cargas' THEN cid:=OLD.id;
      WHEN 'coordinaciones_entrega' THEN SELECT id INTO cid FROM cargas WHERE coordinacion_id=OLD.id;
      WHEN 'origenes_entrega' THEN SELECT id INTO cid FROM cargas WHERE coordinacion_id=OLD.coordinacion_id;
      WHEN 'origenes_carga' THEN SELECT carga_id INTO cid FROM proveedores_carga WHERE id=OLD.proveedor_carga_id;
      WHEN 'entregas_programadas' THEN SELECT ca.id INTO cid FROM cargas ca JOIN coordinaciones_entrega co ON co.id=ca.coordinacion_id WHERE co.entrega_id=OLD.id;
      WHEN 'entrega_variedades' THEN SELECT ca.id INTO cid FROM cargas ca JOIN coordinaciones_entrega co ON co.id=ca.coordinacion_id WHERE co.entrega_id=OLD.entrega_id;
      ELSE cid:=OLD.carga_id;
    END CASE;
    SELECT EXISTS(SELECT 1 FROM facturas_venta WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidaciones_proveedor WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidaciones_transporte WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM guias_remision WHERE carga_id=cid) INTO protegido;
    -- Permite agregar recepción y adjuntar guía de salida sin alterar carga/origen ya documentados.
    IF protegido AND TG_TABLE_NAME='cargas' AND TG_OP='UPDATE' THEN
      protegido := (to_jsonb(NEW)-ARRAY['guia_salida_id','guia_salida_registrada_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['guia_salida_id','guia_salida_registrada_at']);
    END IF;
    IF TG_TABLE_NAME='recepciones_planta' THEN
      SELECT EXISTS(SELECT 1 FROM facturas_venta WHERE carga_id=cid) INTO protegido;
      IF protegido AND TG_OP='UPDATE' THEN
        protegido := (to_jsonb(NEW)-ARRAY['descarga_at','cierre_fisico_at','cierre_administrativo_at','jabas_devueltas','jabas_devolucion_at','recepcion_confirmada_at','descarte_confirmado_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['descarga_at','cierre_fisico_at','cierre_administrativo_at','jabas_devueltas','jabas_devolucion_at','recepcion_confirmada_at','descarte_confirmado_at']);
      END IF;
    END IF;
  END IF;
  IF protegido THEN RAISE EXCEPTION 'Documento u origen protegido por movimientos o documentación registrada'; END IF;
  IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['liquidaciones_proveedor','liquidaciones_transporte','facturas_venta','contratos_venta','requerimientos_comerciales','certificaciones','acuerdos_transporte','cargas','coordinaciones_entrega','origenes_entrega','origenes_carga','entregas_programadas','entrega_variedades','proveedores_carga','gastos_transporte','recepciones_planta','guias_remision'] LOOP
 EXECUTE format('CREATE TRIGGER proteger BEFORE UPDATE OR DELETE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.proteger_documentos()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_secuencia_chofer() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE previo text; requerido text; rp recepciones_planta%ROWTYPE;
BEGIN
  PERFORM 1 FROM coordinaciones_entrega WHERE id=NEW.coordinacion_id FOR UPDATE;
  SELECT estado INTO previo FROM historial_chofer WHERE coordinacion_id=NEW.coordinacion_id ORDER BY fecha_hora DESC,id DESC LIMIT 1;
  requerido:=CASE coalesce(previo,'') WHEN '' THEN 'EN_CARGA' WHEN 'EN_CARGA' THEN 'SALIDA' WHEN 'SALIDA' THEN 'EN_CAMINO' WHEN 'EN_CAMINO' THEN 'LLEGADA' WHEN 'LLEGADA' THEN 'CIERRE' ELSE NULL END;
  IF requerido IS NULL OR NEW.estado<>requerido THEN RAISE EXCEPTION 'Secuencia de despacho inválida'; END IF;
  IF EXISTS(SELECT 1 FROM historial_chofer WHERE coordinacion_id=NEW.coordinacion_id AND fecha_hora>NEW.fecha_hora) THEN RAISE EXCEPTION 'Evento anterior al último reporte'; END IF;
  IF NEW.estado='CIERRE' THEN
    SELECT * INTO rp FROM recepciones_planta WHERE carga_id=NEW.carga_id;
    IF rp.recepcion_confirmada_at IS NULL OR rp.descarte_confirmado_at IS NULL OR rp.peso_planta_kg IS NULL OR rp.hubo_descarte IS NULL OR rp.descarte_kg IS NULL THEN RAISE EXCEPTION 'Checklist de recepción y descarte incompleto'; END IF;
    IF NOT EXISTS(SELECT 1 FROM cargas WHERE id=NEW.carga_id AND guia_salida_id IS NOT NULL) THEN RAISE EXCEPTION 'Falta guía de salida'; END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER secuencia BEFORE INSERT ON agro.historial_chofer FOR EACH ROW EXECUTE FUNCTION agro.validar_secuencia_chofer();

-- Consultas derivadas: no se almacenan saldos ni copias de resúmenes por pantalla.
CREATE VIEW agro.v_saldo_proveedor AS
SELECT l.*,l.importe_compra-coalesce((SELECT sum(p.monto) FROM agro.pagos_proveedor p WHERE p.liquidacion_id=l.id),0) AS saldo
FROM agro.liquidaciones_proveedor l;
CREATE VIEW agro.v_saldo_factura AS
SELECT f.*,f.importe_venta-coalesce((SELECT sum(c.monto) FROM agro.cobros_venta c WHERE c.factura_id=f.id),0) AS saldo
FROM agro.facturas_venta f;
CREATE VIEW agro.v_saldo_transporte AS
SELECT l.*,l.flete+coalesce((SELECT sum(g.monto) FROM agro.gastos_transporte g WHERE g.carga_id=l.carga_id AND g.incluido_en_liquidacion),0)
-coalesce((SELECT sum(p.monto) FROM agro.pagos_transporte p WHERE p.liquidacion_id=l.id),0)
-coalesce((SELECT sum(a.monto) FROM agro.aplicaciones_adelanto a WHERE a.liquidacion_id=l.id),0) AS saldo
FROM agro.liquidaciones_transporte l;
CREATE VIEW agro.v_control_uit AS
SELECT p.persona_liquidacion_id,extract(year FROM p.fecha)::integer AS anio,sum(p.importe_compra) AS acumulado,
u.valor,u.limite_uit,u.valor*u.limite_uit-sum(p.importe_compra) AS disponible
FROM agro.liquidaciones_proveedor p LEFT JOIN agro.parametros_uit u ON u.anio=extract(year FROM p.fecha)::integer
GROUP BY p.persona_liquidacion_id,extract(year FROM p.fecha)::integer,u.valor,u.limite_uit;
CREATE VIEW agro.v_estado_despacho AS
SELECT DISTINCT ON (coordinacion_id) coordinacion_id,carga_id,chofer_id,estado,fecha_hora
FROM agro.historial_chofer ORDER BY coordinacion_id,fecha_hora DESC,id DESC;
CREATE VIEW agro.v_programa_semanal AS
SELECT r.campania_id,r.cliente_id,c.id AS contrato_id,e.id AS entrega_id,e.fecha,
extract(isoyear FROM e.fecha)::integer AS anio_iso,extract(week FROM e.fecha)::integer AS semana_iso,
d.variedad_id,d.kilos_programados,co.vehiculo_id
FROM agro.entregas_programadas e JOIN agro.entrega_variedades d ON d.entrega_id=e.id
JOIN agro.contratos_venta c ON c.id=e.contrato_id JOIN agro.requerimientos_comerciales r ON r.id=c.requerimiento_id
LEFT JOIN agro.coordinaciones_entrega co ON co.entrega_id=e.id;

-- El cierre exige validación transaccional del servicio descrita en el reporte.
-- Esta función añade un mínimo verificable en BD: no cerrar con entregas sin carga,
-- despachos abiertos, recepciones incompletas, facturas, liquidaciones o saldos pendientes.
CREATE FUNCTION agro.validar_cierre_campania() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE abiertos bigint;
BEGIN
 IF OLD.estado='FINALIZADO' THEN RAISE EXCEPTION 'Campaña finalizada protegida'; END IF;
 IF NEW.estado='FINALIZADO' THEN
   SELECT count(*) INTO abiertos FROM entregas_programadas e JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id
   LEFT JOIN coordinaciones_entrega co ON co.entrega_id=e.id LEFT JOIN cargas ca ON ca.coordinacion_id=co.id
   LEFT JOIN recepciones_planta rp ON rp.carga_id=ca.id LEFT JOIN v_estado_despacho h ON h.coordinacion_id=co.id
   LEFT JOIN facturas_venta f ON f.carga_id=ca.id LEFT JOIN v_saldo_transporte st ON st.carga_id=ca.id
   WHERE r.campania_id=NEW.id AND (ca.id IS NULL OR h.estado IS DISTINCT FROM 'CIERRE' OR rp.peso_planta_kg IS NULL OR rp.resultado IS NULL OR rp.reporte_recepcion_id IS NULL OR rp.descarga_at IS NULL OR rp.cierre_fisico_at IS NULL OR rp.cierre_administrativo_at IS NULL OR f.estado IS DISTINCT FROM 'EMITIDA' OR st.id IS NULL OR st.saldo<>0);
   IF abiertos>0 THEN RAISE EXCEPTION 'Campaña con entregas o cierres pendientes'; END IF;
   IF EXISTS(SELECT 1 FROM contratos_venta c JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND c.kilos_acordados<>(SELECT coalesce(sum(kilos_programados),0) FROM entregas_programadas e WHERE e.contrato_id=c.id)) THEN RAISE EXCEPTION 'Contrato sin programación completa'; END IF;
   IF EXISTS(SELECT 1 FROM v_saldo_factura f JOIN cargas ca ON ca.id=f.carga_id JOIN coordinaciones_entrega co ON co.id=ca.coordinacion_id JOIN entregas_programadas e ON e.id=co.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND f.saldo<>0) THEN RAISE EXCEPTION 'Cobros pendientes'; END IF;
   IF EXISTS(SELECT 1 FROM proveedores_carga pc JOIN participaciones_proveedor pp ON pp.id=pc.participacion_id LEFT JOIN v_saldo_proveedor s ON s.carga_id=pc.carga_id AND s.proveedor_id=pp.proveedor_id WHERE pp.campania_id=NEW.id AND (s.id IS NULL OR s.saldo<>0)) THEN RAISE EXCEPTION 'Compras sin liquidar o pagar'; END IF;
   IF EXISTS(SELECT 1 FROM certificaciones c WHERE c.campania_id=NEW.id AND c.costo<>(SELECT coalesce(sum(monto),0) FROM pagos_certificacion p WHERE p.certificacion_id=c.id)) THEN RAISE EXCEPTION 'Certificación por pagar'; END IF;
   IF EXISTS(SELECT 1 FROM adelantos_transporte a JOIN acuerdos_transporte ac ON ac.id=a.acuerdo_id WHERE ac.campania_id=NEW.id AND a.monto<>(SELECT coalesce(sum(monto),0) FROM aplicaciones_adelanto ap WHERE ap.adelanto_id=a.id)) THEN RAISE EXCEPTION 'Adelantos sin aplicar'; END IF;
   IF EXISTS(SELECT 1 FROM cosechas h JOIN entregas_programadas e ON e.id=h.entrega_id JOIN contratos_venta c ON c.id=e.contrato_id JOIN requerimientos_comerciales r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND (h.estado<>'CONCLUIDA' OR (c.canal='EXPORTACION' AND h.cierre_cosecha_at IS NULL))) THEN RAISE EXCEPTION 'Cosechas sin concluir'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER cierre BEFORE UPDATE ON agro.campanias FOR EACH ROW EXECUTE FUNCTION agro.validar_cierre_campania();

-- Sin usuarios, credenciales ni datos de demostración. No concede acceso público a tablas.
REVOKE ALL ON SCHEMA agro FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA agro FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA agro FROM PUBLIC;
-- Evita agregar líneas a posteriori para desajustar un documento ya registrado.
CREATE FUNCTION agro.proteger_nuevos_detalles() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE cid bigint;
BEGIN
  IF TG_TABLE_NAME='origenes_carga' THEN
    SELECT carga_id INTO cid FROM proveedores_carga WHERE id=NEW.proveedor_carga_id;
  ELSIF TG_TABLE_NAME='origenes_entrega' THEN
    SELECT id INTO cid FROM cargas WHERE coordinacion_id=NEW.coordinacion_id;
  ELSE cid:=NEW.carga_id; END IF;
  IF TG_TABLE_NAME='gastos_transporte' THEN
    IF EXISTS(SELECT 1 FROM liquidaciones_transporte WHERE carga_id=cid) THEN RAISE EXCEPTION 'No agregar gastos a transporte ya liquidado'; END IF;
    RETURN NEW;
  END IF;
  IF EXISTS(SELECT 1 FROM facturas_venta WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidaciones_proveedor WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidaciones_transporte WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM guias_remision WHERE carga_id=cid) THEN
    RAISE EXCEPTION 'No agregar detalle a carga ya documentada';
  END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['proveedores_carga','origenes_carga','origenes_entrega','gastos_transporte'] LOOP
 EXECUTE format('CREATE TRIGGER nuevo_detalle BEFORE INSERT ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.proteger_nuevos_detalles()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_recepcion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE origen numeric;
BEGIN
 SELECT sum(kilos_cargados) INTO origen FROM proveedores_carga WHERE carga_id=NEW.carga_id;
 IF NEW.descarte_kg>origen THEN RAISE EXCEPTION 'Descarte superior al peso de origen'; END IF;
 IF NEW.recepcion_confirmada_at IS NOT NULL AND (NEW.peso_planta_kg IS NULL OR NEW.fecha_recepcion IS NULL) THEN RAISE EXCEPTION 'Recepción confirmada requiere peso y fecha'; END IF;
 IF NEW.descarte_confirmado_at IS NOT NULL AND (NEW.hubo_descarte IS NULL OR NEW.descarte_kg IS NULL) THEN RAISE EXCEPTION 'Confirmar explícitamente si hubo descarte y su cantidad'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER recepcion_valida BEFORE INSERT OR UPDATE ON agro.recepciones_planta FOR EACH ROW EXECUTE FUNCTION agro.validar_recepcion();
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA agro FROM PUBLIC;
COMMIT;
