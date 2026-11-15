"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO DE RRHH (src/infraestructura/repo_rrhh.py)
===============================================================================
Gestiona la persistencia de datos en 'personas' y 'empleados'.
===============================================================================
"""

from typing import List, Optional
from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import Empleado, limpiar_documento, TIPOS_VINCULO, SECTORES, CARGOS


class RepositorioRRHH:
    """ Capa de acceso a datos para la gestión del personal y registros de personas. """

    @staticmethod
    def asegurar_columnas() -> None:
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(empleados)")
                columnas = [col[1] for col in cursor.fetchall()]
                if "activo" not in columnas:
                    cursor.execute("ALTER TABLE empleados ADD COLUMN activo INTEGER DEFAULT 1")
                if "tipo_vinculo" not in columnas:
                    cursor.execute("ALTER TABLE empleados ADD COLUMN tipo_vinculo TEXT DEFAULT 'Planta'")
                conn.commit()
        except Exception as e:
            print(f"Error al verificar/actualizar columnas en empleados: {e}")

    @staticmethod
    def existe_documento(nro_documento: str, id_persona_actual: Optional[int] = None) -> bool:
        doc_limpio = limpiar_documento(nro_documento)
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()
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
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM empleados")
                row = cursor.fetchone()
                ultimo_id = row[0] if (row and row[0] is not None) else 0
                return f"EMP-{(ultimo_id + 1):03d}"
        except Exception as e:
            print(f"Error al calcular legajo: {e}")
            return "EMP-001"

    @staticmethod
    def crear_empleado(empleado: Empleado) -> bool:
        """Inserta un nuevo empleado en una transacción atómica."""
        RepositorioRRHH.asegurar_columnas()
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()

                sql_persona = """
                    INSERT INTO personas (tipo_persona, nombres, apellidos, razon_social, tipo_documento, nro_documento, telefono, email, domicilio, ciudad, provincia, codigo_postal)
                    VALUES ('Fisica', ?, ?, NULL, 'DNI', ?, ?, ?, '', '', '', '')
                """
                cursor.execute(sql_persona, (
                    empleado.nombres or "Sin Nombre",
                    empleado.apellidos or "Sin Apellido",
                    empleado.nro_documento or "",
                    empleado.telefono or "",
                    empleado.email or ""
                ))

                id_persona_generado = cursor.lastrowid

                cargo_val = empleado.cargo if empleado.cargo in CARGOS else "empleado_ventas"
                sector_val = empleado.sector if empleado.sector in SECTORES else "Ventas"
                vinculo_val = empleado.tipo_vinculo if empleado.tipo_vinculo in TIPOS_VINCULO else "Planta"

                sql_empleado = """
                    INSERT INTO empleados (id_persona, id_usuario, legajo, cargo, sector, tipo_vinculo, sueldo, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """
                cursor.execute(sql_empleado, (
                    id_persona_generado,
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
            print(f"[Error RepoRRHH]: Falló la creación del empleado -> {e}")
            return False

    @staticmethod
    def actualizar_empleado(empleado: Empleado) -> bool:
        """Actualiza la información de un empleado existente."""
        RepositorioRRHH.asegurar_columnas()
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE personas
                    SET nombres = ?, apellidos = ?, nro_documento = ?, telefono = ?, email = ?
                    WHERE id = ?
                """, (
                    empleado.nombres or "",
                    empleado.apellidos or "",
                    empleado.nro_documento or "",
                    empleado.telefono or "",
                    empleado.email or "",
                    empleado.id
                ))

                cargo_val = empleado.cargo if empleado.cargo in CARGOS else "empleado_ventas"
                sector_val = empleado.sector if empleado.sector in SECTORES else "Ventas"
                vinculo_val = empleado.tipo_vinculo if empleado.tipo_vinculo in TIPOS_VINCULO else "Planta"

                cursor.execute("""
                    UPDATE empleados
                    SET legajo = ?, cargo = ?, sector = ?, tipo_vinculo = ?, sueldo = ?
                    WHERE id = ?
                """, (
                    empleado.legajo or "",
                    cargo_val,
                    sector_val,
                    vinculo_val,
                    empleado.sueldo or 0.0,
                    empleado.id_empleado
                ))

                conn.commit()
                return True
        except Exception as e:
            print(f"[Error RepoRRHH]: Falló la actualización del empleado -> {e}")
            return False

    @staticmethod
    def cambiar_estado_empleado(id_empleado: int, nuevo_estado: int) -> bool:
        """Realiza la baja lógica o activación de un empleado."""
        RepositorioRRHH.asegurar_columnas()
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE empleados SET activo = ? WHERE id = ?", (nuevo_estado, id_empleado))
                conn.commit()
                return True
        except Exception as e:
            print(f"[Error RepoRRHH]: Falló el cambio de estado -> {e}")
            return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = "", incluir_inactivos: bool = False) -> List[Empleado]:
        RepositorioRRHH.asegurar_columnas()
        sql = """
            SELECT e.id, p.id, p.nro_documento, p.nombres, p.apellidos,
                   e.legajo, e.cargo, e.sector, e.tipo_vinculo, e.sueldo,
                   p.email, p.telefono, COALESCE(e.activo, 1) as activo, e.id_usuario
            FROM empleados e
            INNER JOIN personas p ON e.id_persona = p.id
            WHERE 1 = 1
        """
        parametros = []
        if not incluir_inactivos:
            sql += " AND COALESCE(e.activo, 1) = 1"

        if criterio_busqueda:
            sql += """
                AND (p.nombres LIKE ? OR p.apellidos LIKE ? OR e.legajo LIKE ? OR p.nro_documento LIKE ? OR p.email LIKE ?)
            """
            patron = f"%{criterio_busqueda}%"
            parametros.extend([patron, patron, patron, patron, patron])

        sql += " ORDER BY e.id ASC"

        empleados = []
        try:
            with ConexionDB() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, parametros)
                filas = cursor.fetchall()

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
                        telefono=f[11],
                        id_usuario=f[13]
                    )
                    emp.activo = bool(f[12])
                    empleados.append(emp)
        except Exception as e:
            print(f"[Error RepoRRHH]: Falló la consulta de empleados -> {e}")

        return empleados