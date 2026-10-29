"""
===============================================================================
REPOSITORIO DE STOCK Y PROVEEDORES (infraestructura/repo_stock.py)
===============================================================================
Gestiona las operaciones CRUD para el inventario y el padrón de proveedores,
respetando la estructura de la base de datos original.
===============================================================================
"""

import sqlite3
from typing import List, Optional
from infraestructura.conexion import ConexionDB
from dominio.entidades_proveedores import Proveedor
from dominio.entidades_stock import Producto


class RepositorioStock:
    """
    Repositorio encargado de la persistencia de inventario y padrón de proveedores.
    """

    @staticmethod
    def guardar_proveedor(prov: Proveedor, conexion_alt: Optional[sqlite3.Connection] = None) -> int:
        """Inserta o actualiza un proveedor en la base de datos de manera transaccional."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            t_pers = prov.tipo_persona
            noms = prov.nombres
            apells = prov.apellidos
            razon = prov.razon_social
            t_doc = prov.tipo_documento
            n_doc = prov.nro_documento
            tel = prov.telefono
            mail = prov.email
            dom = prov.domicilio
            ciud = prov.ciudad
            prov_est = prov.provincia
            cp = prov.codigo_postal
            rub = prov.rubro
            contacto_sec = prov.contacto_secundario

            # 1. Tabla Personas
            if prov.id_persona:
                query_per = """
                    UPDATE personas 
                    SET tipo_persona=?, nombres=?, apellidos=?, razon_social=?,
                        tipo_documento=?, nro_documento=?, telefono=?, email=?,
                        domicilio=?, ciudad=?, provincia=?, codigo_postal=?
                    WHERE id = ?;
                """
                cursor.execute(query_per, (
                    t_pers, noms, apells, razon, t_doc, n_doc, tel, mail,
                    dom, ciud, prov_est, cp, prov.id_persona
                ))
                id_per: int = int(prov.id_persona)
            else:
                query_per = """
                    INSERT INTO personas (
                        tipo_persona, nombres, apellidos, razon_social,
                        tipo_documento, nro_documento, telefono, email,
                        domicilio, ciudad, provincia, codigo_postal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(query_per, (
                    t_pers, noms, apells, razon, t_doc, n_doc, tel, mail,
                    dom, ciud, prov_est, cp
                ))
                id_per = int(cursor.lastrowid or 0)

            # 2. Tabla Proveedores
            if prov.id:
                query_prov = "UPDATE proveedores SET rubro=?, contacto_secundario=? WHERE id=?;"
                cursor.execute(query_prov, (rub, contacto_sec, prov.id))
                id_p: int = int(prov.id)
            else:
                query_prov = "INSERT INTO proveedores (id_persona, rubro, contacto_secundario) VALUES (?, ?, ?);"
                cursor.execute(query_prov, (id_per, rub, contacto_sec))
                id_p = int(cursor.lastrowid or 0)

            if conexion_alt is None:
                conn.commit()

            return id_p

        except Exception as e:
            if conexion_alt is None:
                conn.rollback()
            raise e

    @staticmethod
    def listar_proveedores(conexion_alt: Optional[sqlite3.Connection] = None) -> List[Proveedor]:
        """Obtiene el padrón completo de proveedores."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        query = """
            SELECT pr.id AS id_proveedor, pr.id_persona, pr.rubro, pr.contacto_secundario,
                   p.tipo_persona, p.nombres, p.apellidos, p.razon_social,
                   p.tipo_documento, p.nro_documento, p.telefono, p.email,
                   p.domicilio, p.ciudad, p.provincia, p.codigo_postal
            FROM proveedores pr
            JOIN personas p ON pr.id_persona = p.id
            ORDER BY p.razon_social, p.apellidos;
        """
        cursor.execute(query)
        filas = cursor.fetchall()

        resultado = []
        for f in filas:
            prov = Proveedor(
                id=f["id_proveedor"],
                id_persona=f["id_persona"],
                rubro=f["rubro"] or "",
                contacto_secundario=f["contacto_secundario"] or "",
                tipo_persona=f["tipo_persona"] or "Juridica",
                nombres=f["nombres"] or "",
                apellidos=f["apellidos"] or "",
                razon_social=f["razon_social"] or "",
                tipo_documento=f["tipo_documento"] or "CUIT",
                nro_documento=f["nro_documento"] or "",
                telefono=f["telefono"] or "",
                email=f["email"] or "",
                domicilio=f["domicilio"] or "",
                ciudad=f["ciudad"] or "",
                provincia=f["provincia"] or "",
                codigo_postal=f["codigo_postal"] or ""
            )
            resultado.append(prov)

        return resultado

    @staticmethod
    def guardar_producto(prod: Producto, conexion_alt: Optional[sqlite3.Connection] = None) -> int:
        """Inserta o actualiza un producto en el inventario identificando si posee ID."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        target_id = prod.id if prod.id is not None else getattr(prod, 'id_producto', None)

        if target_id:
            # ACTUALIZACIÓN (Evita el error UNIQUE constraint al editar)
            query = """
                UPDATE productos 
                SET codigo=?, descripcion=?, categoria=?, id_proveedor=?,
                    stock_actual=?, stock_minimo=?, precio_costo=?, precio_venta=?,
                    ubicacion=?, vencimiento=?
                WHERE id=?;
            """
            cursor.execute(query, (
                prod.codigo, prod.descripcion, prod.categoria, prod.id_proveedor,
                prod.stock_actual, prod.stock_minimo, prod.precio_costo, prod.precio_venta,
                prod.ubicacion, prod.vencimiento, target_id
            ))
            id_pr: int = int(target_id)
        else:
            # INSERCIÓN NUEVA
            query = """
                INSERT INTO productos (
                    codigo, descripcion, categoria, id_proveedor,
                    stock_actual, stock_minimo, precio_costo, precio_venta,
                    ubicacion, vencimiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(query, (
                prod.codigo, prod.descripcion, prod.categoria, prod.id_proveedor,
                prod.stock_actual, prod.stock_minimo, prod.precio_costo, prod.precio_venta,
                prod.ubicacion, prod.vencimiento
            ))
            id_pr = int(cursor.lastrowid or 0)

        if conexion_alt is None:
            conn.commit()

        return id_pr

    @staticmethod
    def listar_productos(solo_alertas: bool = False, conexion_alt: Optional[sqlite3.Connection] = None) -> List[Producto]:
        """Obtiene el catálogo de productos evaluando opcionalmente el stock mínimo."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        query = """
            SELECT prod.*, 
                   COALESCE(p.razon_social, p.apellidos || ' ' || COALESCE(p.nombres, '')) AS prov_nombre
            FROM productos prod
            JOIN proveedores pr ON prod.id_proveedor = pr.id
            JOIN personas p ON pr.id_persona = p.id
        """
        if solo_alertas:
            query += " WHERE prod.stock_actual <= prod.stock_minimo"

        query += " ORDER BY prod.descripcion;"

        cursor.execute(query)
        filas = cursor.fetchall()

        lista_prod = []
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
                ubicacion=f["ubicacion"] or "",
                vencimiento=f["vencimiento"],
                nombre_proveedor=f["prov_nombre"]
            )
            lista_prod.append(p)

        return lista_prod

    @staticmethod
    def eliminar_producto(id_producto: int, conexion_alt: Optional[sqlite3.Connection] = None) -> None:
        """Elimina físicamente un producto descontinuado del inventario."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?;", (id_producto,))
        if conexion_alt is None:
            conn.commit()

    @staticmethod
    def ajustar_stock(id_producto: int, cantidad_cambio: int, conexion_alt: Optional[sqlite3.Connection] = None) -> bool:
        """Ajusta el stock de un producto validando reglas de negocio."""
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()

        cursor.execute("SELECT stock_actual FROM productos WHERE id = ?;", (id_producto,))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError(f"No existe el producto con ID {id_producto}")

        nuevo_stock = fila["stock_actual"] + cantidad_cambio
        if nuevo_stock < 0:
            raise ValueError("El ajuste resultaría en un stock negativo no permitido.")

        cursor.execute("UPDATE productos SET stock_actual = ? WHERE id = ?;", (nuevo_stock, id_producto))

        if conexion_alt is None:
            conn.commit()

        return True