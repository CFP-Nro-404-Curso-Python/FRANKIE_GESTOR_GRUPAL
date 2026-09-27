"""
Módulo de Infraestructura: Repositorio de Recursos Humanos
Maneja las operaciones CRUD en la base de datos para la entidad Empleado.
"""

import infraestructura.conexion as modulo_conexion
from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import Empleado


def _obtener_conexion_segura():
    """
    Función auxiliar para obtener la conexión a la base de datos
    independientemente de la implementación exacta en ConexionDB.
    """
    if hasattr(ConexionDB, "obtener_conexion"):
        return ConexionDB.obtener_conexion()
    elif hasattr(ConexionDB, "get_connection"):
        return ConexionDB.get_connection()
    elif hasattr(modulo_conexion, "obtener_conexion"):
        return modulo_conexion.obtener_conexion()
    else:
        instancia = ConexionDB()
        if hasattr(instancia, "obtener_conexion"):
            return instancia.obtener_conexion()
        elif hasattr(instancia, "get_connection"):
            return instancia.get_connection()
        elif hasattr(instancia, "conexion"):
            return instancia.conexion
        raise AttributeError(
            "No se encontró un método de conexión válido en ConexionDB.")


class RepositorioRRHH:

    @staticmethod
    def generar_siguiente_legajo() -> str:
        """
        Calcula y retorna el siguiente legajo en formato 'EMP-XXX' (ej. EMP-001).
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM empleados")
            row = cursor.fetchone()
            ultimo_id = row[0] if (row and row[0] is not None) else 0
            siguiente_num = ultimo_id + 1
            return f"EMP-{siguiente_num:03d}"
        except Exception as e:
            print(f"Error al calcular el siguiente legajo: {e}")
            return "EMP-001"

    @staticmethod
    def crear_empleado(empleado: Empleado) -> bool:
        """
        Inserta una nueva Persona y su correspondiente Empleado en una transacción atómica.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            # 1. Insertar en la tabla 'personas'
            query_persona = """
            INSERT INTO personas (
                tipo_persona, nombres, apellidos, razon_social, tipo_documento,
                nro_documento, telefono, email, domicilio, ciudad, provincia, codigo_postal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_persona, (
                empleado.tipo_persona,
                empleado.nombres,
                empleado.apellidos,
                empleado.razon_social,
                empleado.tipo_documento,
                empleado.nro_documento,
                empleado.telefono,
                empleado.email,
                empleado.domicilio,
                empleado.ciudad,
                empleado.provincia,
                empleado.codigo_postal
            ))

            id_persona_insertada = cursor.lastrowid

            # 2. Insertar en la tabla 'empleados'
            query_empleado = """
            INSERT INTO empleados (
                id_persona, id_usuario, legajo, cargo, sector, sueldo
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query_empleado, (
                id_persona_insertada,
                empleado.id_usuario,
                empleado.legajo,
                empleado.cargo,
                empleado.sector,
                empleado.sueldo
            ))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error al crear el empleado en la BD: {e}")
            return False

    @staticmethod
    def actualizar_empleado(empleado: Empleado) -> bool:
        """
        Actualiza los datos del empleado y su correspondiente registro de Persona.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            # 1. Actualizar tabla 'personas'
            query_persona = """
            UPDATE personas
            SET nombres = ?, apellidos = ?, nro_documento = ?, telefono = ?, email = ?
            WHERE id = ?
            """
            cursor.execute(query_persona, (
                empleado.nombres,
                empleado.apellidos,
                empleado.nro_documento,
                empleado.telefono,
                empleado.email,
                empleado.id
            ))

            # 2. Actualizar tabla 'empleados'
            query_empleado = """
            UPDATE empleados
            SET legajo = ?, cargo = ?, sector = ?, sueldo = ?
            WHERE id = ?
            """
            cursor.execute(query_empleado, (
                empleado.legajo,
                empleado.cargo,
                empleado.sector,
                empleado.sueldo,
                empleado.id_empleado
            ))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar el empleado en la BD: {e}")
            return False

    @staticmethod
    def deshabilitar_empleado(id_empleado: int) -> bool:
        """
        Realiza la Baja Lógica del empleado deshabilitándolo (marca estado/activo en 0 o inactivo).
        Si la tabla aún no tiene columna 'activo', se deshabilita actualizando un flag en la BD.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            # Intentar actualización de columna 'activo' si existe en la tabla
            query = "UPDATE empleados SET activo = 0 WHERE id = ?"
            cursor.execute(query, (id_empleado,))
            conn.commit()
            return True
        except Exception:
            try:
                # Alternativa si el esquema utiliza la columna 'estado'
                query_alt = "UPDATE empleados SET estado = 'INACTIVO' WHERE id = ?"
                cursor.execute(query_alt, (id_empleado,))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                print(f"Error al deshabilitar empleado en BD: {e}")
                return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = ""):
        """
        Retorna la lista consolidada de empleados activos, opcionalmente filtrada por un criterio.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        query = """
        SELECT e.id, p.id, p.nro_documento, p.nombres, p.apellidos,
               e.legajo, e.cargo, e.sector, e.sueldo, p.email, p.telefono
        FROM empleados e
        JOIN personas p ON e.id_persona = p.id
        WHERE 1=1
        """

        parametros = []
        if criterio_busqueda:
            query += """
            AND (p.nombres LIKE ? OR p.apellidos LIKE ? OR e.legajo LIKE ? OR p.nro_documento LIKE ?)
            """
            patron = f"%{criterio_busqueda}%"
            parametros = [patron, patron, patron, patron]

        query += " ORDER BY e.id ASC"

        try:
            cursor.execute(query, parametros)
            filas = cursor.fetchall()

            lista_empleados = []
            for f in filas:
                emp = Empleado(
                    id_empleado=f[0],
                    id_persona=f[1],
                    nro_documento=f[2],
                    nombres=f[3],
                    apellidos=f[4],
                    legajo=f[5],
                    cargo=f[6],
                    sector=f[7],
                    sueldo=f[8],
                    email=f[9],
                    telefono=f[10]
                )
                lista_empleados.append(emp)

            return lista_empleados
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []