-- Protecciones funcionales acotadas: no sustituye servicios de permisos/cierre.
CREATE FUNCTION validar_recepcion_compras() RETURNS trigger
LANGUAGE plpgsql SET search_path = agro, pg_temp AS $$
DECLARE item jsonb; ids integer[] := '{}'; pid integer; total numeric := 0; completos boolean := true; cargado numeric;
BEGIN
  FOR item IN SELECT value FROM jsonb_array_elements(NEW.compras) LOOP
    IF jsonb_typeof(item) <> 'object' OR NOT item ? 'providerId' THEN
      RAISE EXCEPTION 'Cada compra requiere providerId y datos de revisión';
    END IF;
    pid := (item->>'providerId')::integer;
    IF pid IS NULL OR pid = ANY(ids) THEN RAISE EXCEPTION 'Proveedor duplicado o inválido en recepción'; END IF;
    ids := array_append(ids, pid);
    SELECT sum(pc.kilos_cargados) INTO cargado FROM proveedor_carga pc
      JOIN campania_x_proveedores p ON p.cxp_id=pc.cxp_id
      WHERE pc.carga_id=NEW.carga_id AND p.proveedor_id=pid;
    IF cargado IS NULL THEN RAISE EXCEPTION 'El proveedor no pertenece a esta carga'; END IF;
    IF item->>'recognizedQuantity' IS NULL THEN completos := false;
    ELSE
      IF (item->>'recognizedQuantity')::numeric <= 0 OR (item->>'recognizedQuantity')::numeric > cargado + 0.01 THEN
        RAISE EXCEPTION 'Kilos reconocidos fuera de los kilos cargados del proveedor';
      END IF;
      total := total + (item->>'recognizedQuantity')::numeric;
    END IF;
  END LOOP;
  IF jsonb_array_length(NEW.compras)>0 AND completos THEN
    IF NEW.peso_planta_kg IS NULL OR abs(total-NEW.peso_planta_kg)>0.01 THEN
      RAISE EXCEPTION 'La suma reconocida debe coincidir con el peso de planta';
    END IF;
    IF cardinality(ids) <> (SELECT count(DISTINCT p.proveedor_id) FROM proveedor_carga pc
      JOIN campania_x_proveedores p ON p.cxp_id=pc.cxp_id WHERE pc.carga_id=NEW.carga_id) THEN
      RAISE EXCEPTION 'Completa el desglose de todos los proveedores';
    END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER trg_recepcion_compras BEFORE INSERT OR UPDATE OF compras,peso_planta_kg,carga_id
ON recepcion_planta FOR EACH ROW EXECUTE FUNCTION validar_recepcion_compras();

CREATE FUNCTION validar_persona_liquidacion() RETURNS trigger
LANGUAGE plpgsql SET search_path = agro, pg_temp AS $$
DECLARE p persona%ROWTYPE; titular boolean; reconocidos numeric; proveedores integer; precio_acuerdo numeric;
BEGIN
  SELECT * INTO STRICT p FROM persona WHERE persona_id=NEW.persona_liquidacion_id;
  SELECT (proveedor.persona_id=p.persona_id OR (proveedor.nmr_documento=p.numero_documento AND proveedor.tipo_documento::text=p.tipo_documento))
    INTO titular FROM proveedor WHERE proveedor_id=NEW.proveedor_id;
  IF NOT coalesce(titular,false) AND NOT EXISTS(SELECT 1 FROM proveedor_x_persona
    WHERE proveedor_id=NEW.proveedor_id AND persona_id=p.persona_id AND activo) THEN
    RAISE EXCEPTION 'La persona no es el proveedor principal ni una persona vinculada activa';
  END IF;
  SELECT (x->>'recognizedQuantity')::numeric INTO reconocidos FROM recepcion_planta r,
    LATERAL jsonb_array_elements(r.compras) x WHERE r.carga_id=NEW.carga_id AND (x->>'providerId')::integer=NEW.proveedor_id;
  IF reconocidos IS NULL THEN
    SELECT count(DISTINCT p.proveedor_id) INTO proveedores FROM proveedor_carga pc JOIN campania_x_proveedores p
      ON p.cxp_id=pc.cxp_id WHERE pc.carga_id=NEW.carga_id;
    IF proveedores=1 AND EXISTS(SELECT 1 FROM proveedor_carga pc JOIN campania_x_proveedores p
      ON p.cxp_id=pc.cxp_id WHERE pc.carga_id=NEW.carga_id AND p.proveedor_id=NEW.proveedor_id) THEN
      SELECT peso_planta_kg INTO reconocidos FROM recepcion_planta WHERE carga_id=NEW.carga_id;
    END IF;
  END IF;
  IF reconocidos IS NULL OR abs(reconocidos-NEW.kilos_reconocidos)>0.01 THEN RAISE EXCEPTION 'Liquida los kilos reconocidos del proveedor en planta'; END IF;
  SELECT cxp.precio_compra_kg INTO precio_acuerdo FROM campania_x_proveedores cxp
    JOIN coordinacion_entrega co ON co.coordinacion_entrega_id=(SELECT coordinacion_entrega_id FROM carga WHERE carga_id=NEW.carga_id)
    JOIN entrega_programada e ON e.entrega_programada_id=co.entrega_programada_id
    JOIN contrato_venta cv ON cv.contrato_venta_id=e.contrato_venta_id
    JOIN cliente_negocio_campana cc ON cc.cliente_negocio_campana_id=cv.cliente_negocio_campana_id
    WHERE cxp.campania_id=cc.campania_id AND cxp.proveedor_id=NEW.proveedor_id;
  IF precio_acuerdo IS NULL OR precio_acuerdo IS DISTINCT FROM NEW.precio_kg_aplicado THEN RAISE EXCEPTION 'Completa el precio de compra de la participación antes de liquidar'; END IF;
  IF TG_OP='INSERT' THEN
    NEW.persona_snapshot := jsonb_build_object('nombres',p.nombres,'apellidos',p.apellidos,'tipoDocumento',p.tipo_documento,'dni',p.numero_documento);
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER trg_persona_liquidacion BEFORE INSERT OR UPDATE OF persona_liquidacion_id,proveedor_id,carga_id,kilos_reconocidos,precio_kg_aplicado
ON liquidacion_proveedor FOR EACH ROW EXECUTE FUNCTION validar_persona_liquidacion();

CREATE FUNCTION proteger_documento_financiero() RETURNS trigger
LANGUAGE plpgsql SET search_path = agro, pg_temp AS $$
DECLARE tiene_movimientos boolean; recibido numeric; facturado numeric; precio_contrato numeric; moneda_contrato text;
BEGIN
  IF TG_TABLE_NAME='factura_venta' THEN
    -- Serializa documentos de la misma carga antes de repartir los kilos recibidos.
    PERFORM 1 FROM carga WHERE carga_id=NEW.carga_id FOR UPDATE;
    SELECT cv.precio_kg,cv.moneda INTO precio_contrato,moneda_contrato FROM carga c
      JOIN coordinacion_entrega co ON co.coordinacion_entrega_id=c.coordinacion_entrega_id
      JOIN entrega_programada e ON e.entrega_programada_id=co.entrega_programada_id
      JOIN contrato_venta cv ON cv.contrato_venta_id=e.contrato_venta_id WHERE c.carga_id=NEW.carga_id;
    IF TG_OP='INSERT' AND (precio_contrato IS NULL OR precio_contrato IS DISTINCT FROM NEW.precio_kg_aplicado OR moneda_contrato IS DISTINCT FROM NEW.moneda) THEN
      RAISE EXCEPTION 'Completa el precio y usa la moneda del contrato antes de facturar';
    END IF;
    SELECT peso_planta_kg INTO recibido FROM recepcion_planta WHERE carga_id=NEW.carga_id;
    SELECT coalesce(sum(kilos_facturados),0) INTO facturado FROM factura_venta WHERE carga_id=NEW.carga_id AND factura_venta_id<>NEW.factura_venta_id;
    IF recibido IS NULL OR facturado+NEW.kilos_facturados>recibido+0.01 THEN RAISE EXCEPTION 'Las facturas superan los kilos recibidos de la carga'; END IF;
    tiene_movimientos := EXISTS(SELECT 1 FROM cobro_venta WHERE factura_venta_id=NEW.factura_venta_id);
    IF TG_OP='UPDATE' AND tiene_movimientos AND
      (NEW.carga_id,NEW.kilos_facturados,NEW.precio_kg_aplicado,NEW.descuento,NEW.cargos,NEW.importe_venta,NEW.moneda)
      IS DISTINCT FROM (OLD.carga_id,OLD.kilos_facturados,OLD.precio_kg_aplicado,OLD.descuento,OLD.cargos,OLD.importe_venta,OLD.moneda) THEN RAISE EXCEPTION 'Conserva los importes y origen de la factura cobrada'; END IF;
  ELSIF TG_TABLE_NAME='liquidacion_proveedor' THEN
    tiene_movimientos := EXISTS(SELECT 1 FROM pago_proveedor WHERE liquidacion_proveedor_id=NEW.liquidacion_proveedor_id);
    IF TG_OP='UPDATE' AND tiene_movimientos AND
      (NEW.carga_id,NEW.proveedor_id,NEW.persona_liquidacion_id,NEW.persona_snapshot,NEW.kilos_reconocidos,NEW.precio_kg_aplicado,NEW.importe_compra)
      IS DISTINCT FROM (OLD.carga_id,OLD.proveedor_id,OLD.persona_liquidacion_id,OLD.persona_snapshot,OLD.kilos_reconocidos,OLD.precio_kg_aplicado,OLD.importe_compra) THEN RAISE EXCEPTION 'Conserva el documento de compra con pagos'; END IF;
  ELSE
    tiene_movimientos := EXISTS(SELECT 1 FROM pago_transporte WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id)
      OR EXISTS(SELECT 1 FROM aplicacion_adelanto WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id);
    IF TG_OP='UPDATE' AND tiene_movimientos AND (NEW.carga_id,NEW.flete) IS DISTINCT FROM (OLD.carga_id,OLD.flete) THEN RAISE EXCEPTION 'Conserva el flete liquidado con movimientos'; END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER trg_documento_venta BEFORE INSERT OR UPDATE ON factura_venta FOR EACH ROW EXECUTE FUNCTION proteger_documento_financiero();
CREATE TRIGGER trg_documento_compra BEFORE UPDATE ON liquidacion_proveedor FOR EACH ROW EXECUTE FUNCTION proteger_documento_financiero();
CREATE TRIGGER trg_documento_transporte BEFORE UPDATE ON liquidacion_transporte FOR EACH ROW EXECUTE FUNCTION proteger_documento_financiero();

CREATE FUNCTION validar_movimiento_financiero() RETURNS trigger
LANGUAGE plpgsql SET search_path = agro, pg_temp AS $$
DECLARE limite numeric; usado numeric; credito numeric; acuerdo_adelanto integer; acuerdo_carga integer;
BEGIN
  IF TG_TABLE_NAME='pago_proveedor' THEN
    IF TG_OP='UPDATE' AND NEW.liquidacion_proveedor_id<>OLD.liquidacion_proveedor_id THEN RAISE EXCEPTION 'Conserva el documento del pago'; END IF;
    SELECT importe_compra INTO limite FROM liquidacion_proveedor WHERE liquidacion_proveedor_id=NEW.liquidacion_proveedor_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pago_proveedor WHERE liquidacion_proveedor_id=NEW.liquidacion_proveedor_id AND pago_proveedor_id<>NEW.pago_proveedor_id;
  ELSIF TG_TABLE_NAME='cobro_venta' THEN
    IF TG_OP='UPDATE' AND NEW.factura_venta_id<>OLD.factura_venta_id THEN RAISE EXCEPTION 'Conserva el documento del cobro'; END IF;
    SELECT importe_venta INTO limite FROM factura_venta WHERE factura_venta_id=NEW.factura_venta_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM cobro_venta WHERE factura_venta_id=NEW.factura_venta_id AND cobro_venta_id<>NEW.cobro_venta_id;
  ELSIF TG_TABLE_NAME='pago_certificado_campana' THEN
    IF TG_OP='UPDATE' AND NEW.certificado_id<>OLD.certificado_id THEN RAISE EXCEPTION 'Conserva el certificado del pago'; END IF;
    SELECT costo INTO limite FROM certificado_campana WHERE certificado_id=NEW.certificado_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pago_certificado_campana WHERE certificado_id=NEW.certificado_id AND pago_certificado_campana_id<>NEW.pago_certificado_campana_id;
  ELSE
    IF TG_OP='UPDATE' AND NEW.liquidacion_transporte_id<>OLD.liquidacion_transporte_id THEN RAISE EXCEPTION 'Conserva la liquidación del movimiento'; END IF;
    IF TG_TABLE_NAME='aplicacion_adelanto' THEN
      IF TG_OP='UPDATE' AND NEW.adelanto_transporte_id<>OLD.adelanto_transporte_id THEN RAISE EXCEPTION 'Conserva el origen del adelanto'; END IF;
      SELECT monto,acuerdo_transporte_id INTO credito,acuerdo_adelanto FROM adelanto_transporte WHERE adelanto_transporte_id=NEW.adelanto_transporte_id FOR UPDATE;
      SELECT coalesce(sum(monto),0) INTO usado FROM aplicacion_adelanto WHERE adelanto_transporte_id=NEW.adelanto_transporte_id AND aplicacion_adelanto_id<>NEW.aplicacion_adelanto_id;
      IF credito IS NULL OR usado+NEW.monto>credito THEN RAISE EXCEPTION 'El adelanto aplicado supera el disponible'; END IF;
      SELECT co.acuerdo_transporte_id INTO acuerdo_carga FROM liquidacion_transporte l JOIN carga c ON c.carga_id=l.carga_id
        JOIN coordinacion_entrega co ON co.coordinacion_entrega_id=c.coordinacion_entrega_id WHERE l.liquidacion_transporte_id=NEW.liquidacion_transporte_id;
      IF acuerdo_carga IS DISTINCT FROM acuerdo_adelanto THEN RAISE EXCEPTION 'Adelanto de otra empresa o campaña'; END IF;
    END IF;
    SELECT flete INTO limite FROM liquidacion_transporte WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id FOR UPDATE;
    limite := limite + coalesce((SELECT sum(g.monto) FROM gasto_transporte g JOIN liquidacion_transporte l ON l.carga_id=g.carga_id WHERE l.liquidacion_transporte_id=NEW.liquidacion_transporte_id AND g.incluido_en_liquidacion),0);
    IF TG_TABLE_NAME='pago_transporte' THEN
      SELECT coalesce(sum(monto),0) INTO usado FROM pago_transporte WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id AND pago_transporte_id<>NEW.pago_transporte_id;
      usado := usado + coalesce((SELECT sum(monto) FROM aplicacion_adelanto WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id),0);
    ELSE
      SELECT coalesce(sum(monto),0) INTO usado FROM aplicacion_adelanto WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id AND aplicacion_adelanto_id<>NEW.aplicacion_adelanto_id;
      usado := usado + coalesce((SELECT sum(monto) FROM pago_transporte WHERE liquidacion_transporte_id=NEW.liquidacion_transporte_id),0);
    END IF;
  END IF;
  IF limite IS NULL OR usado+NEW.monto>limite THEN RAISE EXCEPTION 'El movimiento supera el saldo del documento'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER trg_pago_proveedor BEFORE INSERT OR UPDATE ON pago_proveedor FOR EACH ROW EXECUTE FUNCTION validar_movimiento_financiero();
CREATE TRIGGER trg_pago_transporte BEFORE INSERT OR UPDATE ON pago_transporte FOR EACH ROW EXECUTE FUNCTION validar_movimiento_financiero();
CREATE TRIGGER trg_cobro_venta BEFORE INSERT OR UPDATE ON cobro_venta FOR EACH ROW EXECUTE FUNCTION validar_movimiento_financiero();
CREATE TRIGGER trg_pago_certificado BEFORE INSERT OR UPDATE ON pago_certificado_campana FOR EACH ROW EXECUTE FUNCTION validar_movimiento_financiero();
CREATE TRIGGER trg_aplicacion_adelanto BEFORE INSERT OR UPDATE ON aplicacion_adelanto FOR EACH ROW EXECUTE FUNCTION validar_movimiento_financiero();

CREATE FUNCTION validar_desembolso_adelanto() RETURNS trigger
LANGUAGE plpgsql SET search_path = agro, pg_temp AS $$
DECLARE previsto numeric; usado numeric; tipo text;
BEGIN
  IF TG_OP='UPDATE' AND EXISTS(SELECT 1 FROM aplicacion_adelanto WHERE adelanto_transporte_id=OLD.adelanto_transporte_id)
    AND (NEW.monto,NEW.acuerdo_transporte_id) IS DISTINCT FROM (OLD.monto,OLD.acuerdo_transporte_id) THEN
    RAISE EXCEPTION 'Conserva el adelanto ya aplicado';
  END IF;
  SELECT adelanto_acordado,tipo_pago INTO previsto,tipo FROM acuerdo_transporte WHERE acuerdo_transporte_id=NEW.acuerdo_transporte_id FOR UPDATE;
  SELECT coalesce(sum(monto),0) INTO usado FROM adelanto_transporte WHERE acuerdo_transporte_id=NEW.acuerdo_transporte_id AND adelanto_transporte_id<>NEW.adelanto_transporte_id;
  IF tipo IS DISTINCT FROM 'CON_ADELANTO' OR usado+NEW.monto>previsto THEN RAISE EXCEPTION 'El desembolso supera el adelanto acordado'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER trg_desembolso_adelanto BEFORE INSERT OR UPDATE ON adelanto_transporte FOR EACH ROW EXECUTE FUNCTION validar_desembolso_adelanto();

-- La vista anual conserva el parámetro aplicado al documento, no revaloriza el pasado.
CREATE OR REPLACE VIEW v_control_uit AS
SELECT l.persona_liquidacion_id, extract(year FROM l.fecha)::integer AS anio, sum(l.importe_compra) AS acumulado,
l.valor_uit_aplicado AS valor,l.limite_uit_aplicado AS limite_uit,
l.valor_uit_aplicado*l.limite_uit_aplicado-sum(l.importe_compra) AS disponible
FROM liquidacion_proveedor l GROUP BY l.persona_liquidacion_id,extract(year FROM l.fecha)::integer,l.valor_uit_aplicado,l.limite_uit_aplicado;
