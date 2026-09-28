"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO DE RRHH (repo_rrhh.py)
===============================================================================
Estrategia y Buenas Prácticas Aplicadas:
1. Patrón Repository (Repository Pattern):
   Mediador entre la capa de Dominio (Python) y la Base de Datos SQLite,
   desacoplando completamente la persistencia SQL de la Interfaz de Usuario.

2. Respeto del Esquema Relacional Multitabla:
   Garantiza la integridad referencial y las restricciones CHECK del esquema
   'personas' y 'empleados' (tipo_persona='Fisica', validación de listas fijas).

3. Transacciones Atómicas (ACID - Commit / Rollback):
   Las operaciones que modifican múltiples tablas se ejecutan en un bloque
   transaccional único; si ocurre un error, se revierte con conn.rollback().

4. Sanitización y Descarte Defensivo (Fallback):
   Aplica listas de opciones (CARGOS, SECTORES, TIPOS_VINCULO) antes de la
   persistencia para evitar excepciones por violaciones de restricción CHECK.
===============================================================================
"""

from typing import List, Optional
import infraestructura.conexion as modulo_conexion
from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import (
    Empleado,
    limpiar_documento,
    TIPOS_VINCULO,
    SECTORES,
    CARGOS
)


def _obtener_conexion_segura():
    """
    Función helper de resiliencia para obtener la conexión a la Base de Datos.
    Soporta múltiples métodos de resolución según la estructura de ConexionDB.
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
        raise AttributeError("No se encontró un método de conexión válido en ConexionDB.")


class RepositorioRRHH:
    """ Repositorio encargado de la persistencia de la entidad Empleado y liquidaciones. """

    @staticmethod
    def asegurar_columnas():
        """
        Migración defensiva del esquema.
        Garantiza la presencia de 'activo' y 'tipo_vinculo' en la tabla 'empleados'
        si se ejecuta sobre bases de datos heredadas.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(empleados)")
            columnas = [col[1] for col in cursor.fetchall()]
            if "activo" not in columnas:
                cursor.execute("ALTER TABLE empleados ADD COLUMN activo INTEGER DEFAULT 1")
            if "tipo_vinculo" not in columnas:
                cursor.execute("ALTER TABLE empleados ADD COLUMN tipo_vinculo TEXT DEFAULT 'Planta'")
            conn.commit()
        except Exception as e:
            print(f"Error al verificar o migrar columnas en 'empleados': {e}")

    @staticmethod
    def existe_documento(nro_documento: str, id_persona_actual: Optional[int] = None) -> bool:
        """ Validación de Unicidad de Documento en la Base de Datos. """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        doc_limpio = limpiar_documento(nro_documento)
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
        """ Secuencia Autoincremental de Legajo (EMP-001, EMP-002, etc.). """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM empleados")
            row = cursor.fetchone()
            ultimo_id = row[0] if (row and row[0] is not None) else 0
            return f"EMP-{(ultimo_id + 1):03d}"
        except Exception as e:
            print(f"Error al calcular el legajo: {e}")
            return "EMP-001"

    @staticmethod
    def crear_empleado(empleado: Empleado) -> bool:
        """
        Operación Transaccional de Alta Multitabla (INSERT personas + empleados).
        Cumple estrictamente con el CHECK chk_tipo_persona ('Fisica').
        """
        RepositorioRRHH.asegurar_columnas()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            # 1. Inserción en la tabla base 'personas'
            # 'Fisica' requiere nombres y apellidos NOT NULL y razon_social NULL (exigido por el CHECK)
            query_persona = """
                            INSERT INTO personas (tipo_persona, nombres, apellidos, razon_social, tipo_documento,
                                                  nro_documento, telefono, email, domicilio, ciudad, provincia,
                                                  codigo_postal)
                            VALUES ('Fisica', ?, ?, NULL, 'DNI', ?, ?, ?, '', '', '', '')
                            """
            cursor.execute(query_persona, (
                empleado.nombres or "Sin Nombre",
                empleado.apellidos or "Sin Apellido",
                empleado.nro_documento or "",
                empleado.telefono or "",
                empleado.email or ""
            ))

            id_persona_insertada = cursor.lastrowid

            # Sanitización mediante las listas de opciones (Valores por descarte/fallback)
            cargo_val = empleado.cargo if empleado.cargo in CARGOS else "Empleado_Admin"
            sector_val = empleado.sector if empleado.sector in SECTORES else "Administración"
            vinculo_val = empleado.tipo_vinculo if empleado.tipo_vinculo in TIPOS_VINCULO else "Planta"

            # 2. Inserción en la tabla derivada 'empleados'
            query_empleado = """
                             INSERT INTO empleados (id_persona, id_usuario, legajo, cargo, sector, tipo_vinculo, sueldo, activo)
                             VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                             """
            cursor.execute(query_empleado, (
                id_persona_insertada,
                empleado.id_usuario,
                empleado.legajo or RepositorioRRHH.generar_siguiente_legajo(),
                cargo_val,
                sector_val,
                vinculo_val,
                empleado.sueldo or 0.0
            ))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al crear empleado en la base de datos: {e}")
            return False

    @staticmethod
    def actualizar_empleado(empleado: Empleado) -> bool:
        """ Actualización Transaccional Multitabla (UPDATE personas + empleados). """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE personas
                SET nombres = ?, apellidos = ?, nro_documento = ?, telefono = ?, email = ?
                WHERE id = ?
            """, (empleado.nombres or "", empleado.apellidos or "", empleado.nro_documento or "",
                  empleado.telefono or "", empleado.email or "", empleado.id))

            cargo_val = empleado.cargo if empleado.cargo in CARGOS else "Empleado_Admin"
            sector_val = empleado.sector if empleado.sector in SECTORES else "Administración"
            vinculo_val = empleado.tipo_vinculo if empleado.tipo_vinculo in TIPOS_VINCULO else "Planta"

            cursor.execute("""
                UPDATE empleados
                SET legajo = ?, cargo = ?, sector = ?, tipo_vinculo = ?, sueldo = ?
                WHERE id = ?
            """, (empleado.legajo or "", cargo_val, sector_val, vinculo_val,
                  empleado.sueldo or 0.0, empleado.id_empleado))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar empleado: {e}")
            return False

    @staticmethod
    def cambiar_estado_empleado(id_empleado: int, nuevo_estado: int) -> bool:
        """ Baja Lógica / Reinstalación (Soft Delete). Preserva auditoría e historial. """
        RepositorioRRHH.asegurar_columnas()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE empleados SET activo = ? WHERE id = ?", (nuevo_estado, id_empleado))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al cambiar estado del empleado: {e}")
            return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = "", incluir_inactivos: bool = False) -> List[Empleado]:
        """ Recupera empleados uniendo 'empleados' y 'personas' mediante JOIN. """
        RepositorioRRHH.asegurar_columnas()
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        query = """
                SELECT e.id, p.id, p.nro_documento, p.nombres, p.apellidos,
                       e.legajo, e.cargo, e.sector, e.tipo_vinculo, e.sueldo,
                       p.email, p.telefono, COALESCE(e.activo, 1) as activo
                FROM empleados e
                JOIN personas p ON e.id_persona = p.id
                WHERE 1 = 1
                """

        parametros = []
        if not incluir_inactivos:
            query += " AND COALESCE(e.activo, 1) = 1"

        if criterio_busqueda:
            query += """
            AND (p.nombres LIKE ? OR p.apellidos LIKE ? OR e.legajo LIKE ? OR p.nro_documento LIKE ? OR p.email LIKE ?)
            """
            patron = f"%{criterio_busqueda}%"
            parametros.extend([patron, patron, patron, patron, patron])

        query += " ORDER BY e.id ASC"

        try:
            cursor.execute(query, parametros)
            filas = cursor.fetchall()

            lista_empleados: List[Empleado] = []
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
                    tipo_vinculo=f[8],
                    sueldo=f[9],
                    email=f[10],
                    telefono=f[11]
                )
                emp.activo = bool(f[12])
                lista_empleados.append(emp)

            return lista_empleados
        except Exception as e:
            print(f"Error al listar empleados: {e}")
            return []

    @staticmethod
    def calcular_liquidacion_planta() -> List[dict]:
        """
        Regla de Negocio:
        Calcula el sueldo a liquidar únicamente para los empleados activos con vínculo 'Planta'.
        Aplica un adicional del 15% para el sector Ventas y del 10% para Gestión.
        """
        conn = _obtener_conexion_segura()
        cursor = conn.cursor()

        query = """
                SELECT e.legajo, p.apellidos || ', ' || p.nombres AS nombre_completo,
                       e.cargo, e.sector, e.sueldo,
                       CASE 
                           WHEN e.sector = 'Ventas' THEN e.sueldo * 1.15
                           WHEN e.sector = 'Gestión' THEN e.sueldo * 1.10
                           ELSE e.sueldo
                       END AS sueldo_liquidado
                FROM empleados e
                JOIN personas p ON e.id_persona = p.id
                WHERE e.tipo_vinculo = 'Planta' AND COALESCE(e.activo, 1) = 1
                """
        try:
            cursor.execute(query)
            filas = cursor.fetchall()
            return [
                {
                    "legajo": f[0],
                    "empleado": f[1],
                    "cargo": f[2],
                    "sector": f[3],
                    "sueldo_base": f[4],
                    "sueldo_liquidado": f[5]
                }
                for f in filas
            ]
        except Exception as e:
            print(f"Error al calcular liquidación: {e}")
            return []