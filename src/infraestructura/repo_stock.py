"""
===============================================================================
REPOSITORIO DE STOCK Y PROVEEDORES (src/infraestructura/repo_stock.py)
===============================================================================
Gestiona las operaciones CRUD para el inventario y proveedores, soportando
baja lógica, actualizaciones seguras y control de stock crítico.
===============================================================================
"""

import sqlite3
from typing import List, Optional
from infraestructura.conexion import ConexionDB
from dominio.entidades_stock import Proveedor, Producto


class RepositorioStock:
    """
    Repositorio encargado de la persistencia de inventario y padrón de proveedores.
    """

    @staticmethod
    def guardar_proveedor(prov: Proveedor, conexion_alt: Optional[sqlite3.Connection] = None) -> int:
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()
        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            t_pers = getattr(prov, 'tipo_persona', 'Juridica')
            noms = getattr(prov, 'nombres', None)
            apells = getattr(prov, 'apellidos', None)
            razon = getattr(prov, 'razon_social', '') or ''
            t_doc = getattr(prov, 'tipo_documento', 'CUIT')
            n_doc = getattr(prov, 'nro_documento', '') or ''
            tel = getattr(prov, 'telefono', '') or ''
            mail = getattr(prov, 'email', '') or ''
            dom = getattr(prov, 'domicilio', '') or ''
            ciud = getattr(prov, 'ciudad', '') or ''
            prov_est = getattr(prov, 'provincia', '') or ''
            cp = getattr(prov, 'codigo_postal', '') or ''
            rub = getattr(prov, 'rubro', '') or ''
            contacto_sec = getattr(prov, 'contacto_secundario', '') or ''
            activo_val = 1 if getattr(prov, 'activo', True) else 0

            if prov.id_persona:
                cursor.execute("""
                    UPDATE personas 
                    SET tipo_persona=?, nombres=?, apellidos=?, razon_social=?,
                        tipo_documento=?, nro_documento=?, telefono=?, email=?,
                        domicilio=?, ciudad=?, provincia=?, codigo_postal=?
                    WHERE id = ?;
                """, (t_pers, noms, apells, razon, t_doc, n_doc, tel, mail, dom, ciud, prov_est, cp, prov.id_persona))
                id_per: int = int(prov.id_persona)
            else:
                cursor.execute("""
                    INSERT INTO personas (
                        tipo_persona, nombres, apellidos, razon_social,
                        tipo_documento, nro_documento, telefono, email,
                        domicilio, ciudad, provincia, codigo_postal
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (t_pers, noms, apells, razon, t_doc, n_doc, tel, mail, dom, ciud, prov_est, cp))
                id_per = int(cursor.lastrowid or 0)

            if prov.id:
                cursor.execute("UPDATE proveedores SET rubro=?, contacto_secundario=?, activo=? WHERE id=?;",
                               (rub, contacto_sec, activo_val, prov.id))
                id_p: int = int(prov.id)
            else:
                cursor.execute(
                    "INSERT INTO proveedores (id_persona, rubro, contacto_secundario, activo) VALUES (?, ?, ?, ?);",
                    (id_per, rub, contacto_sec, activo_val))
                id_p = int(cursor.lastrowid or 0)

            if conexion_alt is None:
                conn.commit()
            return id_p
        except Exception as e:
            if conexion_alt is None:
                conn.rollback()
            raise e

    @staticmethod
    def cambiar_estado_proveedor(id_proveedor: int, nuevo_estado: bool) -> bool:
        conn = ConexionDB().conexion
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE proveedores SET activo = ? WHERE id = ?;", (1 if nuevo_estado else 0, id_proveedor))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            return False

    @staticmethod
    def listar_proveedores(incluir_inactivos: bool = False) -> List[Proveedor]:
        conn = ConexionDB().conexion
        cursor = conn.cursor()
        query = """
            SELECT pr.id AS id_proveedor, pr.id_persona, pr.rubro, pr.contacto_secundario, pr.activo,
                   p.tipo_persona, p.nombres, p.apellidos, p.razon_social,
                   p.tipo_documento, p.nro_documento, p.telefono, p.email,
                   p.domicilio, p.ciudad, p.provincia, p.codigo_postal
            FROM proveedores pr
            JOIN personas p ON pr.id_persona = p.id
        """
        if not incluir_inactivos:
            query += " WHERE pr.activo = 1"
        query += " ORDER BY p.razon_social, p.apellidos;"

        cursor.execute(query)
        filas = cursor.fetchall()
        resultado = []
        for f in filas:
            prov = Proveedor(
                id=f["id_proveedor"],
                id_persona=f["id_persona"],
                rubro=f["rubro"] or "",
                contacto_secundario=f["contacto_secundario"] or "",
                activo=bool(f["activo"]) if "activo" in f.keys() else True,
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
    def guardar_producto(prod: Producto) -> int:
        conn = ConexionDB().conexion
        cursor = conn.cursor()
        target_id = prod.id if prod.id is not None else getattr(prod, 'id_producto', None)
        activo_val = 1 if getattr(prod, 'activo', True) else 0
        s_min = prod.stock_minimo if prod.stock_minimo and prod.stock_minimo > 0 else 75

        try:
            if target_id:
                query = """
                    UPDATE productos 
                    SET codigo=?, descripcion=?, categoria=?, id_proveedor=?,
                        stock_actual=?, stock_minimo=?, precio_costo=?, precio_venta=?,
                        ubicacion=?, vencimiento=?, activo=?
                    WHERE id=?;
                """
                cursor.execute(query, (
                    prod.codigo, prod.descripcion, prod.categoria, prod.id_proveedor,
                    prod.stock_actual, s_min, prod.precio_costo, prod.precio_venta,
                    prod.ubicacion, prod.vencimiento, activo_val, target_id
                ))
                id_pr = int(target_id)
            else:
                query = """
                    INSERT INTO productos (
                        codigo, descripcion, categoria, id_proveedor,
                        stock_actual, stock_minimo, precio_costo, precio_venta,
                        ubicacion, vencimiento, activo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                cursor.execute(query, (
                    prod.codigo, prod.descripcion, prod.categoria, prod.id_proveedor,
                    prod.stock_actual, s_min, prod.precio_costo, prod.precio_venta,
                    prod.ubicacion, prod.vencimiento, activo_val
                ))
                id_pr = int(cursor.lastrowid or 0)
            conn.commit()
            return id_pr
        except Exception as e:
            conn.rollback()
            raise e

    @staticmethod
    def cambiar_estado_producto(id_producto: int, nuevo_estado: bool) -> bool:
        conn = ConexionDB().conexion
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE productos SET activo = ? WHERE id = ?;", (1 if nuevo_estado else 0, id_producto))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            return False

    @staticmethod
    def listar_productos(solo_alertas: bool = False, incluir_inactivos: bool = False) -> List[Producto]:
        conn = ConexionDB().conexion
        cursor = conn.cursor()

        # 🛡️ Corrección automática: Fuerza activo=1 en productos antiguos que tengan NULL
        try:
            cursor.execute("UPDATE productos SET activo = 1 WHERE activo IS NULL;")
            conn.commit()
        except Exception:
            pass

        query = """
            SELECT prod.*, 
                   COALESCE(p.razon_social, p.apellidos || ' ' || COALESCE(p.nombres, '')) AS prov_nombre
            FROM productos prod
            JOIN proveedores pr ON prod.id_proveedor = pr.id
            JOIN personas p ON pr.id_persona = p.id
            WHERE 1=1
        """
        if not incluir_inactivos:
            query += " AND (prod.activo = 1 OR prod.activo IS NULL)"

        if solo_alertas:
            query += " AND prod.stock_actual <= (prod.stock_minimo * 0.20)"

        query += " ORDER BY prod.descripcion;"

        cursor.execute(query)
        filas = cursor.fetchall()
        lista_prod = []
        for f in filas:
            activo_prod = bool(f["activo"]) if "activo" in f.keys() else True
            p = Producto(
                id=f["id"],
                codigo=f["codigo"],
                descripcion=f["descripcion"],
                categoria=f["categoria"] or "",
                id_proveedor=f["id_proveedor"],
                stock_actual=f["stock_actual"],
                stock_minimo=f["stock_minimo"] if f["stock_minimo"] else 75,
                precio_costo=f["precio_costo"],
                precio_venta=f["precio_venta"],
                ubicacion=f["ubicacion"] or "",
                vencimiento=f["vencimiento"],
                activo=activo_prod,
                nombre_proveedor=f["prov_nombre"] or ""
            )
            lista_prod.append(p)
        return lista_prod