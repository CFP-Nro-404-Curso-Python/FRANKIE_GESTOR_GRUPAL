"""
Módulo de Infraestructura: Repositorio de Recursos Humanos
Maneja las operaciones CRUD en la base de datos para la entidad Empleado.
"""

import infraestructura.conexion as modulo_conexion
from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import Empleado


def _obtener_conexion_segura():
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
    def asegurar_columna_activo():
        """ Asegura que la columna 'activo' exista en la tabla empleados. """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(empleados)")
            columnas = [col[1] for col in cursor.fetchall()]
            if "activo" not in columnas:
                cursor.execute(
                    "ALTER TABLE empleados ADD COLUMN activo INTEGER DEFAULT 1")
                conn.commit()
        except Exception as e:
            print(f"Error al verificar/crear columna 'activo': {e}")

    @staticmethod
    def existe_documento(nro_documento: str,
                         id_persona_actual: int = None) -> bool:
        """
        Verifica si un CUIT/CUIL de 11 dígitos ya está registrado en la base de datos.
        Si se le pasa 'id_persona_actual', ignora el registro del propio empleado que se está editando.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        doc_limpio = "".join(c for c in str(nro_documento) if c.isdigit())
        try:
            if id_persona_actual:
                cursor.execute("""
                    SELECT 1 FROM personas 
                    WHERE REPLACE(REPLACE(nro_documento, '-', ''), ' ', '') = ?
                    AND id <> ?
                """, (doc_limpio, id_persona_actual))
            else:
                cursor.execute("""
                    SELECT 1 FROM personas 
                    WHERE REPLACE(REPLACE(nro_documento, '-', ''), ' ', '') = ?
                """, (doc_limpio,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar duplicado de documento: {e}")
            return False

    @staticmethod
    def generar_siguiente_legajo() -> str:
        """ Genera automáticamente la secuencia de legajos EMP-001, EMP-002, etc. """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM empleados")
            row = cursor.fetchone()
            ultimo_id = row[0] if (row and row[0] is not None) else 0
            siguiente_num = ultimo_id + 1
            return f"EMP-{siguiente_num:03d}"
        except Exception as e:
            print(f"Error al calcular legajo: {e}")
            return "EMP-001"

    @staticmethod
    def crear_empleado(empleado: Empleado) -> bool:
        RepositorioRRHH.asegurar_columna_activo()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
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

            query_empleado = """
            INSERT INTO empleados (
                id_persona, id_usuario, legajo, cargo, sector, sueldo, activo
            ) VALUES (?, ?, ?, ?, ?, ?, 1)
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
            print(f"Error al crear empleado: {e}")
            return False

    @staticmethod
    def actualizar_empleado(empleado: Empleado) -> bool:
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
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
            print(f"Error al actualizar empleado: {e}")
            return False

    @staticmethod
    def cambiar_estado_empleado(id_empleado: int, nuevo_estado: int) -> bool:
        """ Cambia el estado 'activo' del empleado (1 = Activo, 0 = Inactivo). """
        RepositorioRRHH.asegurar_columna_activo()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE empleados SET activo = ? WHERE id = ?",
                           (nuevo_estado, id_empleado))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al cambiar estado del empleado: {e}")
            return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = "",
                         incluir_inactivos: bool = False):
        RepositorioRRHH.asegurar_columna_activo()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        query = """
        SELECT e.id, p.id, p.nro_documento, p.nombres, p.apellidos,
               e.legajo, e.cargo, e.sector, e.sueldo, p.email, p.telefono,
               COALESCE(e.activo, 1) as activo
        FROM empleados e
        JOIN personas p ON e.id_persona = p.id
        WHERE 1=1
        """

        parametros = []
        if not incluir_inactivos:
            query += " AND COALESCE(e.activo, 1) = 1"

        if criterio_busqueda:
            query += """
            AND (p.nombres LIKE ? OR p.apellidos LIKE ? OR e.legajo LIKE ? OR p.nro_documento LIKE ? OR p.email LIKE ? OR p.telefono LIKE ?)
            """
            patron = f"%{criterio_busqueda}%"
            parametros.extend([patron, patron, patron, patron, patron, patron])

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
                emp.activo = bool(f[11])
                lista_empleados.append(emp)

            return lista_empleados
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []