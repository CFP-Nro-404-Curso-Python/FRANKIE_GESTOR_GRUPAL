import sqlite3
from typing import List, Optional, Dict, Tuple

# =============================================================================
# 1. CAPA DE DOMINIO (ENTIDADES)
# =============================================================================
class Persona:
    def __init__(self, nombre: str, apellido: str, dni: str):
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni

class Cliente(Persona):
    def __init__(
        self,
        nombre: str,
        apellido: str,
        dni: str,
        cuit_cliente: str,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        id_cliente: Optional[int] = None,
        id_persona: Optional[int] = None
    ):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni)
        self.id_cliente = id_cliente
        self.id_persona = id_persona or id_cliente
        self.cuit_cliente = cuit_cliente
        self.email = email
        self.telefono = telefono

class DetalleFactura:
    def __init__(
        self,
        id_producto: int,
        cantidad: int,
        precio_unitario: float,
        descuento_porcentaje: float = 0.0,
        subtotal: float = 0.0,
        id_detalle: Optional[int] = None,
        id_factura: Optional[int] = None
    ):
        self.id_detalle = id_detalle
        self.id_factura = id_factura
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.descuento_porcentaje = descuento_porcentaje
        self.subtotal = subtotal

class Factura:
    def __init__(
        self,
        id_factura: Optional[int],
        cliente: Cliente,
        id_vendedor: int,
        fecha: Optional[str] = None,
        subtotal_base: float = 0.0,
        monto_iva: float = 0.0,
        total: float = 0.0,
        detalles: Optional[List[DetalleFactura]] = None,
        estado: str = "Emitida"
    ):
        self.id_factura = id_factura
        self.cliente = cliente
        self.id_vendedor = id_vendedor
        self.fecha = fecha
        self.subtotal_base = subtotal_base
        self.monto_iva = monto_iva
        self.total = total
        self.detalles = detalles if detalles is not None else []
        self.estado = estado

# =============================================================================
# 2. CAPA DE INFRAESTRUCTURA (BASE DE DATOS Y REPOSITORIO)
# =============================================================================
class ConexionDB:
    DB_NAME = ":memory:"  # Base de datos ligera en memoria para tests

    def __init__(self, conn=None):
        self.conn = conn

    def __enter__(self):
        if self.conn:
            return self.conn
        self.conn = sqlite3.connect(ConexionDB.DB_NAME)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class RepositorioVentas:
    def __init__(self, conexion_db):
        self.conexion_db = conexion_db

    def obtener_cliente_por_id(self, id_cliente: int) -> Optional[Cliente]:
        with self.conexion_db as db:
            cursor = db.cursor()
            cursor.execute(
                """SELECT c.id, p.nombres, p.apellidos, p.nro_documento, p.email, p.telefono, p.id
                   FROM clientes c
                   INNER JOIN personas p ON c.id_persona = p.id
                   WHERE c.id = ?""",
                (id_cliente,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Cliente(
                id_cliente=row[0],
                nombre=row[1],
                apellido=row[2],
                dni=row[3],
                cuit_cliente=row[3],
                email=row[4],
                telefono=row[5],
                id_persona=row[6]
            )

    def guardar_factura(self, factura: Factura) -> Factura:
        if not factura.detalles:
            raise ValueError("La factura debe contener al menos un detalle.")

        with self.conexion_db as db:
            cursor = db.cursor()
            try:
                cursor.execute(
                    "INSERT INTO facturas (id_cliente, id_vendedor, total) VALUES (?, ?, ?)",
                    (factura.cliente.id_cliente, factura.id_vendedor, factura.total)
                )
                factura.id_factura = cursor.lastrowid

                for det in factura.detalles:
                    cursor.execute(
                        """INSERT INTO facturas_detalles 
                           (id_factura, id_producto, cantidad, precio_unitario, descuento_porcentaje, subtotal)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            factura.id_factura,
                            det.id_producto,
                            det.cantidad,
                            det.precio_unitario,
                            det.descuento_porcentaje,
                            det.subtotal
                        )
                    )
                    det.id_detalle = cursor.lastrowid
                    det.id_factura = factura.id_factura

                db.commit()
                return factura
            except sqlite3.IntegrityError as e:
                db.rollback()
                raise ValueError(f"Error de integridad: Verifique que el Cliente o Vendedor existan ({e})")
            except sqlite3.DatabaseError as e:
                db.rollback()
                raise ValueError(f"Rechazado por la base de datos (Stock insuficiente): {e}")

# =============================================================================
# 3. CAPA DE CONTROL / ORQUESTADOR
# =============================================================================
class OrquestadorVentas:
    PORCENTAJE_IVA = 0.21

    def __init__(self, repo_ventas: RepositorioVentas):
        self.repo = repo_ventas

    @classmethod
    def calcular_renglon(cls, cantidad: int, precio_unitario: float, descuento_porc: float) -> float:
        subtotal_bruto = cantidad * precio_unitario
        descuento_monto = subtotal_bruto * (descuento_porc / 100.0)
        return round(subtotal_bruto - descuento_monto, 2)

    @classmethod
    def calcular_totales_factura(cls, lista_detalles: List[DetalleFactura], aplicar_iva: bool = True) -> Tuple[float, float, float]:
        subtotal_base = sum(det.subtotal for det in lista_detalles)
        monto_iva = (subtotal_base * cls.PORCENTAJE_IVA) if aplicar_iva else 0.0
        total_final = subtotal_base + monto_iva
        return round(subtotal_base, 2), round(monto_iva, 2), round(total_final, 2)

    def emitir_factura(self, id_cliente: int, id_vendedor: int, items_raw: List[Dict], aplicar_iva: bool = True) -> Factura:
        cliente = self.repo.obtener_cliente_por_id(id_cliente)
        if not cliente:
            raise ValueError(f"El Cliente con ID #{id_cliente} no existe en el sistema.")

        detalles_entidad: List[DetalleFactura] = []
        for item in items_raw:
            subtotal_item = self.calcular_renglon(item["cantidad"], item["precio_unitario"], item.get("descuento", 0.0))
            det = DetalleFactura(
                id_producto=item["id_producto"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                descuento_porcentaje=item.get("descuento", 0.0),
                subtotal=subtotal_item
            )
            detalles_entidad.append(det)

        subtotal_base, monto_iva, total_final = self.calcular_totales_factura(detalles_entidad, aplicar_iva)

        factura = Factura(
            id_factura=None,
            cliente=cliente,
            id_vendedor=id_vendedor,
            subtotal_base=subtotal_base,
            monto_iva=monto_iva,
            total=total_final,
            detalles=detalles_entidad
        )

        return self.repo.guardar_factura(factura)

# =============================================================================
# 4. SUITE DE PRUEBAS AUTOMÁTICAS
# =============================================================================
def ejecutar_suite_de_pruebas():
    # Conexión temporal a memoria
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Creación de tablas y triggers de prueba
    conn.executescript("""
        CREATE TABLE personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_persona TEXT NOT NULL,
            nombres TEXT,
            apellidos TEXT,
            tipo_documento TEXT NOT NULL,
            nro_documento TEXT NOT NULL UNIQUE,
            telefono TEXT,
            email TEXT
        );

        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_persona INTEGER NOT NULL UNIQUE,
            FOREIGN KEY (id_persona) REFERENCES personas(id) ON DELETE CASCADE
        );

        CREATE TABLE empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_persona INTEGER NOT NULL UNIQUE,
            legajo TEXT NOT NULL UNIQUE
        );

        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            descripcion TEXT NOT NULL,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            precio_costo REAL NOT NULL,
            precio_venta REAL NOT NULL
        );

        CREATE TABLE facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_cliente INTEGER NOT NULL,
            id_vendedor INTEGER NOT NULL,
            total REAL DEFAULT 0.00,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id),
            FOREIGN KEY (id_vendedor) REFERENCES empleados(id)
        );

        CREATE TABLE facturas_detalles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            descuento_porcentaje REAL DEFAULT 0.00,
            subtotal REAL DEFAULT 0.00,
            FOREIGN KEY (id_factura) REFERENCES facturas(id),
            FOREIGN KEY (id_producto) REFERENCES productos(id)
        );

        -- TRIGGER 1: Validar stock
        CREATE TRIGGER trg_validar_stock
        BEFORE INSERT ON facturas_detalles
        FOR EACH ROW
        WHEN (SELECT stock_actual FROM productos WHERE id = NEW.id_producto) < NEW.cantidad
        BEGIN
            SELECT RAISE(ABORT, 'Stock insuficiente para realizar la venta.');
        END;

        -- TRIGGER 2: Descontar stock
        CREATE TRIGGER trg_descontar_stock
        AFTER INSERT ON facturas_detalles
        FOR EACH ROW
        BEGIN
            UPDATE productos
            SET stock_actual = stock_actual - NEW.cantidad
            WHERE id = NEW.id_producto;
        END;
    """)

    # Datos semilla
    conn.execute("INSERT INTO personas (tipo_persona, nombres, apellidos, tipo_documento, nro_documento) VALUES ('Fisica', 'Juan', 'Pérez', 'DNI', '30111222')")
    conn.execute("INSERT INTO clientes (id_persona) VALUES (1)")
    
    conn.execute("INSERT INTO personas (tipo_persona, nombres, apellidos, tipo_documento, nro_documento) VALUES ('Fisica', 'Carlos', 'Gómez', 'DNI', '20333444')")
    conn.execute("INSERT INTO empleados (id_persona, legajo) VALUES (2, 'EMP-001')")

    conn.execute("INSERT INTO productos (codigo, descripcion, stock_actual, precio_costo, precio_venta) VALUES ('P001', 'Teclado Mecánico', 10, 15000, 25000)")

    conn.commit()

    # Instanciado de componentes
    conexion_db = ConexionDB(conn)
    repo = RepositorioVentas(conexion_db)
    orquestador = OrquestadorVentas(repo)

    resultados = []

    # TEST 1: Cálculo matemático del Orquestador
    s_renglon = OrquestadorVentas.calcular_renglon(cantidad=2, precio_unitario=100.0, descuento_porc=10.0)
    det = DetalleFactura(id_producto=1, cantidad=2, precio_unitario=100.0, descuento_porcentaje=10.0, subtotal=s_renglon)
    sub, iva, total = OrquestadorVentas.calcular_totales_factura([det], aplicar_iva=True)
    
    if s_renglon == 180.0 and sub == 180.0 and iva == 37.8 and total == 217.8:
        resultados.append("✅ TEST 1: Lógica Matemática e IVA (OrquestadorVentas) -> PASÓ")
    else:
        resultados.append(f"❌ TEST 1: Falló ({s_renglon}, {sub}, {iva}, {total})")

    # TEST 2: Emisión y guardado en BD
    items = [{"id_producto": 1, "cantidad": 3, "precio_unitario": 25000.0, "descuento": 0.0}]
    factura_creada = orquestador.emitir_factura(id_cliente=1, id_vendedor=1, items_raw=items, aplicar_iva=True)
    
    if factura_creada.id_factura == 1 and factura_creada.total == 90750.0:
        resultados.append(f"✅ TEST 2: Emisión y Persistencia de Factura #{factura_creada.id_factura} -> PASÓ")
    else:
        resultados.append(f"❌ TEST 2: Falló ({factura_creada.id_factura}, {factura_creada.total})")

    # TEST 3: Descuento automático de stock por Trigger
    cursor = conn.cursor()
    cursor.execute("SELECT stock_actual FROM productos WHERE id = 1")
    stock_restante = cursor.fetchone()[0]
    
    if stock_restante == 7:
        resultados.append(f"✅ TEST 3: Trigger 'trg_descontar_stock' (Stock actual: {stock_restante}) -> PASÓ")
    else:
        resultados.append(f"❌ TEST 3: Falló stock restante = {stock_restante}")

    # TEST 4: Rechazo por Stock Insuficiente
    items_exceso = [{"id_producto": 1, "cantidad": 20, "precio_unitario": 25000.0, "descuento": 0.0}]
    try:
        orquestador.emitir_factura(id_cliente=1, id_vendedor=1, items_raw=items_exceso, aplicar_iva=True)
        resultados.append("❌ TEST 4: Falló (se permitió vender sin stock)")
    except ValueError as e:
        if "Stock insuficiente" in str(e):
            resultados.append("✅ TEST 4: Trigger 'trg_validar_stock' rechazó venta por falta de stock -> PASÓ")
        else:
            resultados.append(f"❌ TEST 4: Lanzó otra excepción ({e})")

    conn.close()
    return resultados

if __name__ == "__main__":
    print("\n=======================================================")
    print(" EJECUTANDO PRUEBAS AUTOMÁTICAS - MÓDULO DE VENTAS")
    print("=======================================================\n")
    for r in ejecutar_suite_de_pruebas():
        print(r)
    print("\n=======================================================\n")
