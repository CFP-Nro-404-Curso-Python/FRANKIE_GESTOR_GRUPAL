"""
===============================================================================
MÓDULO 4: GESTIÓN DE INVENTARIOS Y PROVEEDORES
Entregables 2 y 3: Repositorio de Stock y Métodos de Persistencia (repo_stock.py)
===============================================================================
Maneja las operaciones CRUD sobre la base de datos SQLite para proveedores
y productos de inventario utilizando 'dataclasses' para modelar la información.
===============================================================================
"""

import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from infraestructura.conexion import ConexionDB


# =============================================================================
# ENTIDADES DE DOMINIO REFACTORIZADAS CON @DATACLASS
# =============================================================================

@dataclass
class Proveedor:
    """ Dataclass para la entidad Proveedor. """
    tipo_persona: str
    nombres: str
    apellidos: str
    razon_social: str
    tipo_documento: str
    nro_documento: str
    telefono: str
    email: str
    domicilio: str
    ciudad: str
    provincia: str
    codigo_postal: str
    rubro: str
    contacto_secundario: str
    id: Optional[int] = None
    id_persona: Optional[int] = None

    @property
    def nombre_comercial(self) -> str:
        """ Retorna la razón social o el nombre completo del proveedor. """
        if self.razon_social and self.razon_social.strip():
            return self.razon_social.strip()
        return f"{self.nombres} {self.apellidos}".strip()


@dataclass
class Producto:
    """ Dataclass para la entidad Producto. """
    codigo: str
    descripcion: str
    categoria: str
    id_proveedor: int
    stock_actual: int = 0
    stock_minimo: int = 5
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    ubicacion: str = ""
    vencimiento: Optional[str] = None
    id: Optional[int] = None
    nombre_proveedor: Optional[str] = None

    @property
    def requiere_reposicion(self) -> bool:
        """ Evalúa si el stock actual está por debajo o en el mínimo. """
        stock_act = self.stock_actual if self.stock_actual is not None else 0
        stock_min = self.stock_minimo if self.stock_minimo is not None else 0
        return stock_act <= stock_min


# =============================================================================
# REPOSITORIO DE STOCK Y PROVEEDORES
# =============================================================================

class RepositorioStock:
    """
    Capa de acceso a datos para la gestión de inventario y proveedores.
    """

    # -------------------------------------------------------------------------
    # GESTIÓN DE PROVEEDORES
    # -------------------------------------------------------------------------
    @classmethod
    def guardar_proveedor(cls, prov: Proveedor, conexion_alt: Optional[sqlite3.Connection] = None) -> int:
        """
        Inserta o actualiza un Proveedor garantizando el retorno de un ID entero ('int').
        """
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            # -----------------------------------------------------------------
            # 1. TABLA PERSONAS
            # -----------------------------------------------------------------
            if prov.id_persona:
                query_persona = """
                    UPDATE personas 
                    SET tipo_persona=?, nombres=?, apellidos=?, razon_social=?,
                        tipo_documento=?, nro_documento=?, telefono=?, email=?,
                        domicilio=?, ciudad=?, provincia=?, codigo_postal=?
                    WHERE id = ?;
                """
                cursor.execute(query_persona, (
                    prov.tipo_persona, prov.nombres, prov.apellidos, prov.razon_social,
                    prov.tipo_documento, prov.nro_documento, prov.telefono, prov.email,
                    prov.domicilio, prov.ciudad, prov.provincia, prov.codigo_postal,
                    prov.id_persona
                ))
                id_persona_validado: int = int(prov.id_persona)
            else:
                query_persona = """
                    INSERT INTO personas (
                        tipo_persona, nombres, apellidos, razon_social,
                        tipo_documento, nro_documento, telefono, email,
                        domicilio, ciudad, provincia, codigo_postal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(query_persona, (
                    prov.tipo_persona, prov.nombres, prov.apellidos, prov.razon_social,
                    prov.tipo_documento, prov.nro_documento, prov.telefono, prov.email,
                    prov.domicilio, prov.ciudad, prov.provincia, prov.codigo_postal
                ))
                last_id = cursor.lastrowid
                id_persona_validado = int(last_id) if last_id is not None else 0

            # -----------------------------------------------------------------
            # 2. TABLA PROVEEDORES
            # -----------------------------------------------------------------
            if prov.id:
                query_prov = "UPDATE proveedores SET rubro=?, contacto_secundario=? WHERE id=?;"
                cursor.execute(query_prov, (prov.rubro, prov.contacto_secundario, prov.id))
                id_prov_validado: int = int(prov.id)
            else:
                query_prov = "INSERT INTO proveedores (id_persona, rubro, contacto_secundario) VALUES (?, ?, ?);"
                cursor.execute(query_prov, (id_persona_validado, prov.rubro, prov.contacto_secundario))
                last_prov_id = cursor.lastrowid
                id_prov_validado = int(last_prov_id) if last_prov_id is not None else 0

            if conexion_alt is None:
                conn.commit()

            return id_prov_validado

        except Exception as e:
            if conexion_alt is None:
                conn.rollback()
            raise e

    @classmethod
    def listar_proveedores(cls, conexion_alt: Optional[sqlite3.Connection] = None) -> List[Proveedor]:
        """ Obtiene la lista completa de proveedores construyendo instancias de @dataclass. """
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        query = """
            SELECT p.id as id_persona, p.tipo_persona, p.nombres, p.apellidos, 
                   p.razon_social, p.tipo_documento, p.nro_documento, p.telefono, 
                   p.email, p.domicilio, p.ciudad, p.provincia, p.codigo_postal,
                   pr.id as id_proveedor, pr.rubro, pr.contacto_secundario
            FROM proveedores pr
            JOIN personas p ON pr.id_persona = p.id
            ORDER BY p.razon_social, p.apellidos;
        """
        cursor.execute(query)
        filas = cursor.fetchall()

        lista: List[Proveedor] = []
        for f in filas:
            prov = Proveedor(
                id=f["id_proveedor"],
                id_persona=f["id_persona"],
                tipo_persona=f["tipo_persona"],
                nombres=f["nombres"],
                apellidos=f["apellidos"],
                razon_social=f["razon_social"],
                tipo_documento=f["tipo_documento"],
                nro_documento=f["nro_documento"],
                telefono=f["telefono"],
                email=f["email"],
                domicilio=f["domicilio"],
                ciudad=f["ciudad"],
                provincia=f["provincia"],
                codigo_postal=f["codigo_postal"],
                rubro=f["rubro"],
                contacto_secundario=f["contacto_secundario"]
            )
            lista.append(prov)

        return lista

    # -------------------------------------------------------------------------
    # GESTIÓN DE PRODUCTOS
    # -------------------------------------------------------------------------
    @classmethod
    def guardar_producto(cls, prod: Producto, conexion_alt: Optional[sqlite3.Connection] = None) -> int:
        """ Inserta o actualiza un producto en la tabla 'productos'. """
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        if prod.id_proveedor is None:
            raise ValueError("El producto debe estar asociado a un id_proveedor válido.")

        id_proveedor_validado: int = int(prod.id_proveedor)

        if prod.id:
            query = """
                UPDATE productos 
                SET codigo=?, descripcion=?, categoria=?, id_proveedor=?,
                    stock_actual=?, stock_minimo=?, precio_costo=?, precio_venta=?,
                    ubicacion=?, vencimiento=?
                WHERE id=?;
            """
            cursor.execute(query, (
                prod.codigo, prod.descripcion, prod.categoria, id_proveedor_validado,
                prod.stock_actual, prod.stock_minimo, prod.precio_costo, prod.precio_venta,
                prod.ubicacion, prod.vencimiento, prod.id
            ))
            id_prod_validado: int = int(prod.id)
        else:
            query = """
                INSERT INTO productos (
                    codigo, descripcion, categoria, id_proveedor,
                    stock_actual, stock_minimo, precio_costo, precio_venta,
                    ubicacion, vencimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(query, (
                prod.codigo, prod.descripcion, prod.categoria, id_proveedor_validado,
                prod.stock_actual, prod.stock_minimo, prod.precio_costo, prod.precio_venta,
                prod.ubicacion, prod.vencimiento
            ))
            last_prod_id = cursor.lastrowid
            id_prod_validado = int(last_prod_id) if last_prod_id is not None else 0

        if conexion_alt is None:
            conn.commit()

        return id_prod_validado

    @classmethod
    def listar_productos(cls, solo_alertas: bool = False, conexion_alt: Optional[sqlite3.Connection] = None) -> List[Producto]:
        """ Obtiene el catálogo de productos devolviendo objetos de tipo @dataclass Producto. """
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        query = """
            SELECT prod.*, 
                   COALESCE(pers.razon_social, pers.nombres || ' ' || pers.apellidos) as nombre_proveedor
            FROM productos prod
            JOIN proveedores prov ON prod.id_proveedor = prov.id
            JOIN personas pers ON prov.id_persona = pers.id
        """
        if solo_alertas:
            query += " WHERE prod.stock_actual <= prod.stock_minimo"

        query += " ORDER BY prod.descripcion ASC;"

        cursor.execute(query)
        filas = cursor.fetchall()

        lista: List[Producto] = []
        for f in filas:
            p = Producto(
                id=f["id"],
                codigo=f["codigo"],
                descripcion=f["descripcion"],
                categoria=f["categoria"],
                id_proveedor=f["id_proveedor"],
                stock_actual=f["stock_actual"],
                stock_minimo=f["stock_minimo"],
                precio_costo=f["precio_costo"],
                precio_venta=f["precio_venta"],
                ubicacion=f["ubicacion"],
                vencimiento=f["vencimiento"],
                nombre_proveedor=f["nombre_proveedor"]
            )
            lista.append(p)

        return lista

    @classmethod
    def ajustar_stock(cls, id_producto: int, cantidad_cambio: int, conexion_alt: Optional[sqlite3.Connection] = None) -> None:
        """ Ajusta las unidades en stock controlando la regla de negocio de no negativos. """
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        cursor.execute("SELECT stock_actual FROM productos WHERE id = ?;", (id_producto,))
        fila = cursor.fetchone()

        if not fila:
            raise ValueError(f"No existe el producto con ID {id_producto}")

        stock_actual = fila["stock_actual"]
        nuevo_stock = stock_actual + cantidad_cambio

        if nuevo_stock < 0:
            raise ValueError(f"Stock insuficiente. Stock actual: {stock_actual}, intento de ajuste: {cantidad_cambio}")

        cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?;", (nuevo_stock, id_producto))

        if conexion_alt is None:
            conn.commit()