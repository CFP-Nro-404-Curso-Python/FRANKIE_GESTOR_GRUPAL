"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO DE VENTAS (infraestructura/repo_ventas.py)
===============================================================================
"""

import sqlite3
from typing import Optional, List
from infraestructura.conexion import ConexionDB
from dominio.entidades_ventas import Cliente, Factura, DetalleFactura


class RepositorioVentas:
    """ Maneja las operaciones de base de datos para Clientes y Facturas. """

    def crear_cliente(self, cliente: Cliente) -> Cliente:
        with ConexionDB() as db:
            cursor = db.cursor()
            try:
                cursor.execute(
                    """INSERT INTO personas (tipo_persona, nombres, apellidos, tipo_documento, nro_documento, telefono, email)
                       VALUES ('Fisica', ?, ?, 'DNI', ?, ?, ?)""",
                    (cliente.nombre, cliente.apellido, cliente.dni, cliente.telefono, cliente.email)
                )
                id_persona = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO clientes (id_persona) VALUES (?)",
                    (id_persona,)
                )
                cliente.id_cliente = cursor.lastrowid
                cliente.id_persona = id_persona
                return cliente
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Error de integridad al registrar cliente: {e}")

    def obtener_cliente_por_id(self, id_cliente: int) -> Optional[Cliente]:
        with ConexionDB() as db:
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

        with ConexionDB() as db:
            cursor = db.cursor()
            try:
                # 1. Cabecera
                cursor.execute(
                    "INSERT INTO facturas (id_cliente, id_vendedor, total) VALUES (?, ?, ?)",
                    (factura.cliente.id_cliente, factura.id_vendedor, factura.total)
                )
                factura.id_factura = cursor.lastrowid

                # 2. Detalles (Dispara los Triggers de Stock automáticamente)
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

                return factura
            except sqlite3.IntegrityError as e:
                raise ValueError(f"Error de integridad: Verifique que el Cliente o Vendedor existan ({e})")
            except sqlite3.DatabaseError as e:
                raise ValueError(f"Rechazado por la base de datos (Stock insuficiente): {e}")
