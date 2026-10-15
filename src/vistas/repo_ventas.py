import sqlite3
# Asumiendo que tu proyecto maneja las conexiones mediante un Context Manager centralizado
from src.infraestructura.conexion import ConexionDB

class RepositorioVentas:
    """
    Capa de Acceso a Datos (Infraestructura) para el Módulo de Ventas.
    Usa el gestor centralizado ConexionDB para evitar bloqueos de concurrencia en SQLite.
    """
    def guardar_factura(self, id_cliente: int, id_vendedor: int, detalles: list) -> int:
        if not detalles:
            raise ValueError("La factura no contiene ítems para guardar.")

        # Uso del gestor central con Context Manager (Punto 3 de la corrección)
        with ConexionDB() as db:
            cursor = db.cursor()
            
            try:
                # 1. Insertar Cabecera de Factura
                cursor.execute(
                    "INSERT INTO facturas (id_cliente, id_vendedor) VALUES (?, ?)",
                    (id_cliente, id_vendedor)
                )
                id_factura = cursor.lastrowid

                # 2. Insertar Detalle de Factura
                for item in detalles:
                    cursor.execute(
                        """INSERT INTO facturas_detalles 
                           (id_factura, id_producto, cantidad, precio_unitario, descuento_porcentaje) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (id_factura, item['id_producto'], item['cantidad'], item['precio'], item['descuento'])
                    )

                # Si todo está bien dentro del bloque 'with', la conexión confirma la transacción
                return id_factura

            except sqlite3.IntegrityError as e:
                raise ValueError(f"Error de integridad: Verifique que Cliente ({id_cliente}), Vendedor ({id_vendedor}) y Productos existan.")
            except sqlite3.DatabaseError as e:
                # Captura el RAISE(ABORT) emitido por el Trigger de Stock Insuficiente
                raise ValueError(f"Rechazado por la Base de Datos: {str(e)}")
