from infraestructura.conexion import obtener_conexion


def obtener_clientes():
    """Trae la lista de clientes desde la BD para poblar selectores en la UI."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        query = "SELECT id, nombre, apellido, cuit FROM clientes"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


def obtener_productos_disponibles():
    """Trae productos con stock disponible para facturar."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        query = "SELECT id, nombre, precio, stock FROM productos WHERE stock > 0"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


def guardar_factura(id_cliente, total, detalles):
    """Guarda la cabecera de la factura y cada uno de sus ítems (detalles)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        # Insertar cabecera de factura
        sql_factura = "INSERT INTO facturas (id_cliente, fecha, total, estado) VALUES (%s, NOW(), %s, 'Emitida')"
        cursor.execute(sql_factura, (id_cliente, total))
        id_factura = cursor.lastrowid

        # Insertar ítems
        sql_detalle = "INSERT INTO detalles_factura (id_factura, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
        for item in detalles:
            cursor.execute(
                sql_detalle,
                (
                    id_factura,
                    item["id_producto"],
                    item["cantidad"],
                    item["precio_unitario"],
                ),
            )

        conexion.commit()
        return id_factura
    except Exception as e:
        conexion.rollback()
        print(f"Error al guardar factura: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()
