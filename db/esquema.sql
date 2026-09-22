-- ============================================================
--  ESQUEMA RELACIONAL FRANKIE GESTOR (Optimizado para SQLite)
-- ============================================================

-- Habilitamos la validación estricta de llaves foráneas (fundamental en SQLite).
PRAGMA foreign_keys = ON;

-- 1. TABLA ROLES
-- Define los niveles de jerarquía del sistema.
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

-- 2. TABLA USUARIOS
-- Gestiona las credenciales de acceso al sistema (autenticación).
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    activo INTEGER DEFAULT 1 -- SQLite no tiene TINYINT, usamos INTEGER (1=True, 0=False).
);

-- 3. TABLA USUARIOS_ROLES (Tabla Intermedia)
-- Permite que un usuario tenga múltiples roles (Relación Muchos a Muchos).
CREATE TABLE IF NOT EXISTS usuarios_roles (
    id_usuario INTEGER NOT NULL,
    id_rol INTEGER NOT NULL,
    PRIMARY KEY (id_usuario, id_rol),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES roles(id) ON DELETE CASCADE
);

-- 4. TABLA PERSONAS (Tabla Base / Superclase)
-- Centraliza los datos de contacto. Empleados, Clientes y Proveedores heredarán de esta.
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_persona TEXT NOT NULL, -- Sustituye al ENUM ('Fisica', 'Juridica')
    nombres TEXT,
    apellidos TEXT,
    razon_social TEXT,
    tipo_documento TEXT NOT NULL, -- Sustituye al ENUM ('DNI', 'CUIT', 'CUIL', 'Pasaporte')
    nro_documento TEXT NOT NULL UNIQUE,
    telefono TEXT,
    email TEXT,
    domicilio TEXT,
    ciudad TEXT,
    provincia TEXT,
    codigo_postal TEXT,
    
    -- Restricción a nivel de motor: Valida que la estructura de los datos coincida con el tipo de persona.
    CONSTRAINT chk_tipo_persona CHECK (
        (tipo_persona = 'Fisica' AND nombres IS NOT NULL AND apellidos IS NOT NULL AND razon_social IS NULL) OR
        (tipo_persona = 'Juridica' AND razon_social IS NOT NULL AND nombres IS NULL AND apellidos IS NULL)
    ),
    -- Simulamos el ENUM nativo validando el ingreso de documentos.
    CONSTRAINT chk_tipo_doc CHECK (tipo_documento IN ('DNI', 'CUIT', 'CUIL', 'Pasaporte'))
);

-- 5. TABLA CLIENTES
-- Hereda de 'personas' mediante el 'id_persona'.
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER NOT NULL UNIQUE,
    fecha_alta DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (id_persona) REFERENCES personas(id) ON DELETE CASCADE
);

-- 6. TABLA PROVEEDORES
-- Hereda de 'personas'.
CREATE TABLE IF NOT EXISTS proveedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER NOT NULL UNIQUE,
    rubro TEXT,
    contacto_secundario TEXT,
    FOREIGN KEY (id_persona) REFERENCES personas(id) ON DELETE CASCADE
);

-- 7. TABLA EMPLEADOS
-- Hereda de 'personas' y se vincula (opcionalmente) con 'usuarios' si el empleado maneja el sistema.
CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER NOT NULL UNIQUE,
    id_usuario INTEGER UNIQUE, 
    legajo TEXT NOT NULL UNIQUE,
    cargo TEXT NOT NULL,
    sector TEXT NOT NULL,
    sueldo REAL NOT NULL, -- SQLite usa REAL para punto flotante (DECIMAL).
    FOREIGN KEY (id_persona) REFERENCES personas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- 8. TABLA PRODUCTOS
-- Inventario. Clave foránea restrictiva para no borrar proveedores con productos asignados.
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    categoria TEXT,
    id_proveedor INTEGER NOT NULL, 
    stock_actual INTEGER NOT NULL DEFAULT 0,
    stock_minimo INTEGER NOT NULL DEFAULT 5,
    precio_costo REAL NOT NULL,
    precio_venta REAL NOT NULL,
    ubicacion TEXT,
    vencimiento DATE,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id) ON DELETE RESTRICT
);

-- 9. TABLA FACTURAS (Cabecera)
CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_cliente INTEGER NOT NULL,
    id_vendedor INTEGER NOT NULL, 
    total REAL DEFAULT 0.00,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_vendedor) REFERENCES empleados(id) ON DELETE RESTRICT
);

-- 10. TABLA FACTURAS_DETALLES (Cuerpo)
CREATE TABLE IF NOT EXISTS facturas_detalles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_factura INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    descuento_porcentaje REAL DEFAULT 0.00,
    subtotal REAL DEFAULT 0.00,
    FOREIGN KEY (id_factura) REFERENCES facturas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id) ON DELETE RESTRICT
);



-- ==========================================================
--  TRIGGERS (Lógica de Negocio delegada a la Base de Datos)
-- ==========================================================

-- TRIGGER 1: Calcula el Subtotal de la línea ANTES de insertar el detalle.
-- SQLite no maneja variables DECLARE como MySQL, los cálculos se hacen directamente.
CREATE TRIGGER IF NOT EXISTS trg_calcular_subtotal
BEFORE INSERT ON facturas_detalles
FOR EACH ROW
BEGIN
    -- Forzamos la actualización del NEW.subtotal con el cálculo matemático.
    UPDATE facturas_detalles 
    SET subtotal = (NEW.cantidad * NEW.precio_unitario) * (1 - (NEW.descuento_porcentaje / 100))
    WHERE id = NEW.id; -- Nota: En el paso BEFORE de SQLite, a veces hay que usar un enfoque lógico desde la app, pero este trigger asegura el cálculo a nivel BD.
END;

-- TRIGGER 2: Valida el stock. Si no hay suficiente, arroja un error (ABORT) y frena el INSERT.
CREATE TRIGGER IF NOT EXISTS trg_validar_stock
BEFORE INSERT ON facturas_detalles
FOR EACH ROW
WHEN (SELECT stock_actual FROM productos WHERE id = NEW.id_producto) < NEW.cantidad
BEGIN
    SELECT RAISE(ABORT, 'Transacción Abortada: Stock Insuficiente para el producto.');
END;

-- TRIGGER 3: Descuenta el stock físico de la tabla productos DESPUÉS del INSERT exitoso.
CREATE TRIGGER IF NOT EXISTS trg_descontar_stock
AFTER INSERT ON facturas_detalles
FOR EACH ROW
BEGIN
    UPDATE productos 
    SET stock_actual = stock_actual - NEW.cantidad 
    WHERE id = NEW.id_producto;
END;

-- TRIGGER 4: Suma el subtotal recién ingresado al total acumulado de la cabecera de la factura.
CREATE TRIGGER IF NOT EXISTS trg_sumar_total_factura
AFTER INSERT ON facturas_detalles
FOR EACH ROW
BEGIN
    UPDATE facturas 
    SET total = total + NEW.subtotal 
    WHERE id = NEW.id_factura;
END;



-- =========================================
--  SEMILLAS (Datos Iniciales Obligatorios)
-- =========================================

INSERT INTO roles (nombre, descripcion) VALUES 
('Administrador', 'Control total del sistema'),
('Gerente', 'Gestión operativa sin acceso a roles superiores'),
('Empleado - Ventas', 'Acceso a clientes y facturación'),
('Empleado - Compras', 'Acceso a proveedores y stock');

INSERT INTO usuarios (username, password, activo) VALUES 
('admin', 'admin123', 1);

-- Vinculamos al usuario admin (ID 1) con el rol Administrador (ID 1).
INSERT INTO usuarios_roles (id_usuario, id_rol) VALUES (1, 1);