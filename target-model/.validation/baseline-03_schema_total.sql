-- AGRO EXPORTACIONES | modelo propuesto tras inspección del prototipo, 25/10/2026 (Lima).

-- PostgreSQL. Instalación NUEVA en schema agro. No es una migración del sistema desplegado.

-- No elimina ni reemplaza objetos existentes. Si agro ya existe, se aborta.

-- Los valores UIT no se precargan: configurar después de validar el parámetro aplicable.

BEGIN;

CREATE SCHEMA agro;

SET LOCAL search_path = agro, public;

-- Identidad única de productores, familiares y conductores.

CREATE TABLE personas (
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

CREATE TABLE roles (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(40) NOT NULL,
  UNIQUE (nombre)
);

-- Cuenta asociada a una persona; no se crea una cuenta por cada participación comercial.

CREATE TABLE usuarios (
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

CREATE TABLE archivos (
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

CREATE TABLE sesiones_usuario (
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

CREATE TABLE parametros_uit (
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

CREATE TABLE frutas (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  nombre varchar(80) NOT NULL,
  UNIQUE (nombre)
);

-- Variedades pertenecientes a una fruta.

CREATE TABLE variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  fruta_id bigint NOT NULL,
  nombre varchar(100) NOT NULL,
  UNIQUE (fruta_id, nombre)
);

-- Campaña con sus fechas, responsable y cierre manual.

CREATE TABLE campanias (
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

CREATE TABLE campania_variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  campania_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (campania_id, variedad_id)
);

-- Identidad comercial del proveedor principal.

CREATE TABLE proveedores (
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

CREATE TABLE personas_proveedor (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  persona_id bigint NOT NULL,
  vinculo varchar(60) NOT NULL,
  activo boolean NOT NULL DEFAULT true,
  UNIQUE (proveedor_id, persona_id)
);

-- Frutas asociadas al padrón general.

CREATE TABLE proveedor_frutas (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  fruta_id bigint NOT NULL,
  UNIQUE (proveedor_id, fruta_id)
);

-- Variedades asociadas al padrón general.

CREATE TABLE proveedor_variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (proveedor_id, variedad_id)
);

-- Datos físicos de cada finca, independientes de la campaña.

CREATE TABLE fincas (
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

CREATE TABLE certificados_propios (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_id bigint NOT NULL,
  nombre varchar(180) NOT NULL,
  fecha_revision date,
  archivo_id bigint NOT NULL
);

-- Vinculación proveedor–campaña; aquí pertenecen rol, oferta y evaluación.

CREATE TABLE participaciones_proveedor (
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

CREATE TABLE participacion_variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  participacion_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (participacion_id, variedad_id)
);

-- Fincas vinculadas a una participación; permite conservar historial por campaña.

CREATE TABLE fincas_campania (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  participacion_id bigint NOT NULL,
  campania_id bigint NOT NULL,
  proveedor_id bigint NOT NULL,
  finca_id bigint NOT NULL,
  UNIQUE (campania_id, finca_id),
  UNIQUE (id, participacion_id)
);

-- Registro agronómico de cada finca entrevistada en una campaña.

CREATE TABLE entrevistas (
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

CREATE TABLE examenes (
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

CREATE TABLE acuerdos_compra (
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

CREATE TABLE normas (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  codigo varchar(40) NOT NULL,
  nombre varchar(180) NOT NULL,
  UNIQUE (codigo)
);

-- Certificado de campaña, costo y organismo; un certificado por campaña según la UI.

CREATE TABLE certificaciones (
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

CREATE TABLE certificacion_proveedor (
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

CREATE TABLE ampliaciones_certificacion (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  certificacion_id bigint NOT NULL,
  fecha date NOT NULL,
  kilos_adicionales numeric(14,3) NOT NULL,
  referencia varchar(180) NOT NULL,
  registrado_por bigint,
  CHECK (kilos_adicionales > 0)
);

-- Desembolsos de la certificación en su misma moneda.

CREATE TABLE pagos_certificacion (
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

CREATE TABLE clientes (
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

CREATE TABLE destinos_cliente (
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

CREATE TABLE requerimientos_comerciales (
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

CREATE TABLE requerimiento_variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  requerimiento_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  UNIQUE (requerimiento_id, variedad_id)
);

-- Varios contratos por requerimiento, con precio y moneda propios.

CREATE TABLE contratos_venta (
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

CREATE TABLE entregas_programadas (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  contrato_id bigint NOT NULL,
  destino_id bigint NOT NULL,
  fecha date NOT NULL,
  kilos_programados numeric(14,3) NOT NULL,
  observaciones text,
  CHECK (kilos_programados > 0)
);

-- Distribución programada por variedad para el programa semanal.

CREATE TABLE entrega_variedades (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  entrega_id bigint NOT NULL,
  variedad_id bigint NOT NULL,
  kilos_programados numeric(14,3) NOT NULL,
  UNIQUE (entrega_id, variedad_id),
  CHECK (kilos_programados > 0)
);

-- Nombre heredado del DBML; admite empresas e independientes.

CREATE TABLE empresas_transporte (
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

CREATE TABLE vehiculos (
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

CREATE TABLE choferes (
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

CREATE TABLE solicitudes_transporte (
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

CREATE TABLE invitaciones_transporte (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  solicitud_id bigint NOT NULL,
  empresa_id bigint NOT NULL,
  correo_snapshot varchar(180),
  estado varchar(25) NOT NULL DEFAULT 'INVITADA',
  UNIQUE (solicitud_id, empresa_id)
);

-- Propuesta de respuesta; atributos no observables por lista vacía se proponen.

CREATE TABLE cotizaciones_transporte (
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

CREATE TABLE acuerdos_transporte (
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

CREATE TABLE coordinaciones_entrega (
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

CREATE TABLE origenes_entrega (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  coordinacion_id bigint NOT NULL,
  finca_campania_id bigint NOT NULL,
  UNIQUE (coordinacion_id, finca_campania_id)
);

-- Operación de cosecha de una entrega; estado separado del despacho.

CREATE TABLE cosechas (
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

CREATE TABLE mediciones_mtd (
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

CREATE TABLE cargas (
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

CREATE TABLE proveedores_carga (
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

CREATE TABLE origenes_carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proveedor_carga_id bigint NOT NULL,
  finca_campania_id bigint NOT NULL,
  kilos_origen numeric(14,3),
  UNIQUE (proveedor_carga_id, finca_campania_id),
  CHECK (kilos_origen > 0)
);

-- Cuadrilla, anotadores y otros costos de carga; no son automáticamente gasto de transporte.

CREATE TABLE gastos_carga (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carga_id bigint NOT NULL,
  concepto varchar(150) NOT NULL,
  monto numeric(14,2) NOT NULL,
  UNIQUE (carga_id, concepto),
  CHECK (monto >= 0)
);

-- Documento de traslado y captura histórica de origen, destino y transportista.

CREATE TABLE guias_remision (
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

CREATE TABLE proveedores_guia (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  guia_id bigint NOT NULL,
  carga_id bigint NOT NULL,
  proveedor_carga_id bigint NOT NULL,
  kilos_asignados numeric(14,3) NOT NULL,
  UNIQUE (guia_id, proveedor_carga_id),
  CHECK (kilos_asignados > 0)
);

-- Selección múltiple de normas en la guía.

CREATE TABLE normas_guia (
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

CREATE TABLE recepciones_planta (
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

CREATE TABLE liquidaciones_proveedor (
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

CREATE TABLE liquidaciones_transporte (
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

CREATE TABLE gastos_transporte (
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

CREATE TABLE adelantos_transporte (
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

CREATE TABLE aplicaciones_adelanto (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  adelanto_id bigint NOT NULL,
  liquidacion_id bigint NOT NULL,
  fecha date NOT NULL,
  monto numeric(14,2) NOT NULL,
  UNIQUE (adelanto_id, liquidacion_id),
  CHECK (monto > 0)
);

-- Preparación y factura externa en una fila; preserva peso, precio y moneda facturados.

CREATE TABLE facturas_venta (
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

CREATE TABLE pagos_proveedor (
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

CREATE TABLE pagos_transporte (
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

CREATE TABLE cobros_venta (
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

ALTER TABLE pagos_proveedor ADD CONSTRAINT fk_pagos_proveedor_1 FOREIGN KEY (liquidacion_id) REFERENCES liquidaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE pagos_transporte ADD CONSTRAINT fk_pagos_transporte_2 FOREIGN KEY (liquidacion_id) REFERENCES liquidaciones_transporte (id) ON DELETE RESTRICT;

ALTER TABLE cobros_venta ADD CONSTRAINT fk_cobros_venta_3 FOREIGN KEY (factura_id) REFERENCES facturas_venta (id) ON DELETE RESTRICT;

ALTER TABLE personas ADD CONSTRAINT fk_personas_4 FOREIGN KEY (documento_archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_5 FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE RESTRICT;

ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_6 FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE RESTRICT;

ALTER TABLE archivos ADD CONSTRAINT fk_archivos_7 FOREIGN KEY (subido_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE sesiones_usuario ADD CONSTRAINT fk_sesiones_usuario_8 FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE variedades ADD CONSTRAINT fk_variedades_9 FOREIGN KEY (fruta_id) REFERENCES frutas (id) ON DELETE RESTRICT;

ALTER TABLE campanias ADD CONSTRAINT fk_campanias_10 FOREIGN KEY (fruta_id) REFERENCES frutas (id) ON DELETE RESTRICT;

ALTER TABLE campanias ADD CONSTRAINT fk_campanias_11 FOREIGN KEY (responsable_id) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE campanias ADD CONSTRAINT fk_campanias_12 FOREIGN KEY (lineamientos_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE campanias ADD CONSTRAINT fk_campanias_13 FOREIGN KEY (cerrada_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE campania_variedades ADD CONSTRAINT fk_campania_variedades_14 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE campania_variedades ADD CONSTRAINT fk_campania_variedades_15 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE proveedores ADD CONSTRAINT fk_proveedores_16 FOREIGN KEY (persona_principal_id) REFERENCES personas (id) ON DELETE RESTRICT;

ALTER TABLE personas_proveedor ADD CONSTRAINT fk_personas_proveedor_17 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE personas_proveedor ADD CONSTRAINT fk_personas_proveedor_18 FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_frutas ADD CONSTRAINT fk_proveedor_frutas_19 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_frutas ADD CONSTRAINT fk_proveedor_frutas_20 FOREIGN KEY (fruta_id) REFERENCES frutas (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_variedades ADD CONSTRAINT fk_proveedor_variedades_21 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE proveedor_variedades ADD CONSTRAINT fk_proveedor_variedades_22 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE fincas ADD CONSTRAINT fk_fincas_23 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE fincas ADD CONSTRAINT fk_fincas_24 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE certificados_propios ADD CONSTRAINT fk_certificados_propios_25 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE certificados_propios ADD CONSTRAINT fk_certificados_propios_26 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE participaciones_proveedor ADD CONSTRAINT fk_participaciones_proveedor_27 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE participaciones_proveedor ADD CONSTRAINT fk_participaciones_proveedor_28 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE participacion_variedades ADD CONSTRAINT fk_participacion_variedades_29 FOREIGN KEY (participacion_id) REFERENCES participaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE participacion_variedades ADD CONSTRAINT fk_participacion_variedades_30 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_31 FOREIGN KEY (participacion_id) REFERENCES participaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_32 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_33 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_34 FOREIGN KEY (finca_id) REFERENCES fincas (id) ON DELETE RESTRICT;

ALTER TABLE entrevistas ADD CONSTRAINT fk_entrevistas_35 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE entrevistas ADD CONSTRAINT fk_entrevistas_36 FOREIGN KEY (registrada_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE entrevistas ADD CONSTRAINT fk_entrevistas_37 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE examenes ADD CONSTRAINT fk_examenes_38 FOREIGN KEY (participacion_id) REFERENCES participaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE examenes ADD CONSTRAINT fk_examenes_39 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE examenes ADD CONSTRAINT fk_examenes_40 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_compra ADD CONSTRAINT fk_acuerdos_compra_41 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_compra ADD CONSTRAINT fk_acuerdos_compra_42 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE certificaciones ADD CONSTRAINT fk_certificaciones_43 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE certificaciones ADD CONSTRAINT fk_certificaciones_44 FOREIGN KEY (norma_id) REFERENCES normas (id) ON DELETE RESTRICT;

ALTER TABLE certificaciones ADD CONSTRAINT fk_certificaciones_45 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_46 FOREIGN KEY (certificacion_id) REFERENCES certificaciones (id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_47 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_48 FOREIGN KEY (participacion_id) REFERENCES participaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_49 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE ampliaciones_certificacion ADD CONSTRAINT fk_ampliaciones_certificacion_50 FOREIGN KEY (certificacion_id) REFERENCES certificaciones (id) ON DELETE RESTRICT;

ALTER TABLE ampliaciones_certificacion ADD CONSTRAINT fk_ampliaciones_certificacion_51 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE pagos_certificacion ADD CONSTRAINT fk_pagos_certificacion_52 FOREIGN KEY (certificacion_id) REFERENCES certificaciones (id) ON DELETE RESTRICT;

ALTER TABLE pagos_certificacion ADD CONSTRAINT fk_pagos_certificacion_53 FOREIGN KEY (comprobante_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE pagos_certificacion ADD CONSTRAINT fk_pagos_certificacion_54 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE destinos_cliente ADD CONSTRAINT fk_destinos_cliente_55 FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE RESTRICT;

ALTER TABLE requerimientos_comerciales ADD CONSTRAINT fk_requerimientos_comerciales_56 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE requerimientos_comerciales ADD CONSTRAINT fk_requerimientos_comerciales_57 FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE RESTRICT;

ALTER TABLE requerimientos_comerciales ADD CONSTRAINT fk_requerimientos_comerciales_58 FOREIGN KEY (ficha_tecnica_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE requerimiento_variedades ADD CONSTRAINT fk_requerimiento_variedades_59 FOREIGN KEY (requerimiento_id) REFERENCES requerimientos_comerciales (id) ON DELETE RESTRICT;

ALTER TABLE requerimiento_variedades ADD CONSTRAINT fk_requerimiento_variedades_60 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE contratos_venta ADD CONSTRAINT fk_contratos_venta_61 FOREIGN KEY (requerimiento_id) REFERENCES requerimientos_comerciales (id) ON DELETE RESTRICT;

ALTER TABLE contratos_venta ADD CONSTRAINT fk_contratos_venta_62 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE entregas_programadas ADD CONSTRAINT fk_entregas_programadas_63 FOREIGN KEY (contrato_id) REFERENCES contratos_venta (id) ON DELETE RESTRICT;

ALTER TABLE entregas_programadas ADD CONSTRAINT fk_entregas_programadas_64 FOREIGN KEY (destino_id) REFERENCES destinos_cliente (id) ON DELETE RESTRICT;

ALTER TABLE entrega_variedades ADD CONSTRAINT fk_entrega_variedades_65 FOREIGN KEY (entrega_id) REFERENCES entregas_programadas (id) ON DELETE RESTRICT;

ALTER TABLE entrega_variedades ADD CONSTRAINT fk_entrega_variedades_66 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE empresas_transporte ADD CONSTRAINT fk_empresas_transporte_67 FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE RESTRICT;

ALTER TABLE vehiculos ADD CONSTRAINT fk_vehiculos_68 FOREIGN KEY (empresa_id) REFERENCES empresas_transporte (id) ON DELETE RESTRICT;

ALTER TABLE choferes ADD CONSTRAINT fk_choferes_69 FOREIGN KEY (empresa_id) REFERENCES empresas_transporte (id) ON DELETE RESTRICT;

ALTER TABLE choferes ADD CONSTRAINT fk_choferes_70 FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE RESTRICT;

ALTER TABLE choferes ADD CONSTRAINT fk_choferes_71 FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE solicitudes_transporte ADD CONSTRAINT fk_solicitudes_transporte_72 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE solicitudes_transporte ADD CONSTRAINT fk_solicitudes_transporte_73 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE invitaciones_transporte ADD CONSTRAINT fk_invitaciones_transporte_74 FOREIGN KEY (solicitud_id) REFERENCES solicitudes_transporte (id) ON DELETE RESTRICT;

ALTER TABLE invitaciones_transporte ADD CONSTRAINT fk_invitaciones_transporte_75 FOREIGN KEY (empresa_id) REFERENCES empresas_transporte (id) ON DELETE RESTRICT;

ALTER TABLE cotizaciones_transporte ADD CONSTRAINT fk_cotizaciones_transporte_76 FOREIGN KEY (invitacion_id) REFERENCES invitaciones_transporte (id) ON DELETE RESTRICT;

ALTER TABLE cotizaciones_transporte ADD CONSTRAINT fk_cotizaciones_transporte_77 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_transporte ADD CONSTRAINT fk_acuerdos_transporte_78 FOREIGN KEY (campania_id) REFERENCES campanias (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_transporte ADD CONSTRAINT fk_acuerdos_transporte_79 FOREIGN KEY (empresa_id) REFERENCES empresas_transporte (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_transporte ADD CONSTRAINT fk_acuerdos_transporte_80 FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones_transporte (id) ON DELETE RESTRICT;

ALTER TABLE acuerdos_transporte ADD CONSTRAINT fk_acuerdos_transporte_81 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_82 FOREIGN KEY (entrega_id) REFERENCES entregas_programadas (id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_83 FOREIGN KEY (acuerdo_transporte_id) REFERENCES acuerdos_transporte (id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_84 FOREIGN KEY (empresa_id) REFERENCES empresas_transporte (id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_85 FOREIGN KEY (chofer_id) REFERENCES choferes (id) ON DELETE RESTRICT;

ALTER TABLE origenes_entrega ADD CONSTRAINT fk_origenes_entrega_86 FOREIGN KEY (coordinacion_id) REFERENCES coordinaciones_entrega (id) ON DELETE RESTRICT;

ALTER TABLE origenes_entrega ADD CONSTRAINT fk_origenes_entrega_87 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE cosechas ADD CONSTRAINT fk_cosechas_88 FOREIGN KEY (entrega_id) REFERENCES entregas_programadas (id) ON DELETE RESTRICT;

ALTER TABLE cosechas ADD CONSTRAINT fk_cosechas_89 FOREIGN KEY (evidencia_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_90 FOREIGN KEY (cosecha_id) REFERENCES cosechas (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_91 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE analisis_calidad ADD CONSTRAINT fk_analisis_calidad_92 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE mediciones_mtd ADD CONSTRAINT fk_mediciones_mtd_93 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE mediciones_mtd ADD CONSTRAINT fk_mediciones_mtd_94 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE mediciones_mtd ADD CONSTRAINT fk_mediciones_mtd_95 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE cargas ADD CONSTRAINT fk_cargas_96 FOREIGN KEY (coordinacion_id) REFERENCES coordinaciones_entrega (id) ON DELETE RESTRICT;

ALTER TABLE cargas ADD CONSTRAINT fk_cargas_97 FOREIGN KEY (guia_salida_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_carga ADD CONSTRAINT fk_proveedores_carga_98 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_carga ADD CONSTRAINT fk_proveedores_carga_99 FOREIGN KEY (participacion_id) REFERENCES participaciones_proveedor (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_carga ADD CONSTRAINT fk_proveedores_carga_100 FOREIGN KEY (variedad_id) REFERENCES variedades (id) ON DELETE RESTRICT;

ALTER TABLE origenes_carga ADD CONSTRAINT fk_origenes_carga_101 FOREIGN KEY (proveedor_carga_id) REFERENCES proveedores_carga (id) ON DELETE RESTRICT;

ALTER TABLE origenes_carga ADD CONSTRAINT fk_origenes_carga_102 FOREIGN KEY (finca_campania_id) REFERENCES fincas_campania (id) ON DELETE RESTRICT;

ALTER TABLE gastos_carga ADD CONSTRAINT fk_gastos_carga_103 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE guias_remision ADD CONSTRAINT fk_guias_remision_104 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE guias_remision ADD CONSTRAINT fk_guias_remision_105 FOREIGN KEY (finca_partida_id) REFERENCES fincas (id) ON DELETE RESTRICT;

ALTER TABLE guias_remision ADD CONSTRAINT fk_guias_remision_106 FOREIGN KEY (destino_id) REFERENCES destinos_cliente (id) ON DELETE RESTRICT;

ALTER TABLE guias_remision ADD CONSTRAINT fk_guias_remision_107 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_guia ADD CONSTRAINT fk_proveedores_guia_108 FOREIGN KEY (guia_id) REFERENCES guias_remision (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_guia ADD CONSTRAINT fk_proveedores_guia_109 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE proveedores_guia ADD CONSTRAINT fk_proveedores_guia_110 FOREIGN KEY (proveedor_carga_id) REFERENCES proveedores_carga (id) ON DELETE RESTRICT;

ALTER TABLE normas_guia ADD CONSTRAINT fk_normas_guia_111 FOREIGN KEY (guia_id) REFERENCES guias_remision (id) ON DELETE RESTRICT;

ALTER TABLE normas_guia ADD CONSTRAINT fk_normas_guia_112 FOREIGN KEY (norma_id) REFERENCES normas (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_113 FOREIGN KEY (coordinacion_id) REFERENCES coordinaciones_entrega (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_114 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_115 FOREIGN KEY (chofer_id) REFERENCES choferes (id) ON DELETE RESTRICT;

ALTER TABLE recepciones_planta ADD CONSTRAINT fk_recepciones_planta_116 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE recepciones_planta ADD CONSTRAINT fk_recepciones_planta_117 FOREIGN KEY (chofer_id) REFERENCES choferes (id) ON DELETE RESTRICT;

ALTER TABLE recepciones_planta ADD CONSTRAINT fk_recepciones_planta_118 FOREIGN KEY (evidencia_descarte_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE recepciones_planta ADD CONSTRAINT fk_recepciones_planta_119 FOREIGN KEY (reporte_recepcion_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_120 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_121 FOREIGN KEY (proveedor_id) REFERENCES proveedores (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_122 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_123 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_transporte ADD CONSTRAINT fk_liquidaciones_transporte_124 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_transporte ADD CONSTRAINT fk_liquidaciones_transporte_125 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_transporte ADD CONSTRAINT fk_liquidaciones_transporte_126 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE gastos_transporte ADD CONSTRAINT fk_gastos_transporte_127 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE adelantos_transporte ADD CONSTRAINT fk_adelantos_transporte_128 FOREIGN KEY (acuerdo_id) REFERENCES acuerdos_transporte (id) ON DELETE RESTRICT;

ALTER TABLE adelantos_transporte ADD CONSTRAINT fk_adelantos_transporte_129 FOREIGN KEY (comprobante_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE aplicaciones_adelanto ADD CONSTRAINT fk_aplicaciones_adelanto_130 FOREIGN KEY (adelanto_id) REFERENCES adelantos_transporte (id) ON DELETE RESTRICT;

ALTER TABLE facturas_venta ADD CONSTRAINT fk_facturas_venta_131 FOREIGN KEY (carga_id) REFERENCES cargas (id) ON DELETE RESTRICT;

ALTER TABLE facturas_venta ADD CONSTRAINT fk_facturas_venta_132 FOREIGN KEY (archivo_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE pagos_proveedor ADD CONSTRAINT fk_pagos_proveedor_133 FOREIGN KEY (comprobante_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE pagos_proveedor ADD CONSTRAINT fk_pagos_proveedor_134 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE pagos_transporte ADD CONSTRAINT fk_pagos_transporte_135 FOREIGN KEY (comprobante_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE pagos_transporte ADD CONSTRAINT fk_pagos_transporte_136 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE cobros_venta ADD CONSTRAINT fk_cobros_venta_137 FOREIGN KEY (comprobante_id) REFERENCES archivos (id) ON DELETE RESTRICT;

ALTER TABLE cobros_venta ADD CONSTRAINT fk_cobros_venta_138 FOREIGN KEY (registrado_por) REFERENCES usuarios (id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_139 FOREIGN KEY (participacion_id, campania_id, proveedor_id) REFERENCES participaciones_proveedor (id, campania_id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE fincas_campania ADD CONSTRAINT fk_fincas_campania_140 FOREIGN KEY (finca_id, proveedor_id) REFERENCES fincas (id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE examenes ADD CONSTRAINT fk_examenes_141 FOREIGN KEY (finca_campania_id, participacion_id) REFERENCES fincas_campania (id, participacion_id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_142 FOREIGN KEY (certificacion_id, campania_id) REFERENCES certificaciones (id, campania_id) ON DELETE RESTRICT;

ALTER TABLE certificacion_proveedor ADD CONSTRAINT fk_certificacion_proveedor_143 FOREIGN KEY (participacion_id, campania_id, proveedor_id) REFERENCES participaciones_proveedor (id, campania_id, proveedor_id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_144 FOREIGN KEY (acuerdo_transporte_id, empresa_id) REFERENCES acuerdos_transporte (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_145 FOREIGN KEY (vehiculo_id, empresa_id) REFERENCES vehiculos (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE coordinaciones_entrega ADD CONSTRAINT fk_coordinaciones_entrega_146 FOREIGN KEY (chofer_id, empresa_id) REFERENCES choferes (id, empresa_id) ON DELETE RESTRICT;

ALTER TABLE historial_chofer ADD CONSTRAINT fk_historial_chofer_147 FOREIGN KEY (carga_id, coordinacion_id) REFERENCES cargas (id, coordinacion_id) ON DELETE RESTRICT;

ALTER TABLE proveedores_guia ADD CONSTRAINT fk_proveedores_guia_148 FOREIGN KEY (guia_id, carga_id) REFERENCES guias_remision (id, carga_id) ON DELETE RESTRICT;

ALTER TABLE proveedores_guia ADD CONSTRAINT fk_proveedores_guia_149 FOREIGN KEY (proveedor_carga_id, carga_id) REFERENCES proveedores_carga (id, carga_id) ON DELETE RESTRICT;

ALTER TABLE liquidaciones_proveedor ADD CONSTRAINT fk_liquidaciones_proveedor_150 FOREIGN KEY (proveedor_id, persona_liquidacion_id) REFERENCES personas_proveedor (proveedor_id, persona_id) ON DELETE RESTRICT;

ALTER TABLE aplicaciones_adelanto ADD CONSTRAINT fk_aplicaciones_adelanto_151 FOREIGN KEY (liquidacion_id) REFERENCES liquidaciones_transporte (id) ON DELETE RESTRICT;

CREATE INDEX ix_pagos_proveedor_1 ON pagos_proveedor (liquidacion_id);

CREATE INDEX ix_pagos_transporte_2 ON pagos_transporte (liquidacion_id);

CREATE INDEX ix_cobros_venta_3 ON cobros_venta (factura_id);

CREATE INDEX ix_personas_4 ON personas (documento_archivo_id);

CREATE INDEX ix_usuarios_5 ON usuarios (persona_id);

CREATE INDEX ix_usuarios_6 ON usuarios (rol_id);

CREATE INDEX ix_archivos_7 ON archivos (subido_por);

CREATE INDEX ix_sesiones_usuario_8 ON sesiones_usuario (usuario_id);

CREATE INDEX ix_variedades_9 ON variedades (fruta_id);

CREATE INDEX ix_campanias_10 ON campanias (fruta_id);

CREATE INDEX ix_campanias_11 ON campanias (responsable_id);

CREATE INDEX ix_campanias_12 ON campanias (lineamientos_id);

CREATE INDEX ix_campanias_13 ON campanias (cerrada_por);

CREATE INDEX ix_campania_variedades_14 ON campania_variedades (campania_id);

CREATE INDEX ix_campania_variedades_15 ON campania_variedades (variedad_id);

CREATE INDEX ix_proveedores_16 ON proveedores (persona_principal_id);

CREATE INDEX ix_personas_proveedor_17 ON personas_proveedor (proveedor_id);

CREATE INDEX ix_personas_proveedor_18 ON personas_proveedor (persona_id);

CREATE INDEX ix_proveedor_frutas_19 ON proveedor_frutas (proveedor_id);

CREATE INDEX ix_proveedor_frutas_20 ON proveedor_frutas (fruta_id);

CREATE INDEX ix_proveedor_variedades_21 ON proveedor_variedades (proveedor_id);

CREATE INDEX ix_proveedor_variedades_22 ON proveedor_variedades (variedad_id);

CREATE INDEX ix_fincas_23 ON fincas (proveedor_id);

CREATE INDEX ix_fincas_24 ON fincas (variedad_id);

CREATE INDEX ix_certificados_propios_25 ON certificados_propios (proveedor_id);

CREATE INDEX ix_certificados_propios_26 ON certificados_propios (archivo_id);

CREATE INDEX ix_participaciones_proveedor_27 ON participaciones_proveedor (campania_id);

CREATE INDEX ix_participaciones_proveedor_28 ON participaciones_proveedor (proveedor_id);

CREATE INDEX ix_participacion_variedades_29 ON participacion_variedades (participacion_id);

CREATE INDEX ix_participacion_variedades_30 ON participacion_variedades (variedad_id);

CREATE INDEX ix_fincas_campania_31 ON fincas_campania (participacion_id);

CREATE INDEX ix_fincas_campania_32 ON fincas_campania (campania_id);

CREATE INDEX ix_fincas_campania_33 ON fincas_campania (proveedor_id);

CREATE INDEX ix_fincas_campania_34 ON fincas_campania (finca_id);

CREATE INDEX ix_entrevistas_35 ON entrevistas (finca_campania_id);

CREATE INDEX ix_entrevistas_36 ON entrevistas (registrada_por);

CREATE INDEX ix_entrevistas_37 ON entrevistas (archivo_id);

CREATE INDEX ix_examenes_38 ON examenes (participacion_id);

CREATE INDEX ix_examenes_39 ON examenes (finca_campania_id);

CREATE INDEX ix_examenes_40 ON examenes (archivo_id);

CREATE INDEX ix_acuerdos_compra_41 ON acuerdos_compra (finca_campania_id);

CREATE INDEX ix_acuerdos_compra_42 ON acuerdos_compra (variedad_id);

CREATE INDEX ix_certificaciones_43 ON certificaciones (campania_id);

CREATE INDEX ix_certificaciones_44 ON certificaciones (norma_id);

CREATE INDEX ix_certificaciones_45 ON certificaciones (archivo_id);

CREATE INDEX ix_certificacion_proveedor_46 ON certificacion_proveedor (certificacion_id);

CREATE INDEX ix_certificacion_proveedor_47 ON certificacion_proveedor (campania_id);

CREATE INDEX ix_certificacion_proveedor_48 ON certificacion_proveedor (participacion_id);

CREATE INDEX ix_certificacion_proveedor_49 ON certificacion_proveedor (proveedor_id);

CREATE INDEX ix_ampliaciones_certificacion_50 ON ampliaciones_certificacion (certificacion_id);

CREATE INDEX ix_ampliaciones_certificacion_51 ON ampliaciones_certificacion (registrado_por);

CREATE INDEX ix_pagos_certificacion_52 ON pagos_certificacion (certificacion_id);

CREATE INDEX ix_pagos_certificacion_53 ON pagos_certificacion (comprobante_id);

CREATE INDEX ix_pagos_certificacion_54 ON pagos_certificacion (registrado_por);

CREATE INDEX ix_destinos_cliente_55 ON destinos_cliente (cliente_id);

CREATE INDEX ix_requerimientos_comerciales_56 ON requerimientos_comerciales (campania_id);

CREATE INDEX ix_requerimientos_comerciales_57 ON requerimientos_comerciales (cliente_id);

CREATE INDEX ix_requerimientos_comerciales_58 ON requerimientos_comerciales (ficha_tecnica_id);

CREATE INDEX ix_requerimiento_variedades_59 ON requerimiento_variedades (requerimiento_id);

CREATE INDEX ix_requerimiento_variedades_60 ON requerimiento_variedades (variedad_id);

CREATE INDEX ix_contratos_venta_61 ON contratos_venta (requerimiento_id);

CREATE INDEX ix_contratos_venta_62 ON contratos_venta (archivo_id);

CREATE INDEX ix_entregas_programadas_63 ON entregas_programadas (contrato_id);

CREATE INDEX ix_entregas_programadas_64 ON entregas_programadas (destino_id);

CREATE INDEX ix_entrega_variedades_65 ON entrega_variedades (entrega_id);

CREATE INDEX ix_entrega_variedades_66 ON entrega_variedades (variedad_id);

CREATE INDEX ix_empresas_transporte_67 ON empresas_transporte (persona_id);

CREATE INDEX ix_vehiculos_68 ON vehiculos (empresa_id);

CREATE INDEX ix_choferes_69 ON choferes (empresa_id);

CREATE INDEX ix_choferes_70 ON choferes (persona_id);

CREATE INDEX ix_choferes_71 ON choferes (usuario_id);

CREATE INDEX ix_solicitudes_transporte_72 ON solicitudes_transporte (campania_id);

CREATE INDEX ix_solicitudes_transporte_73 ON solicitudes_transporte (archivo_id);

CREATE INDEX ix_invitaciones_transporte_74 ON invitaciones_transporte (solicitud_id);

CREATE INDEX ix_invitaciones_transporte_75 ON invitaciones_transporte (empresa_id);

CREATE INDEX ix_cotizaciones_transporte_76 ON cotizaciones_transporte (invitacion_id);

CREATE INDEX ix_cotizaciones_transporte_77 ON cotizaciones_transporte (archivo_id);

CREATE INDEX ix_acuerdos_transporte_78 ON acuerdos_transporte (campania_id);

CREATE INDEX ix_acuerdos_transporte_79 ON acuerdos_transporte (empresa_id);

CREATE INDEX ix_acuerdos_transporte_80 ON acuerdos_transporte (cotizacion_id);

CREATE INDEX ix_acuerdos_transporte_81 ON acuerdos_transporte (archivo_id);

CREATE INDEX ix_coordinaciones_entrega_82 ON coordinaciones_entrega (entrega_id);

CREATE INDEX ix_coordinaciones_entrega_83 ON coordinaciones_entrega (acuerdo_transporte_id);

CREATE INDEX ix_coordinaciones_entrega_84 ON coordinaciones_entrega (empresa_id);

CREATE INDEX ix_coordinaciones_entrega_85 ON coordinaciones_entrega (chofer_id);

CREATE INDEX ix_origenes_entrega_86 ON origenes_entrega (coordinacion_id);

CREATE INDEX ix_origenes_entrega_87 ON origenes_entrega (finca_campania_id);

CREATE INDEX ix_cosechas_88 ON cosechas (entrega_id);

CREATE INDEX ix_cosechas_89 ON cosechas (evidencia_id);

CREATE INDEX ix_analisis_calidad_90 ON analisis_calidad (cosecha_id);

CREATE INDEX ix_analisis_calidad_91 ON analisis_calidad (finca_campania_id);

CREATE INDEX ix_analisis_calidad_92 ON analisis_calidad (archivo_id);

CREATE INDEX ix_mediciones_mtd_93 ON mediciones_mtd (finca_campania_id);

CREATE INDEX ix_mediciones_mtd_94 ON mediciones_mtd (archivo_id);

CREATE INDEX ix_mediciones_mtd_95 ON mediciones_mtd (registrado_por);

CREATE INDEX ix_cargas_96 ON cargas (coordinacion_id);

CREATE INDEX ix_cargas_97 ON cargas (guia_salida_id);

CREATE INDEX ix_proveedores_carga_98 ON proveedores_carga (carga_id);

CREATE INDEX ix_proveedores_carga_99 ON proveedores_carga (participacion_id);

CREATE INDEX ix_proveedores_carga_100 ON proveedores_carga (variedad_id);

CREATE INDEX ix_origenes_carga_101 ON origenes_carga (proveedor_carga_id);

CREATE INDEX ix_origenes_carga_102 ON origenes_carga (finca_campania_id);

CREATE INDEX ix_gastos_carga_103 ON gastos_carga (carga_id);

CREATE INDEX ix_guias_remision_104 ON guias_remision (carga_id);

CREATE INDEX ix_guias_remision_105 ON guias_remision (finca_partida_id);

CREATE INDEX ix_guias_remision_106 ON guias_remision (destino_id);

CREATE INDEX ix_guias_remision_107 ON guias_remision (archivo_id);

CREATE INDEX ix_proveedores_guia_108 ON proveedores_guia (guia_id);

CREATE INDEX ix_proveedores_guia_109 ON proveedores_guia (carga_id);

CREATE INDEX ix_proveedores_guia_110 ON proveedores_guia (proveedor_carga_id);

CREATE INDEX ix_normas_guia_111 ON normas_guia (guia_id);

CREATE INDEX ix_normas_guia_112 ON normas_guia (norma_id);

CREATE INDEX ix_historial_chofer_113 ON historial_chofer (coordinacion_id);

CREATE INDEX ix_historial_chofer_114 ON historial_chofer (carga_id);

CREATE INDEX ix_historial_chofer_115 ON historial_chofer (chofer_id);

CREATE INDEX ix_recepciones_planta_116 ON recepciones_planta (carga_id);

CREATE INDEX ix_recepciones_planta_117 ON recepciones_planta (chofer_id);

CREATE INDEX ix_recepciones_planta_118 ON recepciones_planta (evidencia_descarte_id);

CREATE INDEX ix_recepciones_planta_119 ON recepciones_planta (reporte_recepcion_id);

CREATE INDEX ix_liquidaciones_proveedor_120 ON liquidaciones_proveedor (carga_id);

CREATE INDEX ix_liquidaciones_proveedor_121 ON liquidaciones_proveedor (proveedor_id);

CREATE INDEX ix_liquidaciones_proveedor_122 ON liquidaciones_proveedor (registrado_por);

CREATE INDEX ix_liquidaciones_proveedor_123 ON liquidaciones_proveedor (archivo_id);

CREATE INDEX ix_liquidaciones_transporte_124 ON liquidaciones_transporte (carga_id);

CREATE INDEX ix_liquidaciones_transporte_125 ON liquidaciones_transporte (registrado_por);

CREATE INDEX ix_liquidaciones_transporte_126 ON liquidaciones_transporte (archivo_id);

CREATE INDEX ix_gastos_transporte_127 ON gastos_transporte (carga_id);

CREATE INDEX ix_adelantos_transporte_128 ON adelantos_transporte (acuerdo_id);

CREATE INDEX ix_adelantos_transporte_129 ON adelantos_transporte (comprobante_id);

CREATE INDEX ix_aplicaciones_adelanto_130 ON aplicaciones_adelanto (adelanto_id);

CREATE INDEX ix_facturas_venta_131 ON facturas_venta (carga_id);

CREATE INDEX ix_facturas_venta_132 ON facturas_venta (archivo_id);

CREATE INDEX ix_pagos_proveedor_133 ON pagos_proveedor (comprobante_id);

CREATE INDEX ix_pagos_proveedor_134 ON pagos_proveedor (registrado_por);

CREATE INDEX ix_pagos_transporte_135 ON pagos_transporte (comprobante_id);

CREATE INDEX ix_pagos_transporte_136 ON pagos_transporte (registrado_por);

CREATE INDEX ix_cobros_venta_137 ON cobros_venta (comprobante_id);

CREATE INDEX ix_cobros_venta_138 ON cobros_venta (registrado_por);

CREATE INDEX ix_fincas_campania_139 ON fincas_campania (participacion_id, campania_id, proveedor_id);

CREATE INDEX ix_fincas_campania_140 ON fincas_campania (finca_id, proveedor_id);

CREATE INDEX ix_examenes_141 ON examenes (finca_campania_id, participacion_id);

CREATE INDEX ix_certificacion_proveedor_142 ON certificacion_proveedor (certificacion_id, campania_id);

CREATE INDEX ix_certificacion_proveedor_143 ON certificacion_proveedor (participacion_id, campania_id, proveedor_id);

CREATE INDEX ix_coordinaciones_entrega_144 ON coordinaciones_entrega (acuerdo_transporte_id, empresa_id);

CREATE INDEX ix_coordinaciones_entrega_145 ON coordinaciones_entrega (vehiculo_id, empresa_id);

CREATE INDEX ix_coordinaciones_entrega_146 ON coordinaciones_entrega (chofer_id, empresa_id);

CREATE INDEX ix_historial_chofer_147 ON historial_chofer (carga_id, coordinacion_id);

CREATE INDEX ix_proveedores_guia_148 ON proveedores_guia (guia_id, carga_id);

CREATE INDEX ix_proveedores_guia_149 ON proveedores_guia (proveedor_carga_id, carga_id);

CREATE INDEX ix_liquidaciones_proveedor_150 ON liquidaciones_proveedor (proveedor_id, persona_liquidacion_id);

CREATE INDEX ix_aplicaciones_adelanto_151 ON aplicaciones_adelanto (liquidacion_id);

CREATE INDEX ix_eventos_fecha ON historial_chofer (coordinacion_id, fecha_hora DESC, id DESC);

CREATE INDEX ix_uit_persona_fecha ON liquidaciones_proveedor (persona_liquidacion_id, fecha);

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
