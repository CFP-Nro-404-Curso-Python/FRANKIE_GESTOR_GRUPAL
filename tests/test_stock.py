"""
===============================================================================
MÓDULO 4: GESTIÓN DE INVENTARIOS Y PROVEEDORES
Entregable de Calidad y Pruebas (QA): test/test_stock.py
===============================================================================
Batería de pruebas unitarias y de integración para verificar:
1. Creación y persistencia de Proveedores y Productos.
2. Cálculo de alertas de stock mínimo (requiere_reposicion).
3. Reglas de negocio de ajuste de stock (no permitir stock negativo).
4. Integridad referencial y manejo de transacciones en SQLite.
===============================================================================
"""

import sqlite3
import unittest

from infraestructura.repo_stock import RepositorioStock, Proveedor, Producto


class TestStockYProveedores(unittest.TestCase):
    """
    Suite de pruebas para validar el comportamiento del repositorio de stock.
    Usa una base de datos SQLite en memoria (':memory:') para aislar los tests.
    """

    def setUp(self) -> None:
        """
        NOTA DIDÁCTICA: 'setUp' se ejecuta automáticamente ANTES de cada test.
        Prepara una conexión SQLite en memoria aislada y crea las tablas base.
        """
        self.conexion_test = sqlite3.connect(":memory:")
        self.conexion_test.row_factory = sqlite3.Row
        self._crear_tablas_en_memoria()

    def tearDown(self) -> None:
        """
        NOTA DIDÁCTICA: 'tearDown' se ejecuta automáticamente DESPUÉS de cada test.
        Cierra la conexión para liberar memoria y garantizar aislamiento.
        """
        self.conexion_test.close()

    def _crear_tablas_en_memoria(self) -> None:
        """ Recrea el esquema de tablas del Módulo 4 en la base de datos temporal. """
        cursor = self.conexion_test.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS personas
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           tipo_persona
                           TEXT
                           NOT
                           NULL,
                           nombres
                           TEXT,
                           apellidos
                           TEXT,
                           razon_social
                           TEXT,
                           tipo_documento
                           TEXT,
                           nro_documento
                           TEXT,
                           telefono
                           TEXT,
                           email
                           TEXT,
                           domicilio
                           TEXT,
                           ciudad
                           TEXT,
                           provincia
                           TEXT,
                           codigo_postal
                           TEXT
                       );
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS proveedores
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           id_persona
                           INTEGER
                           NOT
                           NULL,
                           rubro
                           TEXT,
                           contacto_secundario
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           id_persona
                       ) REFERENCES personas
                       (
                           id
                       )
                           );
                       """)

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS productos
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           codigo
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           descripcion
                           TEXT
                           NOT
                           NULL,
                           categoria
                           TEXT,
                           id_proveedor
                           INTEGER
                           NOT
                           NULL,
                           stock_actual
                           INTEGER
                           DEFAULT
                           0,
                           stock_minimo
                           INTEGER
                           DEFAULT
                           5,
                           precio_costo
                           REAL
                           DEFAULT
                           0.0,
                           precio_venta
                           REAL
                           DEFAULT
                           0.0,
                           ubicacion
                           TEXT,
                           vencimiento
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           id_proveedor
                       ) REFERENCES proveedores
                       (
                           id
                       )
                           );
                       """)
        self.conexion_test.commit()

    # -------------------------------------------------------------------------
    # 1. PRUEBAS DE PROVEEDORES
    # -------------------------------------------------------------------------
    def test_guardar_y_listar_proveedor(self) -> None:
        """ Verifica la inserción correcta de un nuevo proveedor. """
        prov = Proveedor(
            tipo_persona="Jurídica",
            nombres="",
            apellidos="",
            razon_social="Distribuidora Central S.A.",
            tipo_documento="CUIT",
            nro_documento="30-11223344-5",
            telefono="1144332211",
            email="ventas@distcentral.com",
            domicilio="Av. Corrientes 1000",
            ciudad="CABA",
            provincia="Buenos Aires",
            codigo_postal="1001",
            rubro="Alimentos y Bebidas",
            contacto_secundario="Juan Pérez"
        )

        # Guardar en base de datos de test
        id_prov = RepositorioStock.guardar_proveedor(prov, conexion_alt=self.conexion_test)
        self.assertGreater(id_prov, 0, "El ID del proveedor generado debe ser mayor a 0.")

        # Consultar y verificar recuperación
        proveedores = RepositorioStock.listar_proveedores(conexion_alt=self.conexion_test)
        self.assertEqual(len(proveedores), 1, "Debe existir exactamente 1 proveedor en la BD.")
        self.assertEqual(proveedores[0].nombre_comercial, "Distribuidora Central S.A.")

    # -------------------------------------------------------------------------
    # 2. PRUEBAS DE PRODUCTOS Y ALERTAS DE STOCK
    # -------------------------------------------------------------------------
    def test_guardar_producto_y_evaluar_alerta_stock(self) -> None:
        """ Valida la regla de negocio de alerta cuando stock_actual <= stock_minimo. """
        # 1. Crear proveedor de prueba obligatorio
        prov = Proveedor(
            tipo_persona="Física", nombres="Carlos", apellidos="Gómez", razon_social="",
            tipo_documento="DNI", nro_documento="25111222", telefono="", email="",
            domicilio="", ciudad="", provincia="", codigo_postal="", rubro="Golosinas", contacto_secundario=""
        )
        id_prov = RepositorioStock.guardar_proveedor(prov, conexion_alt=self.conexion_test)

        # 2. Crear producto con stock crítico (Stock 2, Mínimo 5)
        prod = Producto(
            codigo="PROD-001",
            descripcion="Caramelos Menta 100g",
            categoria="Golosinas",
            id_proveedor=id_prov,
            stock_actual=2,
            stock_minimo=5,
            precio_costo=150.0,
            precio_venta=300.0
        )
        id_prod = RepositorioStock.guardar_producto(prod, conexion_alt=self.conexion_test)
        self.assertGreater(id_prod, 0, "El ID del producto generado debe ser mayor a 0.")

        # 3. Verificar que la dataclass evalúa correctamente 'requiere_reposicion'
        self.assertTrue(prod.requiere_reposicion, "El producto debe marcar alerta de reposición.")

        # 4. Probar filtro del repositorio para solo alertas
        productos_alerta = RepositorioStock.listar_productos(solo_alertas=True, conexion_alt=self.conexion_test)
        self.assertEqual(len(productos_alerta), 1, "Debe listar 1 producto con alerta activa.")

    # -------------------------------------------------------------------------
    # 3. PRUEBAS DE AJUSTE DE STOCK Y REGLAS DE NEGOCIO
    # -------------------------------------------------------------------------
    def test_ajustar_stock_valido_e_insuficiente(self) -> None:
        """ Valida el incremento/decremento de stock y rechaza decrementos que dejen stock negativo. """
        # Setup inicial
        prov = Proveedor(
            tipo_persona="Física", nombres="Ana", apellidos="López", razon_social="",
            tipo_documento="DNI", nro_documento="30111222", telefono="", email="",
            domicilio="", ciudad="", provincia="", codigo_postal="", rubro="Varios", contacto_secundario=""
        )
        id_prov = RepositorioStock.guardar_proveedor(prov, conexion_alt=self.conexion_test)

        prod = Producto(
            codigo="PROD-002",
            descripcion="Gaseosa Cola 2L",
            categoria="Bebidas",
            id_proveedor=id_prov,
            stock_actual=10,
            stock_minimo=3
        )
        id_prod = RepositorioStock.guardar_producto(prod, conexion_alt=self.conexion_test)

        # Incremento válido (+5)
        RepositorioStock.ajustar_stock(id_prod, 5, conexion_alt=self.conexion_test)
        productos = RepositorioStock.listar_productos(conexion_alt=self.conexion_test)
        self.assertEqual(productos[0].stock_actual, 15)

        # Decremento válido (-10)
        RepositorioStock.ajustar_stock(id_prod, -10, conexion_alt=self.conexion_test)
        productos = RepositorioStock.listar_productos(conexion_alt=self.conexion_test)
        self.assertEqual(productos[0].stock_actual, 5)

        # Decremento inválido (-10 cuando solo hay 5) -> Debe lanzar ValueError
        with self.assertRaises(ValueError):
            RepositorioStock.ajustar_stock(id_prod, -10, conexion_alt=self.conexion_test)


if __name__ == "__main__":
    unittest.main()