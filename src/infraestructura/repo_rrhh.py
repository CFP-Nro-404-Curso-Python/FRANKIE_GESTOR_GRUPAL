"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO DE RECURSOS HUMANOS (src/infraestructura/repo_rrhh.py)
===============================================================================
"""

from typing import List, Optional
import sqlite3

from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import Empleado


def _obtener_conexion_segura() -> sqlite3.Connection:
    """
    Helper a nivel de módulo (parcheable por los tests).
    Devuelve la conexión activa de la BD (singleton en producción).
    """
    return ConexionDB().conexion


class RepositorioRRHH:
    """
    Capa de acceso a datos para la gestión del personal y registros de personas.
    """

    @staticmethod
    def _obtener_columnas_tabla(cursor, tabla: str) -> List[str]:
        cursor.execute(f"PRAGMA table_info({tabla});")
        return [col[1] for col in cursor.fetchall()]

    @staticmethod
    def generar_siguiente_legajo(conexion_alt: Optional[sqlite3.Connection] = None) -> str:
        conn = conexion_alt or _obtener_conexion_segura()
        cursor = conn.cursor()
        cursor.execute("SELECT legajo FROM empleados ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        if row and row["legajo"] if hasattr(row, "keys") else row and row[0]:
            legajo = row["legajo"] if hasattr(row, "keys") else row[0]
            digitos = "".join(c for c in str(legajo) if c.isdigit())
            if digitos:
                return f"E{int(digitos) + 1:03d}"
        return "E001"

    @staticmethod
    def crear_empleado(emp: Empleado, conexion_alt: Optional[sqlite3.Connection] = None) -> bool:
        conn = conexion_alt or _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            doc_limpio = "".join(c for c in str(emp.nro_documento) if c.isdigit())
            tipo_doc = "CUIL" if len(doc_limpio) == 11 else "DNI"

            cursor.execute(
                """
                INSERT INTO personas (
                    tipo_persona, nombres, apellidos, razon_social,
                    tipo_documento, nro_documento, telefono, email
                ) VALUES ('Fisica', ?, ?, NULL, ?, ?, ?, ?);
                """,
                (
                    emp.nombres.strip(),
                    emp.apellidos.strip(),
                    tipo_doc,
                    doc_limpio,
                    (emp.telefono or "").strip(),
                    (emp.email or "").strip(),
                ),
            )
            id_persona_nueva = cursor.lastrowid

            cols_emp = RepositorioRRHH._obtener_columnas_tabla(cursor, "empleados")

            campos = ["id_persona", "id_usuario", "legajo", "cargo", "sector", "sueldo"]
            valores = [
                id_persona_nueva,
                None,
                emp.legajo or RepositorioRRHH.generar_siguiente_legajo(conexion_alt=conn),
                emp.cargo,
                emp.sector,
                float(emp.sueldo or 0.0),
            ]

            if "tipo_vinculo" in cols_emp:
                campos.append("tipo_vinculo")
                valores.append(getattr(emp, "tipo_vinculo", "Planta") or "Planta")

            if "activo" in cols_emp:
                campos.append("activo")
                valores.append(1)

            placeholders = ", ".join(["?"] * len(campos))
            sql_emp = f"INSERT INTO empleados ({', '.join(campos)}) VALUES ({placeholders});"
            cursor.execute(sql_emp, valores)

            if conexion_alt is None:
                conn.commit()
            return True

        except Exception as e:
            if conexion_alt is None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ERROR RepoRRHH.crear_empleado]: {e}")
            raise e

    @staticmethod
    def actualizar_empleado(emp: Empleado, conexion_alt: Optional[sqlite3.Connection] = None) -> bool:
        conn = conexion_alt or _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            doc_limpio = "".join(c for c in str(emp.nro_documento) if c.isdigit())
            tipo_doc = "CUIL" if len(doc_limpio) == 11 else "DNI"

            if emp.id_persona:
                cursor.execute(
                    """
                    UPDATE personas
                    SET nombres = ?, apellidos = ?, tipo_documento = ?,
                        nro_documento = ?, telefono = ?, email = ?
                    WHERE id = ?;
                    """,
                    (
                        emp.nombres.strip(),
                        emp.apellidos.strip(),
                        tipo_doc,
                        doc_limpio,
                        (emp.telefono or "").strip(),
                        (emp.email or "").strip(),
                        emp.id_persona,
                    ),
                )

            cols_emp = RepositorioRRHH._obtener_columnas_tabla(cursor, "empleados")
            sets = ["legajo = ?", "cargo = ?", "sector = ?", "sueldo = ?"]
            valores = [emp.legajo, emp.cargo, emp.sector, float(emp.sueldo or 0.0)]

            if "tipo_vinculo" in cols_emp:
                sets.append("tipo_vinculo = ?")
                valores.append(getattr(emp, "tipo_vinculo", "Planta") or "Planta")

            valores.append(emp.id_empleado)
            cursor.execute(f"UPDATE empleados SET {', '.join(sets)} WHERE id = ?;", valores)

            if conexion_alt is None:
                conn.commit()
            return True

        except Exception as e:
            if conexion_alt is None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ERROR RepoRRHH.actualizar_empleado]: {e}")
            raise e

    @staticmethod
    def guardar_empleado(emp: Empleado, conexion_alt: Optional[sqlite3.Connection] = None) -> bool:
        if getattr(emp, "id_empleado", None):
            return RepositorioRRHH.actualizar_empleado(emp, conexion_alt=conexion_alt)
        return RepositorioRRHH.crear_empleado(emp, conexion_alt=conexion_alt)

    @staticmethod
    def cambiar_estado_empleado(id_empleado: int, nuevo_estado: bool, conexion_alt: Optional[sqlite3.Connection] = None) -> bool:
        conn = conexion_alt or _obtener_conexion_segura()
        cursor = conn.cursor()
        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            cols_emp = RepositorioRRHH._obtener_columnas_tabla(cursor, "empleados")
            if "activo" not in cols_emp:
                cursor.execute("ALTER TABLE empleados ADD COLUMN activo INTEGER DEFAULT 1;")

            valor_estado = 1 if nuevo_estado else 0
            cursor.execute(
                "UPDATE empleados SET activo = ? WHERE id = ?;",
                (valor_estado, id_empleado),
            )

            if conexion_alt is None:
                conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if conexion_alt is None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ERROR RepoRRHH.cambiar_estado_empleado]: {e}")
            return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = "", incluir_inactivos: bool = False, conexion_alt: Optional[sqlite3.Connection] = None) -> List[Empleado]:
        conn = conexion_alt or _obtener_conexion_segura()
        cursor = conn.cursor()
        cols_emp = RepositorioRRHH._obtener_columnas_tabla(cursor, "empleados")

        col_vinculo = "e.tipo_vinculo" if "tipo_vinculo" in cols_emp else "'Planta' AS tipo_vinculo"
        col_activo = "COALESCE(e.activo, 1) AS activo" if "activo" in cols_emp else "1 AS activo"

        query = f"""
            SELECT e.id AS id_empleado, e.id_persona, e.legajo, e.cargo,
                   e.sector, {col_vinculo}, e.sueldo, {col_activo},
                   p.nro_documento, p.nombres, p.apellidos, p.email, p.telefono
            FROM empleados e
            JOIN personas p ON e.id_persona = p.id
            WHERE 1 = 1
        """
        parametros = []

        if not incluir_inactivos and "activo" in cols_emp:
            query += " AND COALESCE(e.activo, 1) = 1"

        if criterio_busqueda:
            query += """
                AND (p.nombres LIKE ? OR p.apellidos LIKE ? OR e.legajo LIKE ? OR p.nro_documento LIKE ?)
            """
            patron = f"%{criterio_busqueda}%"
            parametros.extend([patron, patron, patron, patron])

        query += " ORDER BY e.id ASC;"
        cursor.execute(query, parametros)
        filas = cursor.fetchall()

        lista: List[Empleado] = []
        for f in filas:
            emp = Empleado(
                id_empleado=f["id_empleado"],
                id_persona=f["id_persona"],
                nro_documento=f["nro_documento"],
                nombres=f["nombres"],
                apellidos=f["apellidos"],
                legajo=f["legajo"],
                cargo=f["cargo"],
                sector=f["sector"],
                tipo_vinculo=f["tipo_vinculo"],
                sueldo=f["sueldo"],
                email=f["email"],
                telefono=f["telefono"],
                activo=bool(f["activo"]),
            )
            lista.append(emp)

        return lista