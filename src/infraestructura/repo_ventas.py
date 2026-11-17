"""
===============================================================================
REPOSITORIO DE VENTAS (src/infraestructura/repo_ventas.py)
===============================================================================
"""

import sqlite3
from typing import Optional
from infraestructura.conexion import ConexionDB
from dominio.entidades_ventas import Cliente, Factura


class RepositorioVentas:
    """
    Repositorio encargado de la persistencia de clientes, emisión de facturas
    y registro de líneas de detalle comercial.
    """

    @staticmethod
    def crear_cliente(cliente: Cliente) -> Cliente:
        """Registra un nuevo cliente vinculado a una persona física."""
        with ConexionDB() as db:
            cursor = db.cursor()
            try:
                nombres_val = str(cliente.nombres or "")
                apellidos_val = str(cliente.apellidos or "")
                dni_val = str(cliente.nro_documento or "")
                tel_val = str(cliente.telefono or "")
                email_val = str(cliente.email or "")

                cursor.execute(
                    """
                    INSERT INTO personas (tipo_persona, nombres, apellidos, tipo_documento, nro_documento, telefono, email)
                    VALUES ('Fisica', ?, ?, 'DNI', ?, ?, ?)
                    """,
                    (nombres_val, apellidos_val, dni_val, tel_val, email_val)
                )
                id_persona = int(cursor.lastrowid or 0)

                cursor.execute(
                    "INSERT INTO clientes (id_persona) VALUES (?)",
                    (id_persona,)
                )
                cliente.id_cliente = int(cursor.lastrowid or 0)
                cliente.id_persona = id_persona
                return cliente
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Error de integridad al registrar cliente: {e}")

    @staticmethod
    def obtener_cliente_por_id(id_cliente: int) -> Optional[Cliente]:
        """Recupera un cliente por su identificador único."""
        with ConexionDB() as db:
            cursor = db.cursor()
            cursor.execute(
                """
                SELECT c.id, p.nombres, p.apellidos, p.nro_documento, p.email, p.telefono, p.id
                FROM clientes c
                INNER JOIN personas p ON c.id_persona = p.id
                WHERE c.id = ?
                """,
                (int(id_cliente),)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return Cliente(
                id_cliente=int(row[0]),
                nombres=str(row[1] or ""),
                apellidos=str(row[2] or ""),
                nro_documento=str(row[3] or ""),
                cuit_cliente=str(row[3] or ""),
                email=str(row[4] or ""),
                telefono=str(row[5] or ""),
                id_persona=int(row[6]) if row[6] is not None else None
            )

    @staticmethod
    def guardar_factura(factura: Factura) -> Factura:
        """Registra la cabecera de la factura y sus detalles, activando los triggers de stock."""
        if not factura.detalles:
            raise ValueError("La factura debe contener al menos un detalle.")

        id_cli = factura.cliente.id_cliente if factura.cliente and factura.cliente.id_cliente is not None else 0
        id_vend = int(factura.id_vendedor) if factura.id_vendedor is not None else 1
        total_fac = float(factura.total or 0.0)

        with ConexionDB() as db:
            cursor = db.cursor()
            try:
                # 1. Cabecera
                cursor.execute(
                    "INSERT INTO facturas (id_cliente, id_vendedor, total) VALUES (?, ?, ?)",
                    (id_cli, id_vend, total_fac)
                )
                factura.id_factura = int(cursor.lastrowid or 0)

                # 2. Detalles (Disparan los Triggers de Stock automáticamente en SQLite)
                for det in factura.detalles:
                    cursor.execute(
                        """
                        INSERT INTO facturas_detalles 
                        (id_factura, id_producto, cantidad, precio_unitario, descuento_porcentaje, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            factura.id_factura,
                            int(det.id_producto),
                            int(det.cantidad),
                            float(det.precio_unitario),
                            float(det.descuento_porcentaje),
                            float(det.subtotal)
                        )
                    )
                    det.id_detalle = int(cursor.lastrowid or 0)
                    det.id_factura = factura.id_factura

                return factura
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Error de integridad: Verifique que el Cliente o Vendedor existan ({e})")
            except sqlite3.DatabaseError as e:
                raise ValueError(f"Rechazado por la base de datos (Stock insuficiente): {e}")