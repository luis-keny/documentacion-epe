-- Nombres alineados con las entidades locales; columnas y relaciones representan el MODELO OBJETIVO.
-- No es una migración ni un reemplazo compatible con las entidades TypeORM actuales.
-- AGRO EXPORTACIONES | modelo propuesto tras inspección del prototipo, 25/10/2026 (Lima).

-- PostgreSQL. Instalación NUEVA en schema agro. No es una migración del sistema desplegado.

-- No elimina ni reemplaza objetos existentes. Si agro ya existe, se aborta.

-- Los valores UIT no se precargan: configurar después de validar el parámetro aplicable.

BEGIN;

CREATE SCHEMA agro;

SET LOCAL search_path = agro, public;

-- Identidad única de productores, familiares y conductores.

CREATE TABLE persona (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tipo_documento varchar(20) NOT NULL,
  numero_documento varchar(30) NOT NULL,
  nombres varchar(120) NOT NULL,
  apellidos varchar(120) NOT NULL,
  telefono varchar(30),
  correo varchar(180),
  documento_archivo_id bigint,
  UNIQUE (tipo_documento, numero_documento)
);

-- Perfiles de acceso; los permisos efectivos se aplican en el servidor.

CREATE TABLE rol (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(40) NOT NULL,
  UNIQUE (nombre)
);

-- Cuenta asociada a una persona; no se crea una cuenta por cada participación comercial.

CREATE TABLE usuario (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  persona_id bigint NOT NULL,
  rol_id bigint NOT NULL,
  usuario varchar(80) NOT NULL,
  password_hash text NOT NULL,
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (persona_id),
  UNIQUE (usuario)
);

-- Metadatos del objeto almacenado; la base no almacena URLs firmadas ni el binario.

CREATE TABLE archivo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(255) NOT NULL,
  ruta_storage text NOT NULL,
  tipo_mime varchar(100) NOT NULL,
  bytes bigint NOT NULL,
  sha256 varchar(64),
  subido_por bigint,
  fecha_subida timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ruta_storage),
  CHECK (bytes > 0)
);

-- Propuesta técnica para persistir sesiones; solo se conserva el hash del token.

CREATE TABLE sesion_usuario (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  usuario_id bigint NOT NULL,
  token_hash text NOT NULL,
  creada_at timestamptz NOT NULL DEFAULT now(),
  expira_at timestamptz NOT NULL,
  revocada_at timestamptz,
  UNIQUE (token_hash),
  CHECK (expira_at > creada_at)
);

-- Parámetros anuales configurables del prototipo, sin afirmar vigencia tributaria.

CREATE TABLE parametro_uit (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  anio integer NOT NULL,
  valor numeric(14,2) NOT NULL,
  limite_uit numeric(10,2) NOT NULL,
  umbral_alerta numeric(5,4) NOT NULL DEFAULT 0.90,
  UNIQUE (anio),
  CHECK (valor > 0),
  CHECK (limite_uit > 0),
  CHECK (umbral_alerta > 0 AND umbral_alerta <= 1)
);

-- Catálogo de frutas.

CREATE TABLE fruta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(80) NOT NULL,
  UNIQUE (nombre)
);

-- Variedades pertenecientes a una fruta.

CREATE TABLE fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  fruta_id bigint NOT NULL,
  nombre varchar(100) NOT NULL,
  UNIQUE (fruta_id, nombre)
);

-- Campaña con sus fechas, responsable y cierre manual.

CREATE TABLE campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(120) NOT NULL,
  fruta_id bigint NOT NULL,
  temporada varchar(30) NOT NULL,
  fecha_inicio date NOT NULL,
  fecha_fin date NOT NULL,
  estado varchar(25) NOT NULL DEFAULT 'PLANIFICADO',
  responsable_id bigint,
  lineamientos_id bigint,
  observaciones text,
  cerrada_at timestamptz,
  cerrada_por bigint,
  motivo_cierre text,
  CHECK (estado IN ('PLANIFICADO','EN_PROCESO','FINALIZADO')),
  CHECK (fecha_fin >= fecha_inicio),
  CHECK ((estado = 'FINALIZADO') = (cerrada_at IS NOT NULL AND cerrada_por IS NOT NULL AND motivo_cierre IS NOT NULL))
);

-- Variedades elegidas para una campaña.

CREATE TABLE campana_x_fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (campania_id, variedad_id)
);

-- Identidad comercial del proveedor principal.

CREATE TABLE proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  persona_principal_id bigint NOT NULL,
  codigo varchar(40) NOT NULL,
  zona varchar(120),
  codigo_produccion varchar(60),
  estado_sanidad varchar(30),
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (persona_principal_id),
  UNIQUE (codigo)
);

-- Personas vinculadas; la relación no transfiere compras históricas.

CREATE TABLE proveedor_x_persona (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  persona_id bigint NOT NULL,
  vinculo varchar(60) NOT NULL,
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (proveedor_id, persona_id)
);

-- Frutas asociadas al padrón general.

CREATE TABLE proveedor_x_fruta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  fruta_id bigint NOT NULL,
  UNIQUE (proveedor_id, fruta_id)
);

-- Variedades asociadas al padrón general.

CREATE TABLE proveedor_x_fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (proveedor_id, variedad_id)
);

-- Datos físicos de cada finca, independientes de la campaña.

CREATE TABLE finca (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  nombre varchar(150) NOT NULL,
  codigo_produccion varchar(60),
  codigo_catastral varchar(60),
  departamento varchar(80) NOT NULL,
  provincia varchar(80) NOT NULL,
  distrito varchar(80) NOT NULL,
  ubigeo varchar(6),
  direccion text,
  codigo_establecimiento varchar(4),
  latitud numeric(10,7),
  longitud numeric(10,7),
  hectareas numeric(12,4) NOT NULL,
  hectareas_cultivo numeric(12,4) NOT NULL,
  variedad_id bigint,
  edad_cultivo_anios numeric(6,2),
  UNIQUE (id, proveedor_id),
  CHECK (hectareas > 0),
  CHECK (hectareas_cultivo >= 0 AND hectareas_cultivo <= hectareas),
  CHECK (ubigeo IS NULL OR ubigeo ~ '^[0-9]{6}$'),
  CHECK (latitud BETWEEN -90 AND 90),
  CHECK (longitud BETWEEN -180 AND 180),
  CHECK ((latitud IS NULL) = (longitud IS NULL))
);

-- Certificados generales del proveedor; distintos del certificado de campaña.

CREATE TABLE certificado_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  nombre varchar(180) NOT NULL,
  fecha_revision date,
  archivo_id bigint NOT NULL
);

-- Vinculación proveedor–campaña; aquí pertenecen rol, oferta y evaluación.

CREATE TABLE participacion_proveedor_campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  proveedor_id bigint NOT NULL,
  rol_comercial varchar(20) NOT NULL,
  tipo_fruta varchar(20) NOT NULL,
  kilos_estimados numeric(14,3) NOT NULL,
  estado varchar(30) NOT NULL DEFAULT 'EXAMEN_PENDIENTE',
  entrevista_aplica boolean NOT NULL DEFAULT true,
  fecha_registro timestamptz NOT NULL DEFAULT now(),
  observaciones text,
  UNIQUE (campania_id, proveedor_id),
  UNIQUE (id, campania_id, proveedor_id),
  CHECK (rol_comercial IN ('PRODUCTOR','ACOPIADOR')),
  CHECK (tipo_fruta IN ('ORGANICA','CONVENCIONAL')),
  CHECK (kilos_estimados >= 0),
  CHECK (estado IN ('EXAMEN_PENDIENTE','ENTREVISTA_PENDIENTE','APROBADO','RECHAZADO'))
);

-- Variedades de la participación, sin deducirlas solo de contratos de compra.

CREATE TABLE participacion_proveedor_x_fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  participacion_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (participacion_id, variedad_id)
);

-- Fincas vinculadas a una participación; permite conservar historial por campaña.

CREATE TABLE campania_x_proveedores (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  participacion_id bigint NOT NULL,
  campania_id bigint NOT NULL,
  proveedor_id bigint NOT NULL,
  finca_id bigint NOT NULL,
  UNIQUE (campania_id, finca_id),
  UNIQUE (id, participacion_id)
);

-- Registro agronómico de cada finca entrevistada en una campaña.

CREATE TABLE entrevista_extencion (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  finca_campania_id bigint NOT NULL,
  codigo_fyv varchar(60) NOT NULL,
  registrada_at timestamptz NOT NULL DEFAULT now(),
  registrada_por bigint,
  densidad_plantacion numeric(12,3),
  distanciamiento_m varchar(60),
  frecuencia_riego varchar(120),
  nombre_aplicacion varchar(180),
  aplicaciones_anio integer,
  resultado text,
  archivo_id bigint,
  CHECK (densidad_plantacion > 0),
  CHECK (aplicaciones_anio >= 0)
);

-- Exámenes sanitarios de la participación, con muestra y fechas de laboratorio.

CREATE TABLE examen_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  participacion_id bigint NOT NULL,
  finca_campania_id bigint,
  tipo varchar(100) NOT NULL,
  codigo_muestra varchar(80),
  origen varchar(180),
  fecha_muestra date NOT NULL,
  fecha_envio date,
  estado varchar(30) NOT NULL DEFAULT 'PENDIENTE',
  resultado varchar(180),
  archivo_id bigint,
  observaciones text,
  CHECK (fecha_envio IS NULL OR fecha_envio >= fecha_muestra)
);

-- Condiciones versionadas por finca, variedad y vigencia; no sustituye la participación.

CREATE TABLE acuerdo_compra (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  finca_campania_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  precio_kg numeric(14,4) NOT NULL,
  kilos_acordados numeric(14,3),
  fecha_inicio date NOT NULL,
  fecha_fin date NOT NULL,
  estado varchar(25) NOT NULL DEFAULT 'VIGENTE',
  CHECK (precio_kg > 0),
  CHECK (kilos_acordados >= 0),
  CHECK (fecha_fin >= fecha_inicio)
);

-- Catálogo de normas de certificación y traslado.

CREATE TABLE norma (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  codigo varchar(40) NOT NULL,
  nombre varchar(180) NOT NULL,
  UNIQUE (codigo)
);

-- Certificado de campaña, costo y organismo; un certificado por campaña según la UI.

CREATE TABLE certificado_campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  norma_id bigint NOT NULL,
  nombre varchar(180) NOT NULL,
  codigo varchar(80),
  organismo varchar(180) NOT NULL,
  fecha_emision date NOT NULL,
  fecha_vencimiento date NOT NULL,
  costo numeric(14,2) NOT NULL,
  moneda varchar(3) NOT NULL,
  archivo_id bigint NOT NULL,
  UNIQUE (campania_id),
  UNIQUE (id, campania_id),
  CHECK (fecha_vencimiento >= fecha_emision),
  CHECK (costo >= 0),
  CHECK (moneda IN ('PEN','USD','EUR'))
);

-- Productores cubiertos y kilos iniciales capturados al certificar.

CREATE TABLE certificado_campana_x_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  certificacion_id bigint NOT NULL,
  campania_id bigint NOT NULL,
  participacion_id bigint NOT NULL,
  proveedor_id bigint NOT NULL,
  kilos_autorizados numeric(14,3) NOT NULL,
  UNIQUE (certificacion_id, participacion_id),
  CHECK (kilos_autorizados > 0)
);

-- Incrementos de cobertura, sin sobrescribir los kilos iniciales.

CREATE TABLE ampliacion_certificado_campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  certificacion_id bigint NOT NULL,
  fecha date NOT NULL,
  kilos_adicionales numeric(14,3) NOT NULL,
  referencia varchar(180) NOT NULL,
  registrado_por bigint,
  CHECK (kilos_adicionales > 0)
);

-- Desembolsos de la certificación en su misma moneda.

CREATE TABLE pago_certificado_campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  certificacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  referencia varchar(100) NOT NULL,
  comprobante_id bigint NOT NULL,
  registrado_por bigint,
  UNIQUE (certificacion_id, referencia),
  CHECK (monto > 0)
);

-- Padrón general del cliente y contacto.

CREATE TABLE cliente_negocio (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  razon_social varchar(180) NOT NULL,
  ruc varchar(11) NOT NULL,
  contacto varchar(180) NOT NULL,
  tipo varchar(20) NOT NULL,
  telefono varchar(30),
  correo varchar(180),
  ubicacion varchar(180),
  fecha_registro date NOT NULL DEFAULT CURRENT_DATE,
  UNIQUE (ruc),
  CHECK (tipo IN ('EXPORTADOR','INDUSTRIA')),
  CHECK (ruc ~ '^[0-9]{11}$')
);

-- Puntos de llegada de cada cliente; no asumir que todos comparten una planta.

CREATE TABLE destino_cliente_negocio (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cliente_id bigint NOT NULL,
  nombre varchar(150) NOT NULL,
  ubigeo varchar(6),
  direccion text,
  codigo_establecimiento varchar(4),
  latitud numeric(10,7),
  longitud numeric(10,7),
  UNIQUE (id, cliente_id),
  CHECK (latitud BETWEEN -90 AND 90),
  CHECK (longitud BETWEEN -180 AND 180),
  CHECK ((latitud IS NULL) = (longitud IS NULL))
);

-- Participación cliente–campaña y necesidad original, previa a sus contratos.

CREATE TABLE cliente_negocio_campana (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  cliente_id bigint NOT NULL,
  cantidad_kg numeric(14,3) NOT NULL,
  fecha_registro date NOT NULL,
  ficha_tecnica_id bigint,
  destino_solicitado varchar(180),
  entrega_desde date,
  entrega_hasta date,
  observaciones text,
  CHECK (cantidad_kg > 0),
  CHECK (entrega_hasta >= entrega_desde)
);

-- Selección múltiple de variedades requeridas.

CREATE TABLE cliente_negocio_campana_x_fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  requerimiento_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (requerimiento_id, variedad_id)
);

-- Varios contratos por requerimiento, con precio y moneda propios.

CREATE TABLE contrato_venta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  requerimiento_id bigint NOT NULL,
  numero varchar(60) NOT NULL,
  canal varchar(20) NOT NULL,
  fecha date NOT NULL,
  kilos_acordados numeric(14,3) NOT NULL,
  precio_kg numeric(14,4) NOT NULL,
  moneda varchar(3) NOT NULL,
  estado varchar(25) NOT NULL DEFAULT 'VIGENTE',
  condiciones_pago text,
  archivo_id bigint,
  UNIQUE (numero),
  CHECK (kilos_acordados > 0),
  CHECK (precio_kg > 0),
  CHECK (canal IN ('EXPORTACION','INDUSTRIA')),
  CHECK (moneda IN ('PEN','USD','EUR'))
);

-- Programación comercial; puede existir antes de asignar transporte.

CREATE TABLE entrega_programada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  contrato_id bigint NOT NULL,
  destino_id bigint NOT NULL,
  fecha date NOT NULL,
  kilos_programados numeric(14,3) NOT NULL,
  observaciones text,
  CHECK (kilos_programados > 0)
);

-- Distribución programada por variedad para el programa semanal.

CREATE TABLE entrega_x_fruta_derivada (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entrega_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  kilos_programados numeric(14,3) NOT NULL,
  UNIQUE (entrega_id, variedad_id),
  CHECK (kilos_programados > 0)
);

-- Nombre heredado del DBML; admite empresas e independientes.

CREATE TABLE empresa_transporte_externo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tipo varchar(20) NOT NULL,
  razon_social varchar(180) NOT NULL,
  tipo_documento varchar(20) NOT NULL,
  numero_documento varchar(30) NOT NULL,
  persona_id bigint,
  registro_mtc varchar(80),
  telefono varchar(30),
  correo varchar(180),
  departamento varchar(80),
  provincia varchar(80),
  ciudad varchar(80),
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (tipo_documento, numero_documento),
  CHECK (tipo IN ('EMPRESA','INDEPENDIENTE')),
  CHECK (tipo <> 'INDEPENDIENTE' OR persona_id IS NOT NULL)
);

-- Unidad de transporte con capacidad y pesos explícitos.

CREATE TABLE vehiculo_externo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  empresa_id bigint NOT NULL,
  placa varchar(15) NOT NULL,
  volumen_m3 numeric(12,3),
  capacidad_kg numeric(14,3) NOT NULL,
  peso_bruto_kg numeric(14,3),
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (placa),
  UNIQUE (id, empresa_id),
  CHECK (capacidad_kg > 0),
  CHECK (volumen_m3 > 0),
  CHECK (peso_bruto_kg >= capacidad_kg)
);

-- Identidad del conductor y vínculo opcional a cuenta de acceso.

CREATE TABLE chofer_transporte_externo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  empresa_id bigint NOT NULL,
  persona_id bigint NOT NULL,
  usuario_id bigint,
  licencia varchar(40) NOT NULL,
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (persona_id),
  UNIQUE (usuario_id),
  UNIQUE (id, empresa_id)
);

-- Solicitud persistida; enviar correos está simulado en el prototipo.

CREATE TABLE solicitud_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  referencia varchar(100) NOT NULL,
  fecha timestamptz NOT NULL DEFAULT now(),
  origen text NOT NULL,
  destino text NOT NULL,
  ventana_servicio varchar(180),
  cantidad_estimada varchar(100),
  caracteristicas_vehiculo text,
  condiciones text,
  limite_respuesta timestamptz,
  mensaje text,
  archivo_id bigint,
  estado varchar(25) NOT NULL DEFAULT 'BORRADOR',
  UNIQUE (referencia)
);

-- Destinatarios por solicitud, con contacto capturado al invitar.

CREATE TABLE invitacion_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  solicitud_id bigint NOT NULL,
  empresa_id bigint NOT NULL,
  correo_snapshot varchar(180),
  estado varchar(25) NOT NULL DEFAULT 'INVITADA',
  UNIQUE (solicitud_id, empresa_id)
);

-- Propuesta de respuesta; atributos no observables por lista vacía se proponen.

CREATE TABLE cotizacion_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  invitacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  moneda varchar(3) NOT NULL,
  condiciones text,
  archivo_id bigint,
  estado varchar(25) NOT NULL DEFAULT 'RECIBIDA',
  CHECK (monto > 0),
  CHECK (moneda IN ('PEN','USD','EUR'))
);

-- Transportista vinculado a campaña y acuerdo de flete autorizado.

CREATE TABLE acuerdo_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  empresa_id bigint NOT NULL,
  cotizacion_id bigint,
  tipo_pago varchar(20) NOT NULL,
  monto_acordado numeric(14,2) NOT NULL,
  fecha_acuerdo date NOT NULL,
  fecha_pago_final date,
  archivo_id bigint,
  UNIQUE (campania_id, empresa_id),
  UNIQUE (id, empresa_id),
  CHECK (monto_acordado > 0),
  CHECK (tipo_pago IN ('INMEDIATO','CON_ADELANTO','AL_FINAL'))
);

-- Asignación previa a la carga real; un registro por entrega.

CREATE TABLE coordinacion_entrega (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entrega_id bigint NOT NULL,
  acuerdo_transporte_id bigint NOT NULL,
  empresa_id bigint NOT NULL,
  vehiculo_id bigint NOT NULL,
  chofer_id bigint NOT NULL,
  inicio_programado timestamptz NOT NULL,
  fin_programado timestamptz NOT NULL,
  origen_descripcion text NOT NULL,
  condiciones_carga text,
  observaciones text,
  UNIQUE (entrega_id),
  UNIQUE (id, entrega_id),
  CHECK (fin_programado >= inicio_programado)
);

-- Selección de varias fincas de varios proveedores antes de cargar.

CREATE TABLE origen_entrega (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  coordinacion_id bigint NOT NULL,
  finca_campania_id bigint NOT NULL,
  UNIQUE (coordinacion_id, finca_campania_id)
);

-- Operación de cosecha de una entrega; estado separado del despacho.

CREATE TABLE cosecha (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entrega_id bigint NOT NULL,
  codigo_lote varchar(60) NOT NULL,
  fecha_prevista date NOT NULL,
  kilos_estimados numeric(14,3) NOT NULL,
  kilos_cosechados numeric(14,3),
  kilos_aceptados numeric(14,3),
  estado varchar(30) NOT NULL DEFAULT 'PENDIENTE',
  cierre_cosecha_at timestamptz,
  evidencia_id bigint,
  UNIQUE (codigo_lote),
  CHECK (kilos_estimados >= 0),
  CHECK (kilos_cosechados >= 0),
  CHECK (kilos_aceptados >= 0)
);

-- Muestreo por operación y finca; no mezclar con exámenes de admisión.

CREATE TABLE analisis_calidad (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cosecha_id bigint NOT NULL,
  finca_campania_id bigint NOT NULL,
  tipo varchar(100) NOT NULL,
  fecha_muestreo date NOT NULL,
  estado varchar(30) NOT NULL DEFAULT 'PENDIENTE',
  resultado_texto varchar(180),
  resultado_numerico numeric(14,4),
  unidad varchar(30),
  archivo_id bigint,
  observaciones text
);

-- Historial de MTD por finca y campaña, con captura de respaldo.

CREATE TABLE medicion_mtd (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  finca_campania_id bigint NOT NULL,
  medido_at timestamptz NOT NULL,
  valor numeric(12,4) NOT NULL,
  limite_aplicado numeric(12,4) NOT NULL,
  archivo_id bigint NOT NULL,
  registrado_por bigint,
  CHECK (valor >= 0),
  CHECK (limite_aplicado >= 0)
);

-- Carga física real de la coordinación; no crea otra asignación de camión o chofer.

CREATE TABLE carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  coordinacion_id bigint NOT NULL,
  codigo varchar(80) NOT NULL,
  fecha_carga date NOT NULL,
  anotador_nombre varchar(180) NOT NULL,
  estado_calidad varchar(30) NOT NULL DEFAULT 'PENDIENTE',
  viaticos_movilidad numeric(14,2) NOT NULL DEFAULT 0,
  viaticos_insumos numeric(14,2) NOT NULL DEFAULT 0,
  guia_salida_id bigint,
  guia_salida_registrada_at timestamptz,
  observaciones text,
  UNIQUE (coordinacion_id),
  UNIQUE (codigo),
  UNIQUE (id, coordinacion_id),
  CHECK (viaticos_movilidad >= 0),
  CHECK (viaticos_insumos >= 0),
  CHECK ((guia_salida_id IS NULL) = (guia_salida_registrada_at IS NULL))
);

-- Kilos reales por proveedor y variedad; la UI no reparte automáticamente por finca.

CREATE TABLE proveedor_carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  participacion_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  kilos_cargados numeric(14,3) NOT NULL,
  precio_compra_kg_aplicado numeric(14,4),
  jabas_cargadas integer NOT NULL DEFAULT 0,
  jabas_vacias integer NOT NULL DEFAULT 0,
  bines_cargados integer NOT NULL DEFAULT 0,
  bines_vacios integer NOT NULL DEFAULT 0,
  mallas_cargadas integer NOT NULL DEFAULT 0,
  mallas_vacias integer NOT NULL DEFAULT 0,
  UNIQUE (carga_id, participacion_id, variedad_id),
  UNIQUE (id, carga_id),
  CHECK (kilos_cargados > 0),
  CHECK (precio_compra_kg_aplicado > 0),
  CHECK (jabas_cargadas >= 0),
  CHECK (jabas_vacias >= 0),
  CHECK (bines_cargados >= 0),
  CHECK (bines_vacios >= 0),
  CHECK (mallas_cargadas >= 0),
  CHECK (mallas_vacias >= 0)
);

-- Trazabilidad a fincas seleccionadas; asignación de kg opcional hasta medirla.

CREATE TABLE origen_carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_carga_id bigint NOT NULL,
  finca_campania_id bigint NOT NULL,
  kilos_origen numeric(14,3),
  UNIQUE (proveedor_carga_id, finca_campania_id),
  CHECK (kilos_origen > 0)
);

-- Cuadrilla, anotadores y otros costos de carga; no son automáticamente gasto de transporte.

CREATE TABLE gasto_carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  concepto varchar(150) NOT NULL,
  monto numeric(14,2) NOT NULL,
  UNIQUE (carga_id, concepto),
  CHECK (monto >= 0)
);

-- Documento de traslado y captura histórica de origen, destino y transportista.

CREATE TABLE guia_remision (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  numero varchar(30) NOT NULL,
  fecha_inicio_traslado date NOT NULL,
  fecha_entrega_transportista date,
  peso_bruto_kg numeric(14,3) NOT NULL,
  unidad_peso varchar(3) NOT NULL DEFAULT 'KGM',
  numero_bultos integer NOT NULL,
  finca_partida_id bigint NOT NULL,
  destino_id bigint NOT NULL,
  ubigeo_partida_snapshot varchar(6) NOT NULL,
  direccion_partida_snapshot text NOT NULL,
  establecimiento_partida_snapshot varchar(4) NOT NULL,
  ubigeo_llegada_snapshot varchar(6) NOT NULL,
  direccion_llegada_snapshot text NOT NULL,
  establecimiento_llegada_snapshot varchar(4) NOT NULL,
  transportista_documento_snapshot varchar(30) NOT NULL,
  mtc_snapshot varchar(80),
  placa_snapshot varchar(15) NOT NULL,
  conductor_documento_snapshot varchar(30) NOT NULL,
  conductor_nombre_snapshot varchar(180) NOT NULL,
  conductor_licencia_snapshot varchar(40) NOT NULL,
  archivo_id bigint,
  observaciones text,
  UNIQUE (numero),
  UNIQUE (id, carga_id),
  CHECK (peso_bruto_kg > 0),
  CHECK (numero_bultos > 0),
  CHECK (unidad_peso = 'KGM')
);

-- Distribución de kilos de una carga entre sus guías, sin duplicarlos.

CREATE TABLE proveedor_guia (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  guia_id bigint NOT NULL,
  carga_id bigint NOT NULL,
  proveedor_carga_id bigint NOT NULL,
  kilos_asignados numeric(14,3) NOT NULL,
  UNIQUE (guia_id, proveedor_carga_id),
  CHECK (kilos_asignados > 0)
);

-- Selección múltiple de normas en la guía.

CREATE TABLE guia_x_norma (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  guia_id bigint NOT NULL,
  norma_id bigint NOT NULL,
  UNIQUE (guia_id, norma_id)
);

-- Eventos ordenados del despacho; el estado vigente se deriva del último evento.

CREATE TABLE historial_chofer (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  coordinacion_id bigint NOT NULL,
  carga_id bigint,
  chofer_id bigint NOT NULL,
  estado varchar(25) NOT NULL,
  fecha_hora timestamptz NOT NULL DEFAULT now(),
  observacion text,
  UNIQUE (coordinacion_id, estado),
  CHECK (estado IN ('EN_CARGA','SALIDA','EN_CAMINO','LLEGADA','CIERRE'))
);

-- Recepción única con checklist, peso, descarte y cierre físico/administrativo.

CREATE TABLE recepcion_planta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  chofer_id bigint NOT NULL,
  fecha_recepcion timestamptz,
  peso_planta_kg numeric(14,3),
  hubo_descarte boolean,
  descarte_kg numeric(14,3),
  evidencia_descarte_id bigint,
  reporte_recepcion_id bigint,
  resultado varchar(80),
  recepcion_confirmada_at timestamptz,
  descarte_confirmado_at timestamptz,
  jabas_devueltas integer,
  jabas_devolucion_at timestamptz,
  descarga_at timestamptz,
  cierre_fisico_at timestamptz,
  cierre_administrativo_at timestamptz,
  observaciones text,
  UNIQUE (carga_id),
  CHECK (peso_planta_kg > 0),
  CHECK (descarte_kg >= 0),
  CHECK (jabas_devueltas >= 0),
  CHECK (hubo_descarte IS DISTINCT FROM false OR descarte_kg = 0),
  CHECK (hubo_descarte IS DISTINCT FROM true OR (descarte_kg > 0 AND evidencia_descarte_id IS NOT NULL))
);

-- Documento por carga y proveedor, con persona receptora e importe histórico.

CREATE TABLE liquidacion_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  proveedor_id bigint NOT NULL,
  persona_liquidacion_id bigint NOT NULL,
  numero varchar(40) NOT NULL,
  fecha date NOT NULL,
  importe_compra numeric(14,2) NOT NULL,
  valor_uit_aplicado numeric(14,2) NOT NULL,
  registrado_por bigint NOT NULL,
  archivo_id bigint,
  observaciones text,
  UNIQUE (carga_id, proveedor_id),
  UNIQUE (numero),
  CHECK (importe_compra > 0),
  CHECK (valor_uit_aplicado > 0)
);

-- Documento por carga; flete ingresado al liquidar y gastos separados.

CREATE TABLE liquidacion_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  numero varchar(40) NOT NULL,
  fecha date NOT NULL,
  flete numeric(14,2) NOT NULL,
  registrado_por bigint NOT NULL,
  archivo_id bigint,
  UNIQUE (carga_id),
  UNIQUE (numero),
  CHECK (flete >= 0)
);

-- Gastos reales o viáticos aplicados una sola vez a la liquidación.

CREATE TABLE gasto_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  concepto varchar(150) NOT NULL,
  monto numeric(14,2) NOT NULL,
  origen varchar(20) NOT NULL,
  incluido_en_liquidacion boolean NOT NULL DEFAULT false,
  UNIQUE (carga_id, concepto),
  CHECK (monto >= 0),
  CHECK (origen IN ('VIATICO','REAL'))
);

-- Dinero entregado a la empresa antes de aplicarse a una carga.

CREATE TABLE adelanto_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  acuerdo_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  referencia varchar(100) NOT NULL,
  comprobante_id bigint NOT NULL,
  UNIQUE (acuerdo_id, referencia),
  CHECK (monto > 0)
);

-- Aplicación de un adelanto existente; no representa otro desembolso.

CREATE TABLE aplicacion_adelanto (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  adelanto_id bigint NOT NULL,
  liquidacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  UNIQUE (adelanto_id, liquidacion_id),
  CHECK (monto > 0)
);

-- Preparación y factura externa en una fila; preserva peso, precio y moneda facturados.

CREATE TABLE factura_venta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  referencia_preparacion varchar(40) NOT NULL,
  fecha_preparacion date NOT NULL,
  estado varchar(25) NOT NULL DEFAULT 'PREPARADA',
  numero_factura varchar(80),
  fecha_emision date,
  fecha_vencimiento date,
  kilos_facturados numeric(14,3) NOT NULL,
  precio_kg_aplicado numeric(14,4) NOT NULL,
  moneda varchar(3) NOT NULL,
  importe_venta numeric(14,2) NOT NULL,
  archivo_id bigint,
  UNIQUE (carga_id),
  UNIQUE (referencia_preparacion),
  UNIQUE (numero_factura),
  CHECK (kilos_facturados > 0),
  CHECK (precio_kg_aplicado > 0),
  CHECK (importe_venta = round(kilos_facturados * precio_kg_aplicado, 2)),
  CHECK (estado IN ('PREPARADA','EMITIDA')),
  CHECK (moneda IN ('PEN','USD','EUR')),
  CHECK (estado <> 'EMITIDA' OR (numero_factura IS NOT NULL AND fecha_emision IS NOT NULL AND archivo_id IS NOT NULL)),
  CHECK (fecha_vencimiento >= fecha_emision)
);

-- Pagos parciales de compras en PEN.

CREATE TABLE pago_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  liquidacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  medio varchar(30) NOT NULL,
  referencia varchar(100) NOT NULL,
  comprobante_id bigint NOT NULL,
  registrado_por bigint,
  UNIQUE (liquidacion_id, referencia),
  CHECK (monto > 0)
);

-- Desembolsos de transporte, distintos de aplicar adelantos.

CREATE TABLE pago_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  liquidacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  medio varchar(30) NOT NULL,
  referencia varchar(100) NOT NULL,
  comprobante_id bigint NOT NULL,
  registrado_por bigint,
  UNIQUE (liquidacion_id, referencia),
  CHECK (monto > 0)
);

-- Cobros parciales en la moneda de la factura.

CREATE TABLE cobro_venta (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  factura_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  medio varchar(30) NOT NULL,
  referencia varchar(100) NOT NULL,
  comprobante_id bigint NOT NULL,
  registrado_por bigint,
  UNIQUE (factura_id, referencia),
  CHECK (monto > 0)
);

ALTER TABLE pago_proveedor ADD CONSTRAINT fk_pagos_proveedor_1 FOREIGN KEY (liquidacion_id) REFERENCES liquidacion_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE pago_transporte ADD CONSTRAINT fk_pagos_transporte_2 FOREIGN KEY (liquidacion_id) REFERENCES liquidacion_transporte (id) ON DELETE RESTRICT;

ALTER TABLE cobro_venta ADD CONSTRAINT fk_cobros_venta_3 FOREIGN KEY (factura_id) REFERENCES factura_venta (id) ON DELETE RESTRICT;

ALTER TABLE persona ADD CONSTRAINT fk_personas_4 FOREIGN KEY (documento_archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE usuario ADD CONSTRAINT fk_usuarios_5 FOREIGN KEY (persona_id) REFERENCES persona (id) ON DELETE RESTRICT;

ALTER TABLE usuario ADD CONSTRAINT fk_usuarios_6 FOREIGN KEY (rol_id) REFERENCES rol (id) ON DELETE RESTRICT;

ALTER TABLE archivo ADD CONSTRAINT fk_archivos_7 FOREIGN KEY (subido_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE sesion_usuario ADD CONSTRAINT fk_sesiones_usuario_8 FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE fruta_derivada ADD CONSTRAINT fk_variedades_9 FOREIGN KEY (fruta_id) REFERENCES fruta (id) ON DELETE RESTRICT;

ALTER TABLE campana ADD CONSTRAINT fk_campanias_10 FOREIGN KEY (fruta_id) REFERENCES fruta (id) ON DELETE RESTRICT;

ALTER TABLE campana ADD CONSTRAINT fk_campanias_11 FOREIGN KEY (responsable_id) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE campana ADD CONSTRAINT fk_campanias_12 FOREIGN KEY (lineamientos_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE campana ADD CONSTRAINT fk_campanias_13 FOREIGN KEY (cerrada_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE campana_x_fruta_derivada ADD CONSTRAINT fk_campania_variedades_14 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE campana_x_fruta_derivada ADD CONSTRAINT fk_campania_variedades_15 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE proveedor ADD CONSTRAINT fk_proveedores_16 FOREIGN KEY (persona_principal_id) REFERENCES persona (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_persona ADD CONSTRAINT fk_personas_proveedor_17 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_persona ADD CONSTRAINT fk_personas_proveedor_18 FOREIGN KEY (persona_id) REFERENCES persona (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_fruta ADD CONSTRAINT fk_proveedor_frutas_19 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_fruta ADD CONSTRAINT fk_proveedor_frutas_20 FOREIGN KEY (fruta_id) REFERENCES fruta (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_fruta_derivada ADD CONSTRAINT fk_proveedor_variedades_21 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_x_fruta_derivada ADD CONSTRAINT fk_proveedor_variedades_22 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE finca ADD CONSTRAINT fk_fincas_23 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE finca ADD CONSTRAINT fk_fincas_24 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE certificado_proveedor ADD CONSTRAINT fk_certificados_propios_25 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE certificado_proveedor ADD CONSTRAINT fk_certificados_propios_26 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE participacion_proveedor_campana ADD CONSTRAINT fk_participaciones_proveedor_27 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE participacion_proveedor_campana ADD CONSTRAINT fk_participaciones_proveedor_28 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE participacion_proveedor_x_fruta_derivada ADD CONSTRAINT fk_participacion_variedades_29 FOREIGN KEY (participacion_id) REFERENCES participacion_proveedor_campana (id) ON DELETE RESTRICT;

ALTER TABLE participacion_proveedor_x_fruta_derivada ADD CONSTRAINT fk_participacion_variedades_30 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_31 FOREIGN KEY (participacion_id) REFERENCES participacion_proveedor_campana (id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_32 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_33 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_34 FOREIGN KEY (finca_id) REFERENCES finca (id) ON DELETE RESTRICT;

ALTER TABLE entrevista_extencion ADD CONSTRAINT fk_entrevistas_35 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE entrevista_extencion ADD CONSTRAINT fk_entrevistas_36 FOREIGN KEY (registrada_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE entrevista_extencion ADD CONSTRAINT fk_entrevistas_37 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE examen_proveedor ADD CONSTRAINT fk_examenes_38 FOREIGN KEY (participacion_id) REFERENCES participacion_proveedor_campana (id) ON DELETE RESTRICT;

ALTER TABLE examen_proveedor ADD CONSTRAINT fk_examenes_39 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE examen_proveedor ADD CONSTRAINT fk_examenes_40 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_compra ADD CONSTRAINT fk_acuerdos_compra_41 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_compra ADD CONSTRAINT fk_acuerdos_compra_42 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana ADD CONSTRAINT fk_certificaciones_43 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana ADD CONSTRAINT fk_certificaciones_44 FOREIGN KEY (norma_id) REFERENCES norma (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana ADD CONSTRAINT fk_certificaciones_45 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_46 FOREIGN KEY (certificacion_id) REFERENCES certificado_campana (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_47 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_48 FOREIGN KEY (participacion_id) REFERENCES participacion_proveedor_campana (id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_49 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE ampliacion_certificado_campana ADD CONSTRAINT fk_ampliaciones_certificacion_50 FOREIGN KEY (certificacion_id) REFERENCES certificado_campana (id) ON DELETE RESTRICT;

ALTER TABLE ampliacion_certificado_campana ADD CONSTRAINT fk_ampliaciones_certificacion_51 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE pago_certificado_campana ADD CONSTRAINT fk_pagos_certificacion_52 FOREIGN KEY (certificacion_id) REFERENCES certificado_campana (id) ON DELETE RESTRICT;

ALTER TABLE pago_certificado_campana ADD CONSTRAINT fk_pagos_certificacion_53 FOREIGN KEY (comprobante_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE pago_certificado_campana ADD CONSTRAINT fk_pagos_certificacion_54 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE destino_cliente_negocio ADD CONSTRAINT fk_destinos_cliente_55 FOREIGN KEY (cliente_id) REFERENCES cliente_negocio (id) ON DELETE RESTRICT;

ALTER TABLE cliente_negocio_campana ADD CONSTRAINT fk_requerimientos_comerciales_56 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE cliente_negocio_campana ADD CONSTRAINT fk_requerimientos_comerciales_57 FOREIGN KEY (cliente_id) REFERENCES cliente_negocio (id) ON DELETE RESTRICT;

ALTER TABLE cliente_negocio_campana ADD CONSTRAINT fk_requerimientos_comerciales_58 FOREIGN KEY (ficha_tecnica_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE cliente_negocio_campana_x_fruta_derivada ADD CONSTRAINT fk_requerimiento_variedades_59 FOREIGN KEY (requerimiento_id) REFERENCES cliente_negocio_campana (id) ON DELETE RESTRICT;

ALTER TABLE cliente_negocio_campana_x_fruta_derivada ADD CONSTRAINT fk_requerimiento_variedades_60 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE contrato_venta ADD CONSTRAINT fk_contratos_venta_61 FOREIGN KEY (requerimiento_id) REFERENCES cliente_negocio_campana (id) ON DELETE RESTRICT;

ALTER TABLE contrato_venta ADD CONSTRAINT fk_contratos_venta_62 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE entrega_programada ADD CONSTRAINT fk_entregas_programadas_63 FOREIGN KEY (contrato_id) REFERENCES contrato_venta (id) ON DELETE RESTRICT;

ALTER TABLE entrega_programada ADD CONSTRAINT fk_entregas_programadas_64 FOREIGN KEY (destino_id) REFERENCES destino_cliente_negocio (id) ON DELETE RESTRICT;

ALTER TABLE entrega_x_fruta_derivada ADD CONSTRAINT fk_entrega_variedades_65 FOREIGN KEY (entrega_id) REFERENCES entrega_programada (id) ON DELETE RESTRICT;

ALTER TABLE entrega_x_fruta_derivada ADD CONSTRAINT fk_entrega_variedades_66 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE empresa_transporte_externo ADD CONSTRAINT fk_empresas_transporte_67 FOREIGN KEY (persona_id) REFERENCES persona (id) ON DELETE RESTRICT;

ALTER TABLE vehiculo_externo ADD CONSTRAINT fk_vehiculos_68 FOREIGN KEY (empresa_id) REFERENCES empresa_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE chofer_transporte_externo ADD CONSTRAINT fk_choferes_69 FOREIGN KEY (empresa_id) REFERENCES empresa_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE chofer_transporte_externo ADD CONSTRAINT fk_choferes_70 FOREIGN KEY (persona_id) REFERENCES persona (id) ON DELETE RESTRICT;

ALTER TABLE chofer_transporte_externo ADD CONSTRAINT fk_choferes_71 FOREIGN KEY (usuario_id) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE solicitud_transporte ADD CONSTRAINT fk_solicitudes_transporte_72 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE solicitud_transporte ADD CONSTRAINT fk_solicitudes_transporte_73 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE invitacion_transporte ADD CONSTRAINT fk_invitaciones_transporte_74 FOREIGN KEY (solicitud_id) REFERENCES solicitud_transporte (id) ON DELETE RESTRICT;

ALTER TABLE invitacion_transporte ADD CONSTRAINT fk_invitaciones_transporte_75 FOREIGN KEY (empresa_id) REFERENCES empresa_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE cotizacion_transporte ADD CONSTRAINT fk_cotizaciones_transporte_76 FOREIGN KEY (invitacion_id) REFERENCES invitacion_transporte (id) ON DELETE RESTRICT;

ALTER TABLE cotizacion_transporte ADD CONSTRAINT fk_cotizaciones_transporte_77 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_transporte ADD CONSTRAINT fk_acuerdos_transporte_78 FOREIGN KEY (campania_id) REFERENCES campana (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_transporte ADD CONSTRAINT fk_acuerdos_transporte_79 FOREIGN KEY (empresa_id) REFERENCES empresa_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_transporte ADD CONSTRAINT fk_acuerdos_transporte_80 FOREIGN KEY (cotizacion_id) REFERENCES cotizacion_transporte (id) ON DELETE RESTRICT;

ALTER TABLE acuerdo_transporte ADD CONSTRAINT fk_acuerdos_transporte_81 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_82 FOREIGN KEY (entrega_id) REFERENCES entrega_programada (id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_83 FOREIGN KEY (acuerdo_transporte_id) REFERENCES acuerdo_transporte (id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_84 FOREIGN KEY (empresa_id) REFERENCES empresa_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_85 FOREIGN KEY (chofer_id) REFERENCES chofer_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE origen_entrega ADD CONSTRAINT fk_origenes_entrega_86 FOREIGN KEY (coordinacion_id) REFERENCES coordinacion_entrega (id) ON DELETE RESTRICT;

ALTER TABLE origen_entrega ADD CONSTRAINT fk_origenes_entrega_87 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE cosecha ADD CONSTRAINT fk_cosechas_88 FOREIGN KEY (entrega_id) REFERENCES entrega_programada (id) ON DELETE RESTRICT;

ALTER TABLE cosecha ADD CONSTRAINT fk_cosechas_89 FOREIGN KEY (evidencia_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_90 FOREIGN KEY (cosecha_id) REFERENCES cosecha (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_91 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_92 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE medicion_mtd ADD CONSTRAINT fk_mediciones_mtd_93 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE medicion_mtd ADD CONSTRAINT fk_mediciones_mtd_94 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE medicion_mtd ADD CONSTRAINT fk_mediciones_mtd_95 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE carga ADD CONSTRAINT fk_cargas_96 FOREIGN KEY (coordinacion_id) REFERENCES coordinacion_entrega (id) ON DELETE RESTRICT;

ALTER TABLE carga ADD CONSTRAINT fk_cargas_97 FOREIGN KEY (guia_salida_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_carga ADD CONSTRAINT fk_proveedores_carga_98 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_carga ADD CONSTRAINT fk_proveedores_carga_99 FOREIGN KEY (participacion_id) REFERENCES participacion_proveedor_campana (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_carga ADD CONSTRAINT fk_proveedores_carga_100 FOREIGN KEY (variedad_id) REFERENCES fruta_derivada (id) ON DELETE RESTRICT;

ALTER TABLE origen_carga ADD CONSTRAINT fk_origenes_carga_101 FOREIGN KEY (proveedor_carga_id) REFERENCES proveedor_carga (id) ON DELETE RESTRICT;

ALTER TABLE origen_carga ADD CONSTRAINT fk_origenes_carga_102 FOREIGN KEY (finca_campania_id) REFERENCES campania_x_proveedores (id) ON DELETE RESTRICT;

ALTER TABLE gasto_carga ADD CONSTRAINT fk_gastos_carga_103 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE guia_remision ADD CONSTRAINT fk_guias_remision_104 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE guia_remision ADD CONSTRAINT fk_guias_remision_105 FOREIGN KEY (finca_partida_id) REFERENCES finca (id) ON DELETE RESTRICT;

ALTER TABLE guia_remision ADD CONSTRAINT fk_guias_remision_106 FOREIGN KEY (destino_id) REFERENCES destino_cliente_negocio (id) ON DELETE RESTRICT;

ALTER TABLE guia_remision ADD CONSTRAINT fk_guias_remision_107 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_guia ADD CONSTRAINT fk_proveedores_guia_108 FOREIGN KEY (guia_id) REFERENCES guia_remision (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_guia ADD CONSTRAINT fk_proveedores_guia_109 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_guia ADD CONSTRAINT fk_proveedores_guia_110 FOREIGN KEY (proveedor_carga_id) REFERENCES proveedor_carga (id) ON DELETE RESTRICT;

ALTER TABLE guia_x_norma ADD CONSTRAINT fk_normas_guia_111 FOREIGN KEY (guia_id) REFERENCES guia_remision (id) ON DELETE RESTRICT;

ALTER TABLE guia_x_norma ADD CONSTRAINT fk_normas_guia_112 FOREIGN KEY (norma_id) REFERENCES norma (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_113 FOREIGN KEY (coordinacion_id) REFERENCES coordinacion_entrega (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_114 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_115 FOREIGN KEY (chofer_id) REFERENCES chofer_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE recepcion_planta ADD CONSTRAINT fk_recepciones_planta_116 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE recepcion_planta ADD CONSTRAINT fk_recepciones_planta_117 FOREIGN KEY (chofer_id) REFERENCES chofer_transporte_externo (id) ON DELETE RESTRICT;

ALTER TABLE recepcion_planta ADD CONSTRAINT fk_recepciones_planta_118 FOREIGN KEY (evidencia_descarte_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE recepcion_planta ADD CONSTRAINT fk_recepciones_planta_119 FOREIGN KEY (reporte_recepcion_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_120 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_121 FOREIGN KEY (proveedor_id) REFERENCES proveedor (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_122 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_123 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_transporte ADD CONSTRAINT fk_liquidaciones_transporte_124 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_transporte ADD CONSTRAINT fk_liquidaciones_transporte_125 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_transporte ADD CONSTRAINT fk_liquidaciones_transporte_126 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE gasto_transporte ADD CONSTRAINT fk_gastos_transporte_127 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE adelanto_transporte ADD CONSTRAINT fk_adelantos_transporte_128 FOREIGN KEY (acuerdo_id) REFERENCES acuerdo_transporte (id) ON DELETE RESTRICT;

ALTER TABLE adelanto_transporte ADD CONSTRAINT fk_adelantos_transporte_129 FOREIGN KEY (comprobante_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE aplicacion_adelanto ADD CONSTRAINT fk_aplicaciones_adelanto_130 FOREIGN KEY (adelanto_id) REFERENCES adelanto_transporte (id) ON DELETE RESTRICT;

ALTER TABLE factura_venta ADD CONSTRAINT fk_facturas_venta_131 FOREIGN KEY (carga_id) REFERENCES carga (id) ON DELETE RESTRICT;

ALTER TABLE factura_venta ADD CONSTRAINT fk_facturas_venta_132 FOREIGN KEY (archivo_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE pago_proveedor ADD CONSTRAINT fk_pagos_proveedor_133 FOREIGN KEY (comprobante_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE pago_proveedor ADD CONSTRAINT fk_pagos_proveedor_134 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE pago_transporte ADD CONSTRAINT fk_pagos_transporte_135 FOREIGN KEY (comprobante_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE pago_transporte ADD CONSTRAINT fk_pagos_transporte_136 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE cobro_venta ADD CONSTRAINT fk_cobros_venta_137 FOREIGN KEY (comprobante_id) REFERENCES archivo (id) ON DELETE RESTRICT;

ALTER TABLE cobro_venta ADD CONSTRAINT fk_cobros_venta_138 FOREIGN KEY (registrado_por) REFERENCES usuario (id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_139 FOREIGN KEY (participacion_id, campania_id, proveedor_id) REFERENCES participacion_proveedor_campana (id, campania_id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE campania_x_proveedores ADD CONSTRAINT fk_fincas_campania_140 FOREIGN KEY (finca_id, proveedor_id) REFERENCES finca (id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE examen_proveedor ADD CONSTRAINT fk_examenes_141 FOREIGN KEY (finca_campania_id, participacion_id) REFERENCES campania_x_proveedores (id, participacion_id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_142 FOREIGN KEY (certificacion_id, campania_id) REFERENCES certificado_campana (id, campania_id) ON DELETE RESTRICT;

ALTER TABLE certificado_campana_x_proveedor ADD CONSTRAINT fk_certificacion_proveedor_143 FOREIGN KEY (participacion_id, campania_id, proveedor_id) REFERENCES participacion_proveedor_campana (id, campania_id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_144 FOREIGN KEY (acuerdo_transporte_id, empresa_id) REFERENCES acuerdo_transporte (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_145 FOREIGN KEY (vehiculo_id, empresa_id) REFERENCES vehiculo_externo (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE coordinacion_entrega ADD CONSTRAINT fk_coordinaciones_entrega_146 FOREIGN KEY (chofer_id, empresa_id) REFERENCES chofer_transporte_externo (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_147 FOREIGN KEY (carga_id, coordinacion_id) REFERENCES carga (id, coordinacion_id) ON DELETE RESTRICT;

ALTER TABLE proveedor_guia ADD CONSTRAINT fk_proveedores_guia_148 FOREIGN KEY (guia_id, carga_id) REFERENCES guia_remision (id, carga_id) ON DELETE RESTRICT;

ALTER TABLE proveedor_guia ADD CONSTRAINT fk_proveedores_guia_149 FOREIGN KEY (proveedor_carga_id, carga_id) REFERENCES proveedor_carga (id, carga_id) ON DELETE RESTRICT;

ALTER TABLE liquidacion_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_150 FOREIGN KEY (proveedor_id, persona_liquidacion_id) REFERENCES proveedor_x_persona (proveedor_id, persona_id) ON DELETE RESTRICT;

ALTER TABLE aplicacion_adelanto ADD CONSTRAINT fk_aplicaciones_adelanto_151 FOREIGN KEY (liquidacion_id) REFERENCES liquidacion_transporte (id) ON DELETE RESTRICT;

CREATE INDEX ix_pagos_proveedor_1 ON pago_proveedor (liquidacion_id);

CREATE INDEX ix_pagos_transporte_2 ON pago_transporte (liquidacion_id);

CREATE INDEX ix_cobros_venta_3 ON cobro_venta (factura_id);

CREATE INDEX ix_personas_4 ON persona (documento_archivo_id);

CREATE INDEX ix_usuarios_5 ON usuario (persona_id);

CREATE INDEX ix_usuarios_6 ON usuario (rol_id);

CREATE INDEX ix_archivos_7 ON archivo (subido_por);

CREATE INDEX ix_sesiones_usuario_8 ON sesion_usuario (usuario_id);

CREATE INDEX ix_variedades_9 ON fruta_derivada (fruta_id);

CREATE INDEX ix_campanias_10 ON campana (fruta_id);

CREATE INDEX ix_campanias_11 ON campana (responsable_id);

CREATE INDEX ix_campanias_12 ON campana (lineamientos_id);

CREATE INDEX ix_campanias_13 ON campana (cerrada_por);

CREATE INDEX ix_campania_variedades_14 ON campana_x_fruta_derivada (campania_id);

CREATE INDEX ix_campania_variedades_15 ON campana_x_fruta_derivada (variedad_id);

CREATE INDEX ix_proveedores_16 ON proveedor (persona_principal_id);

CREATE INDEX ix_personas_proveedor_17 ON proveedor_x_persona (proveedor_id);

CREATE INDEX ix_personas_proveedor_18 ON proveedor_x_persona (persona_id);

CREATE INDEX ix_proveedor_frutas_19 ON proveedor_x_fruta (proveedor_id);

CREATE INDEX ix_proveedor_frutas_20 ON proveedor_x_fruta (fruta_id);

CREATE INDEX ix_proveedor_variedades_21 ON proveedor_x_fruta_derivada (proveedor_id);

CREATE INDEX ix_proveedor_variedades_22 ON proveedor_x_fruta_derivada (variedad_id);

CREATE INDEX ix_fincas_23 ON finca (proveedor_id);

CREATE INDEX ix_fincas_24 ON finca (variedad_id);

CREATE INDEX ix_certificados_propios_25 ON certificado_proveedor (proveedor_id);

CREATE INDEX ix_certificados_propios_26 ON certificado_proveedor (archivo_id);

CREATE INDEX ix_participaciones_proveedor_27 ON participacion_proveedor_campana (campania_id);

CREATE INDEX ix_participaciones_proveedor_28 ON participacion_proveedor_campana (proveedor_id);

CREATE INDEX ix_participacion_variedades_29 ON participacion_proveedor_x_fruta_derivada (participacion_id);

CREATE INDEX ix_participacion_variedades_30 ON participacion_proveedor_x_fruta_derivada (variedad_id);

CREATE INDEX ix_fincas_campania_31 ON campania_x_proveedores (participacion_id);

CREATE INDEX ix_fincas_campania_32 ON campania_x_proveedores (campania_id);

CREATE INDEX ix_fincas_campania_33 ON campania_x_proveedores (proveedor_id);

CREATE INDEX ix_fincas_campania_34 ON campania_x_proveedores (finca_id);

CREATE INDEX ix_entrevistas_35 ON entrevista_extencion (finca_campania_id);

CREATE INDEX ix_entrevistas_36 ON entrevista_extencion (registrada_por);

CREATE INDEX ix_entrevistas_37 ON entrevista_extencion (archivo_id);

CREATE INDEX ix_examenes_38 ON examen_proveedor (participacion_id);

CREATE INDEX ix_examenes_39 ON examen_proveedor (finca_campania_id);

CREATE INDEX ix_examenes_40 ON examen_proveedor (archivo_id);

CREATE INDEX ix_acuerdos_compra_41 ON acuerdo_compra (finca_campania_id);

CREATE INDEX ix_acuerdos_compra_42 ON acuerdo_compra (variedad_id);

CREATE INDEX ix_certificaciones_43 ON certificado_campana (campania_id);

CREATE INDEX ix_certificaciones_44 ON certificado_campana (norma_id);

CREATE INDEX ix_certificaciones_45 ON certificado_campana (archivo_id);

CREATE INDEX ix_certificacion_proveedor_46 ON certificado_campana_x_proveedor (certificacion_id);

CREATE INDEX ix_certificacion_proveedor_47 ON certificado_campana_x_proveedor (campania_id);

CREATE INDEX ix_certificacion_proveedor_48 ON certificado_campana_x_proveedor (participacion_id);

CREATE INDEX ix_certificacion_proveedor_49 ON certificado_campana_x_proveedor (proveedor_id);

CREATE INDEX ix_ampliaciones_certificacion_50 ON ampliacion_certificado_campana (certificacion_id);

CREATE INDEX ix_ampliaciones_certificacion_51 ON ampliacion_certificado_campana (registrado_por);

CREATE INDEX ix_pagos_certificacion_52 ON pago_certificado_campana (certificacion_id);

CREATE INDEX ix_pagos_certificacion_53 ON pago_certificado_campana (comprobante_id);

CREATE INDEX ix_pagos_certificacion_54 ON pago_certificado_campana (registrado_por);

CREATE INDEX ix_destinos_cliente_55 ON destino_cliente_negocio (cliente_id);

CREATE INDEX ix_requerimientos_comerciales_56 ON cliente_negocio_campana (campania_id);

CREATE INDEX ix_requerimientos_comerciales_57 ON cliente_negocio_campana (cliente_id);

CREATE INDEX ix_requerimientos_comerciales_58 ON cliente_negocio_campana (ficha_tecnica_id);

CREATE INDEX ix_requerimiento_variedades_59 ON cliente_negocio_campana_x_fruta_derivada (requerimiento_id);

CREATE INDEX ix_requerimiento_variedades_60 ON cliente_negocio_campana_x_fruta_derivada (variedad_id);

CREATE INDEX ix_contratos_venta_61 ON contrato_venta (requerimiento_id);

CREATE INDEX ix_contratos_venta_62 ON contrato_venta (archivo_id);

CREATE INDEX ix_entregas_programadas_63 ON entrega_programada (contrato_id);

CREATE INDEX ix_entregas_programadas_64 ON entrega_programada (destino_id);

CREATE INDEX ix_entrega_variedades_65 ON entrega_x_fruta_derivada (entrega_id);

CREATE INDEX ix_entrega_variedades_66 ON entrega_x_fruta_derivada (variedad_id);

CREATE INDEX ix_empresas_transporte_67 ON empresa_transporte_externo (persona_id);

CREATE INDEX ix_vehiculos_68 ON vehiculo_externo (empresa_id);

CREATE INDEX ix_choferes_69 ON chofer_transporte_externo (empresa_id);

CREATE INDEX ix_choferes_70 ON chofer_transporte_externo (persona_id);

CREATE INDEX ix_choferes_71 ON chofer_transporte_externo (usuario_id);

CREATE INDEX ix_solicitudes_transporte_72 ON solicitud_transporte (campania_id);

CREATE INDEX ix_solicitudes_transporte_73 ON solicitud_transporte (archivo_id);

CREATE INDEX ix_invitaciones_transporte_74 ON invitacion_transporte (solicitud_id);

CREATE INDEX ix_invitaciones_transporte_75 ON invitacion_transporte (empresa_id);

CREATE INDEX ix_cotizaciones_transporte_76 ON cotizacion_transporte (invitacion_id);

CREATE INDEX ix_cotizaciones_transporte_77 ON cotizacion_transporte (archivo_id);

CREATE INDEX ix_acuerdos_transporte_78 ON acuerdo_transporte (campania_id);

CREATE INDEX ix_acuerdos_transporte_79 ON acuerdo_transporte (empresa_id);

CREATE INDEX ix_acuerdos_transporte_80 ON acuerdo_transporte (cotizacion_id);

CREATE INDEX ix_acuerdos_transporte_81 ON acuerdo_transporte (archivo_id);

CREATE INDEX ix_coordinaciones_entrega_82 ON coordinacion_entrega (entrega_id);

CREATE INDEX ix_coordinaciones_entrega_83 ON coordinacion_entrega (acuerdo_transporte_id);

CREATE INDEX ix_coordinaciones_entrega_84 ON coordinacion_entrega (empresa_id);

CREATE INDEX ix_coordinaciones_entrega_85 ON coordinacion_entrega (chofer_id);

CREATE INDEX ix_origenes_entrega_86 ON origen_entrega (coordinacion_id);

CREATE INDEX ix_origenes_entrega_87 ON origen_entrega (finca_campania_id);

CREATE INDEX ix_cosechas_88 ON cosecha (entrega_id);

CREATE INDEX ix_cosechas_89 ON cosecha (evidencia_id);

CREATE INDEX ix_analisis_calidad_90 ON analisis_calidad (cosecha_id);

CREATE INDEX ix_analisis_calidad_91 ON analisis_calidad (finca_campania_id);

CREATE INDEX ix_analisis_calidad_92 ON analisis_calidad (archivo_id);

CREATE INDEX ix_mediciones_mtd_93 ON medicion_mtd (finca_campania_id);

CREATE INDEX ix_mediciones_mtd_94 ON medicion_mtd (archivo_id);

CREATE INDEX ix_mediciones_mtd_95 ON medicion_mtd (registrado_por);

CREATE INDEX ix_cargas_96 ON carga (coordinacion_id);

CREATE INDEX ix_cargas_97 ON carga (guia_salida_id);

CREATE INDEX ix_proveedores_carga_98 ON proveedor_carga (carga_id);

CREATE INDEX ix_proveedores_carga_99 ON proveedor_carga (participacion_id);

CREATE INDEX ix_proveedores_carga_100 ON proveedor_carga (variedad_id);

CREATE INDEX ix_origenes_carga_101 ON origen_carga (proveedor_carga_id);

CREATE INDEX ix_origenes_carga_102 ON origen_carga (finca_campania_id);

CREATE INDEX ix_gastos_carga_103 ON gasto_carga (carga_id);

CREATE INDEX ix_guias_remision_104 ON guia_remision (carga_id);

CREATE INDEX ix_guias_remision_105 ON guia_remision (finca_partida_id);

CREATE INDEX ix_guias_remision_106 ON guia_remision (destino_id);

CREATE INDEX ix_guias_remision_107 ON guia_remision (archivo_id);

CREATE INDEX ix_proveedores_guia_108 ON proveedor_guia (guia_id);

CREATE INDEX ix_proveedores_guia_109 ON proveedor_guia (carga_id);

CREATE INDEX ix_proveedores_guia_110 ON proveedor_guia (proveedor_carga_id);

CREATE INDEX ix_normas_guia_111 ON guia_x_norma (guia_id);

CREATE INDEX ix_normas_guia_112 ON guia_x_norma (norma_id);

CREATE INDEX ix_historial_chofer_113 ON historial_chofer (coordinacion_id);

CREATE INDEX ix_historial_chofer_114 ON historial_chofer (carga_id);

CREATE INDEX ix_historial_chofer_115 ON historial_chofer (chofer_id);

CREATE INDEX ix_recepciones_planta_116 ON recepcion_planta (carga_id);

CREATE INDEX ix_recepciones_planta_117 ON recepcion_planta (chofer_id);

CREATE INDEX ix_recepciones_planta_118 ON recepcion_planta (evidencia_descarte_id);

CREATE INDEX ix_recepciones_planta_119 ON recepcion_planta (reporte_recepcion_id);

CREATE INDEX ix_liquidaciones_proveedor_120 ON liquidacion_proveedor (carga_id);

CREATE INDEX ix_liquidaciones_proveedor_121 ON liquidacion_proveedor (proveedor_id);

CREATE INDEX ix_liquidaciones_proveedor_122 ON liquidacion_proveedor (registrado_por);

CREATE INDEX ix_liquidaciones_proveedor_123 ON liquidacion_proveedor (archivo_id);

CREATE INDEX ix_liquidaciones_transporte_124 ON liquidacion_transporte (carga_id);

CREATE INDEX ix_liquidaciones_transporte_125 ON liquidacion_transporte (registrado_por);

CREATE INDEX ix_liquidaciones_transporte_126 ON liquidacion_transporte (archivo_id);

CREATE INDEX ix_gastos_transporte_127 ON gasto_transporte (carga_id);

CREATE INDEX ix_adelantos_transporte_128 ON adelanto_transporte (acuerdo_id);

CREATE INDEX ix_adelantos_transporte_129 ON adelanto_transporte (comprobante_id);

CREATE INDEX ix_aplicaciones_adelanto_130 ON aplicacion_adelanto (adelanto_id);

CREATE INDEX ix_facturas_venta_131 ON factura_venta (carga_id);

CREATE INDEX ix_facturas_venta_132 ON factura_venta (archivo_id);

CREATE INDEX ix_pagos_proveedor_133 ON pago_proveedor (comprobante_id);

CREATE INDEX ix_pagos_proveedor_134 ON pago_proveedor (registrado_por);

CREATE INDEX ix_pagos_transporte_135 ON pago_transporte (comprobante_id);

CREATE INDEX ix_pagos_transporte_136 ON pago_transporte (registrado_por);

CREATE INDEX ix_cobros_venta_137 ON cobro_venta (comprobante_id);

CREATE INDEX ix_cobros_venta_138 ON cobro_venta (registrado_por);

CREATE INDEX ix_fincas_campania_139 ON campania_x_proveedores (participacion_id, campania_id, proveedor_id);

CREATE INDEX ix_fincas_campania_140 ON campania_x_proveedores (finca_id, proveedor_id);

CREATE INDEX ix_examenes_141 ON examen_proveedor (finca_campania_id, participacion_id);

CREATE INDEX ix_certificacion_proveedor_142 ON certificado_campana_x_proveedor (certificacion_id, campania_id);

CREATE INDEX ix_certificacion_proveedor_143 ON certificado_campana_x_proveedor (participacion_id, campania_id, proveedor_id);

CREATE INDEX ix_coordinaciones_entrega_144 ON coordinacion_entrega (acuerdo_transporte_id, empresa_id);

CREATE INDEX ix_coordinaciones_entrega_145 ON coordinacion_entrega (vehiculo_id, empresa_id);

CREATE INDEX ix_coordinaciones_entrega_146 ON coordinacion_entrega (chofer_id, empresa_id);

CREATE INDEX ix_historial_chofer_147 ON historial_chofer (carga_id, coordinacion_id);

CREATE INDEX ix_proveedores_guia_148 ON proveedor_guia (guia_id, carga_id);

CREATE INDEX ix_proveedores_guia_149 ON proveedor_guia (proveedor_carga_id, carga_id);

CREATE INDEX ix_liquidaciones_proveedor_150 ON liquidacion_proveedor (proveedor_id, persona_liquidacion_id);

CREATE INDEX ix_aplicaciones_adelanto_151 ON aplicacion_adelanto (liquidacion_id);

CREATE INDEX ix_eventos_fecha ON historial_chofer (coordinacion_id, fecha_hora DESC, id DESC);

CREATE INDEX ix_uit_persona_fecha ON liquidacion_proveedor (persona_liquidacion_id, fecha);

-- Validaciones estructurales entre módulos. Bloqueos en filas padre serializan consumos.
CREATE FUNCTION agro.validar_contexto() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE camp bigint; expected bigint; fruit bigint; otherfruit bigint; part bigint; prov bigint; ent bigint; coord bigint; drv bigint;
BEGIN
  IF TG_TABLE_NAME='campana_x_fruta_derivada' THEN
    SELECT fruta_id INTO fruit FROM campana WHERE id=NEW.campania_id;
    SELECT fruta_id INTO otherfruit FROM fruta_derivada WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Variedad ajena a la fruta de campaña'; END IF;
  ELSIF TG_TABLE_NAME IN ('participacion_proveedor_x_fruta_derivada','cliente_negocio_campana_x_fruta_derivada') THEN
    IF TG_TABLE_NAME='participacion_proveedor_x_fruta_derivada' THEN SELECT campania_id INTO camp FROM participacion_proveedor_campana WHERE id=NEW.participacion_id;
    ELSE SELECT campania_id INTO camp FROM cliente_negocio_campana WHERE id=NEW.requerimiento_id; END IF;
    SELECT c.fruta_id INTO fruit FROM campana c WHERE c.id=camp;
    SELECT fruta_id INTO otherfruit FROM fruta_derivada WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Variedad incompatible con campaña'; END IF;
  ELSIF TG_TABLE_NAME='chofer_transporte_externo' THEN
    IF NEW.usuario_id IS NOT NULL THEN
      IF NOT EXISTS(SELECT 1 FROM usuario WHERE id=NEW.usuario_id AND persona_id=NEW.persona_id) THEN RAISE EXCEPTION 'Cuenta y chofer deben identificar a la misma persona'; END IF;
    END IF;
  ELSIF TG_TABLE_NAME='entrega_programada' THEN
    SELECT r.cliente_id INTO expected FROM contrato_venta c JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE c.id=NEW.contrato_id;
    IF NOT EXISTS(SELECT 1 FROM destino_cliente_negocio WHERE id=NEW.destino_id AND cliente_id=expected) THEN RAISE EXCEPTION 'Destino de otro cliente'; END IF;
  ELSIF TG_TABLE_NAME='entrega_x_fruta_derivada' THEN
    SELECT r.campania_id INTO camp FROM entrega_programada e JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE e.id=NEW.entrega_id;
    SELECT fruta_id INTO fruit FROM campana WHERE id=camp;
    SELECT fruta_id INTO otherfruit FROM fruta_derivada WHERE id=NEW.variedad_id;
    IF fruit IS DISTINCT FROM otherfruit THEN RAISE EXCEPTION 'Distribución de variedad incompatible'; END IF;
  ELSIF TG_TABLE_NAME='coordinacion_entrega' THEN
    SELECT r.campania_id INTO camp FROM entrega_programada e JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE e.id=NEW.entrega_id;
    IF NOT EXISTS(SELECT 1 FROM acuerdo_transporte WHERE id=NEW.acuerdo_transporte_id AND campania_id=camp) THEN RAISE EXCEPTION 'Acuerdo de transporte de otra campaña'; END IF;
  ELSIF TG_TABLE_NAME='origen_entrega' THEN
    SELECT r.campania_id INTO camp FROM coordinacion_entrega co JOIN entrega_programada e ON e.id=co.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE co.id=NEW.coordinacion_id;
    SELECT campania_id INTO expected FROM campania_x_proveedores WHERE id=NEW.finca_campania_id;
    IF camp IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Finca de otra campaña'; END IF;
    IF EXISTS(SELECT 1 FROM coordinacion_entrega co JOIN entrega_programada e ON e.id=co.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id WHERE co.id=NEW.coordinacion_id AND c.canal='EXPORTACION') AND NOT EXISTS(SELECT 1 FROM campania_x_proveedores f JOIN participacion_proveedor_campana p ON p.id=f.participacion_id WHERE f.id=NEW.finca_campania_id AND p.tipo_fruta='ORGANICA') THEN RAISE EXCEPTION 'Exportación exige origen orgánico según el prototipo'; END IF;
  ELSIF TG_TABLE_NAME='proveedor_carga' THEN
    SELECT coordinacion_id INTO coord FROM carga WHERE id=NEW.carga_id;
    IF NOT EXISTS(SELECT 1 FROM origen_entrega o JOIN campania_x_proveedores f ON f.id=o.finca_campania_id WHERE o.coordinacion_id=coord AND f.participacion_id=NEW.participacion_id) THEN RAISE EXCEPTION 'Proveedor no coordinado para esta carga'; END IF;
    IF NOT EXISTS(SELECT 1 FROM participacion_proveedor_x_fruta_derivada WHERE participacion_id=NEW.participacion_id AND variedad_id=NEW.variedad_id) THEN RAISE EXCEPTION 'Variedad no vinculada al proveedor en campaña'; END IF;
  ELSIF TG_TABLE_NAME='origen_carga' THEN
    SELECT p.participacion_id,c.coordinacion_id INTO part,coord FROM proveedor_carga p JOIN carga c ON c.id=p.carga_id WHERE p.id=NEW.proveedor_carga_id;
    IF NOT EXISTS(SELECT 1 FROM campania_x_proveedores f JOIN origen_entrega o ON o.finca_campania_id=f.id WHERE f.id=NEW.finca_campania_id AND f.participacion_id=part AND o.coordinacion_id=coord) THEN RAISE EXCEPTION 'Origen ajeno al proveedor o a su coordinación'; END IF;
  ELSIF TG_TABLE_NAME='analisis_calidad' THEN
    SELECT r.campania_id INTO camp FROM cosecha h JOIN entrega_programada e ON e.id=h.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE h.id=NEW.cosecha_id;
    IF NOT EXISTS(SELECT 1 FROM campania_x_proveedores WHERE id=NEW.finca_campania_id AND campania_id=camp) THEN RAISE EXCEPTION 'Análisis de finca ajena a campaña'; END IF;
  ELSIF TG_TABLE_NAME='recepcion_planta' THEN
    SELECT co.chofer_id INTO drv FROM carga ca JOIN coordinacion_entrega co ON co.id=ca.coordinacion_id WHERE ca.id=NEW.carga_id;
    IF drv IS DISTINCT FROM NEW.chofer_id THEN RAISE EXCEPTION 'Recepción de otro chofer'; END IF;
  ELSIF TG_TABLE_NAME='historial_chofer' THEN
    SELECT chofer_id INTO drv FROM coordinacion_entrega WHERE id=NEW.coordinacion_id;
    IF drv IS DISTINCT FROM NEW.chofer_id THEN RAISE EXCEPTION 'Despacho de otro chofer'; END IF;
  END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['campana_x_fruta_derivada','participacion_proveedor_x_fruta_derivada','cliente_negocio_campana_x_fruta_derivada','chofer_transporte_externo','entrega_programada','entrega_x_fruta_derivada','coordinacion_entrega','origen_entrega','proveedor_carga','origen_carga','analisis_calidad','recepcion_planta','historial_chofer'] LOOP
 EXECUTE format('CREATE TRIGGER contexto BEFORE INSERT OR UPDATE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.validar_contexto()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_programacion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE parent bigint; total numeric; limite numeric;
BEGIN
  IF TG_TABLE_NAME='entrega_programada' THEN
    parent:=NEW.contrato_id;
    SELECT kilos_acordados INTO limite FROM contrato_venta WHERE id=parent FOR UPDATE;
    SELECT coalesce(sum(kilos_programados),0) INTO total FROM entrega_programada WHERE contrato_id=parent AND id<>NEW.id;
    IF total+NEW.kilos_programados>limite THEN RAISE EXCEPTION 'Kilos programados exceden contrato'; END IF;
  ELSE
    SELECT coalesce(sum(kilos_programados),0) INTO total FROM entrega_programada WHERE contrato_id=NEW.id;
    IF total>NEW.kilos_acordados THEN RAISE EXCEPTION 'Contrato menor que su programación'; END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER programacion BEFORE INSERT OR UPDATE ON agro.entrega_programada FOR EACH ROW EXECUTE FUNCTION agro.validar_programacion();
CREATE TRIGGER programacion BEFORE UPDATE ON agro.contrato_venta FOR EACH ROW EXECUTE FUNCTION agro.validar_programacion();

-- La distribución por variedad debe ser completa; se puede crear cabecera y detalle en una transacción.
CREATE FUNCTION agro.validar_distribucion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE e bigint; total numeric; esperado numeric;
BEGIN
  IF TG_TABLE_NAME='entrega_programada' THEN e:=coalesce(NEW.id,OLD.id);
  ELSE e:=coalesce(NEW.entrega_id,OLD.entrega_id); END IF;
  SELECT kilos_programados INTO esperado FROM entrega_programada WHERE id=e;
  IF esperado IS NULL THEN RETURN NULL; END IF;
  SELECT coalesce(sum(kilos_programados),0) INTO total FROM entrega_x_fruta_derivada WHERE entrega_id=e;
  IF total<>esperado THEN RAISE EXCEPTION 'Distribución por variedades no coincide con entrega %',e; END IF;
  IF TG_TABLE_NAME='entrega_x_fruta_derivada' THEN
    IF TG_OP='UPDATE' THEN
      IF OLD.entrega_id<>NEW.entrega_id THEN RAISE EXCEPTION 'No reasignar detalle; quitar y crear en transacción'; END IF;
    END IF;
  END IF;
  RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER distribucion AFTER INSERT OR UPDATE ON agro.entrega_programada DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION agro.validar_distribucion();
CREATE CONSTRAINT TRIGGER distribucion AFTER INSERT OR UPDATE OR DELETE ON agro.entrega_x_fruta_derivada DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION agro.validar_distribucion();

CREATE FUNCTION agro.validar_asignacion_guia() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE limite numeric; usado numeric; origen bigint;
BEGIN
  SELECT kilos_cargados INTO limite FROM proveedor_carga WHERE id=NEW.proveedor_carga_id FOR UPDATE;
  SELECT coalesce(sum(kilos_asignados),0) INTO usado FROM proveedor_guia WHERE proveedor_carga_id=NEW.proveedor_carga_id AND id<>NEW.id;
  IF usado+NEW.kilos_asignados>limite THEN RAISE EXCEPTION 'Kilos de proveedor duplicados entre guías'; END IF;
  SELECT finca_partida_id INTO origen FROM guia_remision WHERE id=NEW.guia_id;
  IF NOT EXISTS(SELECT 1 FROM origen_carga o JOIN campania_x_proveedores f ON f.id=o.finca_campania_id WHERE o.proveedor_carga_id=NEW.proveedor_carga_id AND f.finca_id=origen) THEN RAISE EXCEPTION 'Proveedor sin trazabilidad al punto de partida de la guía'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER asignacion_guia BEFORE INSERT OR UPDATE ON agro.proveedor_guia FOR EACH ROW EXECUTE FUNCTION agro.validar_asignacion_guia();

CREATE FUNCTION agro.validar_liquidacion_compra() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE calculado numeric; faltan bigint;
BEGIN
  SELECT round(sum(pc.kilos_cargados*pc.precio_compra_kg_aplicado),2),count(*) FILTER(WHERE pc.precio_compra_kg_aplicado IS NULL)
  INTO calculado,faltan FROM proveedor_carga pc JOIN participacion_proveedor_campana p ON p.id=pc.participacion_id
  WHERE pc.carga_id=NEW.carga_id AND p.proveedor_id=NEW.proveedor_id;
  IF calculado IS NULL OR faltan>0 OR calculado<>NEW.importe_compra THEN RAISE EXCEPTION 'Compra debe coincidir con kilos y precios de ese proveedor'; END IF;
  IF NOT EXISTS(SELECT 1 FROM proveedor_x_persona WHERE proveedor_id=NEW.proveedor_id AND persona_id=NEW.persona_liquidacion_id AND activo) THEN RAISE EXCEPTION 'Persona no vinculada activamente al proveedor'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER importe_compra BEFORE INSERT OR UPDATE ON agro.liquidacion_proveedor FOR EACH ROW EXECUTE FUNCTION agro.validar_liquidacion_compra();

CREATE FUNCTION agro.validar_factura() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE peso numeric; precio numeric; divisa text; resultado text; respaldo bigint;
BEGIN
  SELECT rp.peso_planta_kg,rp.resultado,rp.reporte_recepcion_id INTO peso,resultado,respaldo FROM recepcion_planta rp WHERE rp.carga_id=NEW.carga_id FOR UPDATE;
  IF peso IS NULL OR resultado IS NULL OR respaldo IS NULL THEN RAISE EXCEPTION 'Facturación requiere recepción documentada, resultado y peso'; END IF;
  SELECT c.precio_kg,c.moneda INTO precio,divisa FROM carga ca JOIN coordinacion_entrega co ON co.id=ca.coordinacion_id JOIN entrega_programada e ON e.id=co.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id WHERE ca.id=NEW.carga_id FOR UPDATE OF c;
  IF NEW.kilos_facturados<>peso OR NEW.precio_kg_aplicado<>precio OR NEW.moneda<>divisa THEN RAISE EXCEPTION 'Factura debe capturar peso recibido y condiciones de contrato'; END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER factura_consistente BEFORE INSERT OR UPDATE ON agro.factura_venta FOR EACH ROW EXECUTE FUNCTION agro.validar_factura();

CREATE FUNCTION agro.validar_saldos() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE limite numeric; usado numeric; extra numeric:=0; aid bigint; expected bigint;
BEGIN
  IF TG_TABLE_NAME='pago_proveedor' THEN
    SELECT importe_compra INTO limite FROM liquidacion_proveedor WHERE id=NEW.liquidacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pago_proveedor WHERE liquidacion_id=NEW.liquidacion_id;
  ELSIF TG_TABLE_NAME='cobro_venta' THEN
    SELECT importe_venta INTO limite FROM factura_venta WHERE id=NEW.factura_id AND estado='EMITIDA' FOR UPDATE;
    IF limite IS NULL THEN RAISE EXCEPTION 'No cobrar una preparación sin factura emitida'; END IF;
    SELECT coalesce(sum(monto),0) INTO usado FROM cobro_venta WHERE factura_id=NEW.factura_id;
  ELSIF TG_TABLE_NAME='pago_certificado_campana' THEN
    SELECT costo INTO limite FROM certificado_campana WHERE id=NEW.certificacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pago_certificado_campana WHERE certificacion_id=NEW.certificacion_id;
  ELSIF TG_TABLE_NAME='adelanto_transporte' THEN
    SELECT monto_acordado INTO limite FROM acuerdo_transporte WHERE id=NEW.acuerdo_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM adelanto_transporte WHERE acuerdo_id=NEW.acuerdo_id;
  ELSE
    SELECT l.flete+coalesce((SELECT sum(g.monto) FROM gasto_transporte g WHERE g.carga_id=l.carga_id AND g.incluido_en_liquidacion),0)
    INTO limite FROM liquidacion_transporte l WHERE l.id=NEW.liquidacion_id FOR UPDATE;
    SELECT coalesce(sum(monto),0) INTO usado FROM pago_transporte WHERE liquidacion_id=NEW.liquidacion_id;
    SELECT coalesce(sum(monto),0) INTO extra FROM aplicacion_adelanto WHERE liquidacion_id=NEW.liquidacion_id;
    IF TG_TABLE_NAME='aplicacion_adelanto' THEN
      SELECT co.acuerdo_transporte_id INTO expected FROM liquidacion_transporte l JOIN carga c ON c.id=l.carga_id JOIN coordinacion_entrega co ON co.id=c.coordinacion_id WHERE l.id=NEW.liquidacion_id;
      SELECT acuerdo_id INTO aid FROM adelanto_transporte WHERE id=NEW.adelanto_id FOR UPDATE;
      IF aid IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Adelanto de otro acuerdo'; END IF;
      IF NEW.monto+(SELECT coalesce(sum(monto),0) FROM aplicacion_adelanto WHERE adelanto_id=NEW.adelanto_id)>(SELECT monto FROM adelanto_transporte WHERE id=NEW.adelanto_id) THEN RAISE EXCEPTION 'Adelanto agotado'; END IF;
    END IF;
  END IF;
  IF NEW.monto+usado+extra>limite THEN RAISE EXCEPTION 'Movimiento excede saldo disponible'; END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['pago_proveedor','pago_transporte','cobro_venta','pago_certificado_campana','adelanto_transporte','aplicacion_adelanto'] LOOP
 EXECUTE format('CREATE TRIGGER saldo BEFORE INSERT ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.validar_saldos()',t);
END LOOP; END $$;

-- Historial financiero inmutable. Correcciones contables requieren un futuro flujo de reversos.
CREATE FUNCTION agro.no_alterar_historial() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Historial protegido: no editar ni eliminar; implementar reverso explícito'; END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['pago_proveedor','pago_transporte','cobro_venta','pago_certificado_campana','adelanto_transporte','aplicacion_adelanto','historial_chofer','ampliacion_certificado_campana','medicion_mtd'] LOOP
 EXECUTE format('CREATE TRIGGER inmutable BEFORE UPDATE OR DELETE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.no_alterar_historial()',t);
END LOOP; END $$;

-- Se congelan cabeceras y orígenes utilizados por documentos. Impide vaciar sus detalles.
CREATE FUNCTION agro.proteger_documentos() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE cid bigint; protegido boolean:=false;
BEGIN
  IF TG_TABLE_NAME IN ('liquidacion_proveedor','liquidacion_transporte') THEN
    RAISE EXCEPTION 'Liquidación registrada protegida; registrar corrección mediante un flujo de reverso';
  ELSIF TG_TABLE_NAME='factura_venta' THEN
    protegido:=OLD.estado='EMITIDA';
    IF NOT protegido AND TG_OP='UPDATE' THEN
      IF (to_jsonb(NEW)-ARRAY['estado','numero_factura','fecha_emision','fecha_vencimiento','archivo_id']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['estado','numero_factura','fecha_emision','fecha_vencimiento','archivo_id']) THEN RAISE EXCEPTION 'Preparación solo admite completar datos de emisión'; END IF;
    END IF;
  ELSIF TG_TABLE_NAME='contrato_venta' THEN
    SELECT EXISTS(SELECT 1 FROM entrega_programada e JOIN coordinacion_entrega co ON co.entrega_id=e.id JOIN carga ca ON ca.coordinacion_id=co.id JOIN factura_venta f ON f.carga_id=ca.id WHERE e.contrato_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='cliente_negocio_campana' THEN
    SELECT EXISTS(SELECT 1 FROM contrato_venta WHERE requerimiento_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='certificado_campana' THEN
    SELECT EXISTS(SELECT 1 FROM pago_certificado_campana WHERE certificacion_id=OLD.id) OR EXISTS(SELECT 1 FROM ampliacion_certificado_campana WHERE certificacion_id=OLD.id) INTO protegido;
  ELSIF TG_TABLE_NAME='acuerdo_transporte' THEN
    SELECT EXISTS(SELECT 1 FROM adelanto_transporte WHERE acuerdo_id=OLD.id) OR EXISTS(SELECT 1 FROM coordinacion_entrega co JOIN carga ca ON ca.coordinacion_id=co.id JOIN liquidacion_transporte l ON l.carga_id=ca.id WHERE co.acuerdo_transporte_id=OLD.id) INTO protegido;
  ELSE
    CASE TG_TABLE_NAME
      WHEN 'carga' THEN cid:=OLD.id;
      WHEN 'coordinacion_entrega' THEN SELECT id INTO cid FROM carga WHERE coordinacion_id=OLD.id;
      WHEN 'origen_entrega' THEN SELECT id INTO cid FROM carga WHERE coordinacion_id=OLD.coordinacion_id;
      WHEN 'origen_carga' THEN SELECT carga_id INTO cid FROM proveedor_carga WHERE id=OLD.proveedor_carga_id;
      WHEN 'entrega_programada' THEN SELECT ca.id INTO cid FROM carga ca JOIN coordinacion_entrega co ON co.id=ca.coordinacion_id WHERE co.entrega_id=OLD.id;
      WHEN 'entrega_x_fruta_derivada' THEN SELECT ca.id INTO cid FROM carga ca JOIN coordinacion_entrega co ON co.id=ca.coordinacion_id WHERE co.entrega_id=OLD.entrega_id;
      ELSE cid:=OLD.carga_id;
    END CASE;
    SELECT EXISTS(SELECT 1 FROM factura_venta WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidacion_proveedor WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidacion_transporte WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM guia_remision WHERE carga_id=cid) INTO protegido;
    -- Permite agregar recepción y adjuntar guía de salida sin alterar carga/origen ya documentados.
    IF protegido AND TG_TABLE_NAME='carga' AND TG_OP='UPDATE' THEN
      protegido := (to_jsonb(NEW)-ARRAY['guia_salida_id','guia_salida_registrada_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['guia_salida_id','guia_salida_registrada_at']);
    END IF;
    IF TG_TABLE_NAME='recepcion_planta' THEN
      SELECT EXISTS(SELECT 1 FROM factura_venta WHERE carga_id=cid) INTO protegido;
      IF protegido AND TG_OP='UPDATE' THEN
        protegido := (to_jsonb(NEW)-ARRAY['descarga_at','cierre_fisico_at','cierre_administrativo_at','jabas_devueltas','jabas_devolucion_at','recepcion_confirmada_at','descarte_confirmado_at']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['descarga_at','cierre_fisico_at','cierre_administrativo_at','jabas_devueltas','jabas_devolucion_at','recepcion_confirmada_at','descarte_confirmado_at']);
      END IF;
    END IF;
  END IF;
  IF protegido THEN RAISE EXCEPTION 'Documento u origen protegido por movimientos o documentación registrada'; END IF;
  IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['liquidacion_proveedor','liquidacion_transporte','factura_venta','contrato_venta','cliente_negocio_campana','certificado_campana','acuerdo_transporte','carga','coordinacion_entrega','origen_entrega','origen_carga','entrega_programada','entrega_x_fruta_derivada','proveedor_carga','gasto_transporte','recepcion_planta','guia_remision'] LOOP
 EXECUTE format('CREATE TRIGGER proteger BEFORE UPDATE OR DELETE ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.proteger_documentos()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_secuencia_chofer() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE previo text; requerido text; rp recepcion_planta%ROWTYPE;
BEGIN
  PERFORM 1 FROM coordinacion_entrega WHERE id=NEW.coordinacion_id FOR UPDATE;
  SELECT estado INTO previo FROM historial_chofer WHERE coordinacion_id=NEW.coordinacion_id ORDER BY fecha_hora DESC,id DESC LIMIT 1;
  requerido:=CASE coalesce(previo,'') WHEN '' THEN 'EN_CARGA' WHEN 'EN_CARGA' THEN 'SALIDA' WHEN 'SALIDA' THEN 'EN_CAMINO' WHEN 'EN_CAMINO' THEN 'LLEGADA' WHEN 'LLEGADA' THEN 'CIERRE' ELSE NULL END;
  IF requerido IS NULL OR NEW.estado<>requerido THEN RAISE EXCEPTION 'Secuencia de despacho inválida'; END IF;
  IF EXISTS(SELECT 1 FROM historial_chofer WHERE coordinacion_id=NEW.coordinacion_id AND fecha_hora>NEW.fecha_hora) THEN RAISE EXCEPTION 'Evento anterior al último reporte'; END IF;
  IF NEW.estado='CIERRE' THEN
    SELECT * INTO rp FROM recepcion_planta WHERE carga_id=NEW.carga_id;
    IF rp.recepcion_confirmada_at IS NULL OR rp.descarte_confirmado_at IS NULL OR rp.peso_planta_kg IS NULL OR rp.hubo_descarte IS NULL OR rp.descarte_kg IS NULL THEN RAISE EXCEPTION 'Checklist de recepción y descarte incompleto'; END IF;
    IF NOT EXISTS(SELECT 1 FROM carga WHERE id=NEW.carga_id AND guia_salida_id IS NOT NULL) THEN RAISE EXCEPTION 'Falta guía de salida'; END IF;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER secuencia BEFORE INSERT ON agro.historial_chofer FOR EACH ROW EXECUTE FUNCTION agro.validar_secuencia_chofer();

-- Consultas derivadas: no se almacenan saldos ni copias de resúmenes por pantalla.
CREATE VIEW agro.v_saldo_proveedor AS
SELECT l.*,l.importe_compra-coalesce((SELECT sum(p.monto) FROM agro.pago_proveedor p WHERE p.liquidacion_id=l.id),0) AS saldo
FROM agro.liquidacion_proveedor l;
CREATE VIEW agro.v_saldo_factura AS
SELECT f.*,f.importe_venta-coalesce((SELECT sum(c.monto) FROM agro.cobro_venta c WHERE c.factura_id=f.id),0) AS saldo
FROM agro.factura_venta f;
CREATE VIEW agro.v_saldo_transporte AS
SELECT l.*,l.flete+coalesce((SELECT sum(g.monto) FROM agro.gasto_transporte g WHERE g.carga_id=l.carga_id AND g.incluido_en_liquidacion),0)
-coalesce((SELECT sum(p.monto) FROM agro.pago_transporte p WHERE p.liquidacion_id=l.id),0)
-coalesce((SELECT sum(a.monto) FROM agro.aplicacion_adelanto a WHERE a.liquidacion_id=l.id),0) AS saldo
FROM agro.liquidacion_transporte l;
CREATE VIEW agro.v_control_uit AS
SELECT p.persona_liquidacion_id,extract(year FROM p.fecha)::integer AS anio,sum(p.importe_compra) AS acumulado,
u.valor,u.limite_uit,u.valor*u.limite_uit-sum(p.importe_compra) AS disponible
FROM agro.liquidacion_proveedor p LEFT JOIN agro.parametro_uit u ON u.anio=extract(year FROM p.fecha)::integer
GROUP BY p.persona_liquidacion_id,extract(year FROM p.fecha)::integer,u.valor,u.limite_uit;
CREATE VIEW agro.v_estado_despacho AS
SELECT DISTINCT ON (coordinacion_id) coordinacion_id,carga_id,chofer_id,estado,fecha_hora
FROM agro.historial_chofer ORDER BY coordinacion_id,fecha_hora DESC,id DESC;
CREATE VIEW agro.v_programa_semanal AS
SELECT r.campania_id,r.cliente_id,c.id AS contrato_id,e.id AS entrega_id,e.fecha,
extract(isoyear FROM e.fecha)::integer AS anio_iso,extract(week FROM e.fecha)::integer AS semana_iso,
d.variedad_id,d.kilos_programados,co.vehiculo_id
FROM agro.entrega_programada e JOIN agro.entrega_x_fruta_derivada d ON d.entrega_id=e.id
JOIN agro.contrato_venta c ON c.id=e.contrato_id JOIN agro.cliente_negocio_campana r ON r.id=c.requerimiento_id
LEFT JOIN agro.coordinacion_entrega co ON co.entrega_id=e.id;

-- El cierre exige validación transaccional del servicio descrita en el reporte.
-- Esta función añade un mínimo verificable en BD: no cerrar con entregas sin carga,
-- despachos abiertos, recepciones incompletas, facturas, liquidaciones o saldos pendientes.
CREATE FUNCTION agro.validar_cierre_campania() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE abiertos bigint;
BEGIN
 IF OLD.estado='FINALIZADO' THEN RAISE EXCEPTION 'Campaña finalizada protegida'; END IF;
 IF NEW.estado='FINALIZADO' THEN
   SELECT count(*) INTO abiertos FROM entrega_programada e JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id
   LEFT JOIN coordinacion_entrega co ON co.entrega_id=e.id LEFT JOIN carga ca ON ca.coordinacion_id=co.id
   LEFT JOIN recepcion_planta rp ON rp.carga_id=ca.id LEFT JOIN v_estado_despacho h ON h.coordinacion_id=co.id
   LEFT JOIN factura_venta f ON f.carga_id=ca.id LEFT JOIN v_saldo_transporte st ON st.carga_id=ca.id
   WHERE r.campania_id=NEW.id AND (ca.id IS NULL OR h.estado IS DISTINCT FROM 'CIERRE' OR rp.peso_planta_kg IS NULL OR rp.resultado IS NULL OR rp.reporte_recepcion_id IS NULL OR rp.descarga_at IS NULL OR rp.cierre_fisico_at IS NULL OR rp.cierre_administrativo_at IS NULL OR f.estado IS DISTINCT FROM 'EMITIDA' OR st.id IS NULL OR st.saldo<>0);
   IF abiertos>0 THEN RAISE EXCEPTION 'Campaña con entregas o cierres pendientes'; END IF;
   IF EXISTS(SELECT 1 FROM contrato_venta c JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND c.kilos_acordados<>(SELECT coalesce(sum(kilos_programados),0) FROM entrega_programada e WHERE e.contrato_id=c.id)) THEN RAISE EXCEPTION 'Contrato sin programación completa'; END IF;
   IF EXISTS(SELECT 1 FROM v_saldo_factura f JOIN carga ca ON ca.id=f.carga_id JOIN coordinacion_entrega co ON co.id=ca.coordinacion_id JOIN entrega_programada e ON e.id=co.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND f.saldo<>0) THEN RAISE EXCEPTION 'Cobros pendientes'; END IF;
   IF EXISTS(SELECT 1 FROM proveedor_carga pc JOIN participacion_proveedor_campana pp ON pp.id=pc.participacion_id LEFT JOIN v_saldo_proveedor s ON s.carga_id=pc.carga_id AND s.proveedor_id=pp.proveedor_id WHERE pp.campania_id=NEW.id AND (s.id IS NULL OR s.saldo<>0)) THEN RAISE EXCEPTION 'Compras sin liquidar o pagar'; END IF;
   IF EXISTS(SELECT 1 FROM certificado_campana c WHERE c.campania_id=NEW.id AND c.costo<>(SELECT coalesce(sum(monto),0) FROM pago_certificado_campana p WHERE p.certificacion_id=c.id)) THEN RAISE EXCEPTION 'Certificación por pagar'; END IF;
   IF EXISTS(SELECT 1 FROM adelanto_transporte a JOIN acuerdo_transporte ac ON ac.id=a.acuerdo_id WHERE ac.campania_id=NEW.id AND a.monto<>(SELECT coalesce(sum(monto),0) FROM aplicacion_adelanto ap WHERE ap.adelanto_id=a.id)) THEN RAISE EXCEPTION 'Adelantos sin aplicar'; END IF;
   IF EXISTS(SELECT 1 FROM cosecha h JOIN entrega_programada e ON e.id=h.entrega_id JOIN contrato_venta c ON c.id=e.contrato_id JOIN cliente_negocio_campana r ON r.id=c.requerimiento_id WHERE r.campania_id=NEW.id AND (h.estado<>'CONCLUIDA' OR (c.canal='EXPORTACION' AND h.cierre_cosecha_at IS NULL))) THEN RAISE EXCEPTION 'Cosechas sin concluir'; END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER cierre BEFORE UPDATE ON agro.campana FOR EACH ROW EXECUTE FUNCTION agro.validar_cierre_campania();

-- Sin usuarios, credenciales ni datos de demostración. No concede acceso público a tablas.
REVOKE ALL ON SCHEMA agro FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA agro FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA agro FROM PUBLIC;
-- Evita agregar líneas a posteriori para desajustar un documento ya registrado.
CREATE FUNCTION agro.proteger_nuevos_detalles() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE cid bigint;
BEGIN
  IF TG_TABLE_NAME='origen_carga' THEN
    SELECT carga_id INTO cid FROM proveedor_carga WHERE id=NEW.proveedor_carga_id;
  ELSIF TG_TABLE_NAME='origen_entrega' THEN
    SELECT id INTO cid FROM carga WHERE coordinacion_id=NEW.coordinacion_id;
  ELSE cid:=NEW.carga_id; END IF;
  IF TG_TABLE_NAME='gasto_transporte' THEN
    IF EXISTS(SELECT 1 FROM liquidacion_transporte WHERE carga_id=cid) THEN RAISE EXCEPTION 'No agregar gastos a transporte ya liquidado'; END IF;
    RETURN NEW;
  END IF;
  IF EXISTS(SELECT 1 FROM factura_venta WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidacion_proveedor WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM liquidacion_transporte WHERE carga_id=cid) OR EXISTS(SELECT 1 FROM guia_remision WHERE carga_id=cid) THEN
    RAISE EXCEPTION 'No agregar detalle a carga ya documentada';
  END IF;
  RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN
FOREACH t IN ARRAY ARRAY['proveedor_carga','origen_carga','origen_entrega','gasto_transporte'] LOOP
 EXECUTE format('CREATE TRIGGER nuevo_detalle BEFORE INSERT ON agro.%I FOR EACH ROW EXECUTE FUNCTION agro.proteger_nuevos_detalles()',t);
END LOOP; END $$;

CREATE FUNCTION agro.validar_recepcion() RETURNS trigger LANGUAGE plpgsql SET search_path=agro,pg_temp AS $$
DECLARE origen numeric;
BEGIN
 SELECT sum(kilos_cargados) INTO origen FROM proveedor_carga WHERE carga_id=NEW.carga_id;
 IF NEW.descarte_kg>origen THEN RAISE EXCEPTION 'Descarte superior al peso de origen'; END IF;
 IF NEW.recepcion_confirmada_at IS NOT NULL AND (NEW.peso_planta_kg IS NULL OR NEW.fecha_recepcion IS NULL) THEN RAISE EXCEPTION 'Recepción confirmada requiere peso y fecha'; END IF;
 IF NEW.descarte_confirmado_at IS NOT NULL AND (NEW.hubo_descarte IS NULL OR NEW.descarte_kg IS NULL) THEN RAISE EXCEPTION 'Confirmar explícitamente si hubo descarte y su cantidad'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER recepcion_valida BEFORE INSERT OR UPDATE ON agro.recepcion_planta FOR EACH ROW EXECUTE FUNCTION agro.validar_recepcion();
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA agro FROM PUBLIC;
COMMIT;
