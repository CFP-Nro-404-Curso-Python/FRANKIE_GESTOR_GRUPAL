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
# MODIFICADO DAVID: Comentamos el import redundante. Usamos directamente ConexionDB.
# import infraestructura.conexion as modulo_conexion
from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import (
    Empleado,
    limpiar_documento,
    TIPOS_VINCULO,
    SECTORES,
    CARGOS
)



# ===================================================================================
#  ⚠️ MODIFICACIÓN DAVID:
# ===================================================================================
#  Se comenta la función _obtener_conexion_segura.
#  
#  Motivo: Rompía el patrón Singleton y el gestor de contexto 'with' que definimos 
#  en la Semana 1, lo que podía causar bloqueos ('database is locked') al instanciar 
#  conexiones paralelas sueltas.
# ===================================================================================

# def _obtener_conexion_segura():
#     """
#     Función helper de resiliencia para obtener la conexión a la Base de Datos.
#     Soporta múltiples métodos de resolución según la estructura de ConexionDB.
#     """
#     if hasattr(ConexionDB, "obtener_conexion"):
#         return ConexionDB.obtener_conexion()
#     elif hasattr(ConexionDB, "get_connection"):
#         return ConexionDB.get_connection()
#     elif hasattr(modulo_conexion, "obtener_conexion"):
#         return modulo_conexion.obtener_conexion()
#     else:
#         instancia = ConexionDB()
#         if hasattr(instancia, "obtener_conexion"):
#             return instancia.obtener_conexion()
#         elif hasattr(instancia, "get_connection"):
#             return instancia.get_connection()
#         elif hasattr(instancia, "conexion"):
#             return instancia.conexion
#         raise AttributeError("No se encontró un método de conexión válido en ConexionDB.")


class RepositorioRRHH:
    """ Repositorio encargado de la persistencia de la entidad Empleado y liquidaciones. """

    
    # ==========================================================================
    #  ⚠️ MODIFICACIÓN DAVID:
    # ==========================================================================
    #  Se comenta el método asegurar_columnas().
    #
    #  Motivo: Un repositorio NUNCA debe ejecutar un ALTER TABLE. Modificar la 
    #  estructura de la base de datos es responsabilidad exclusiva del archivo 
    #  'db/esquema.sql'. 
    #  El esquema ya incluye estas columnas desde la última actualización.
    # ==========================================================================
    
    # @staticmethod
    # def asegurar_columnas():
    #     """
    #     Migración defensiva del esquema.
    #     Garantiza la presencia de 'activo' y 'tipo_vinculo' en la tabla 'empleados'
    #     si se ejecuta sobre bases de datos heredadas.
    #     """
    #     conn = _obtener_conexion_segura()
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute("PRAGMA table_info(empleados)")
    #         columnas = [col[1] for col in cursor.fetchall()]
    #         if "activo" not in columnas:
    #             cursor.execute("ALTER TABLE empleados ADD COLUMN activo INTEGER DEFAULT 1")
    #         if "tipo_vinculo" not in columnas:
    #             cursor.execute("ALTER TABLE empleados ADD COLUMN tipo_vinculo TEXT DEFAULT 'Planta'")
    #         conn.commit()
    #     except Exception as e:
    #         print(f"Error al verificar o migrar columnas en 'empleados': {e}")

    @staticmethod
    def existe_documento(nro_documento: str, id_persona_actual: Optional[int] = None) -> bool:
        """ Validación de Unicidad de Documento en la Base de Datos. """
        #  CÓDIGO ORIGINAL (Comentado por manejo manual de conexión)
        # -----------------------------------------------------------
        #
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # doc_limpio = limpiar_documento(nro_documento)
        # try:
        #     if id_persona_actual:
        #         cursor.execute("""
        #                        SELECT 1 FROM personas
        #                        WHERE REPLACE(REPLACE(nro_documento, '-', ''), ' ', '') = ?
        #                          AND id <> ?
        #                        """, (doc_limpio, id_persona_actual))
        #     else:
        #         cursor.execute("""
        #                        SELECT 1 FROM personas
        #                        WHERE REPLACE(REPLACE(nro_documento, '-', ''), ' ', '') = ?
        #                        """, (doc_limpio,))
        #     return cursor.fetchone() is not None
        # except Exception as e:
        #     print(f"Error al verificar duplicado de documento: {e}")
        #     return False


        #  NUEVO CÓDIGO REFACCIONADO (Con 'with ConexionDB() as db')
        # -----------------------------------------------------------

        doc_limpio = limpiar_documento(nro_documento)
        try:
            with ConexionDB() as db:
                cursor = db.cursor()
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

        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # try:
        #     cursor.execute("SELECT MAX(id) FROM empleados")
        #     row = cursor.fetchone()
        #     ultimo_id = row[0] if (row and row[0] is not None) else 0
        #     return f"EMP-{(ultimo_id + 1):03d}"
        # except Exception as e:
        #     print(f"Error al calcular el legajo: {e}")
        #     return "EMP-001"

        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()
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
        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # RepositorioRRHH.asegurar_columnas()
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # try:
        #     query_persona = """ ... """
        #     cursor.execute(...)
        #     id_persona_insertada = cursor.lastrowid
        #     cargo_val = empleado.cargo if empleado.cargo in CARGOS else "Empleado_Admin"
        #     ...
        #     query_empleado = """ ... """
        #     cursor.execute(...)
        #     conn.commit()
        #     return True
        # except Exception as e:
        #     conn.rollback()
        #     print(f"Error al crear empleado en la base de datos: {e}")
        #     return False

        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()

                # 1. Inserción en la tabla base 'personas'.
                query_persona = """
                                INSERT INTO personas (tipo_persona, nombres, apellidos, razon_social, tipo_documento,
                                                      nro_documento, telefono, email, domicilio, ciudad, provincia,
                                                      codigo_postal)
                                VALUES ('Fisica', ?, ?, NULL, 'CUIL', ?, ?, ?, '', '', '', '')
                                """
                cursor.execute(query_persona, (
                    empleado.nombres or "Sin Nombre",
                    empleado.apellidos or "Sin Apellido",
                    empleado.nro_documento or "",
                    empleado.telefono or "",
                    empleado.email or ""
                ))

                id_persona_insertada = cursor.lastrowid

                # Sanitización mediante las listas de opciones (Valores por descarte/fallback).
                cargo_val = empleado.cargo if getattr(empleado, 'cargo', None) in CARGOS else "Empleado_Admin"
                sector_val = empleado.sector if getattr(empleado, 'sector', None) in SECTORES else "Administración"
                vinculo_val = empleado.tipo_vinculo if getattr(empleado, 'tipo_vinculo', None) in TIPOS_VINCULO else "Planta"

                # 2. Inserción en la tabla derivada 'empleados'.
                query_empleado = """
                                 INSERT INTO empleados (id_persona, id_usuario, legajo, cargo, sector, tipo_vinculo, sueldo, activo)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                                 """
                cursor.execute(query_empleado, (
                    id_persona_insertada,
                    getattr(empleado, 'id_usuario', None),
                    empleado.legajo or RepositorioRRHH.generar_siguiente_legajo(),
                    cargo_val,
                    sector_val,
                    vinculo_val,
                    empleado.sueldo or 0.0
                ))
                # MODIFICADO: No se requiere conn.commit() explícito; el 'with' lo maneja automáticamente.
            return True
        except Exception as e:
            print(f"Error al crear empleado en la base de datos: {e}")
            return False

    @staticmethod
    def actualizar_empleado(empleado: Empleado) -> bool:
        """ Actualización Transaccional Multitabla (UPDATE personas + empleados). """

        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # try:
        #     cursor.execute(...) # Update personas
        #     cursor.execute(...) # Update empleados
        #     conn.commit()
        #     return True
        # except Exception as e:
        #     conn.rollback()
        #     print(f"Error al actualizar empleado: {e}")
        #     return False

        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE personas
                    SET nombres = ?, apellidos = ?, nro_documento = ?, telefono = ?, email = ?
                    WHERE id = ?
                """, (empleado.nombres or "", empleado.apellidos or "", empleado.nro_documento or "",
                      empleado.telefono or "", empleado.email or "", getattr(empleado, 'id', None)))

                cargo_val = empleado.cargo if getattr(empleado, 'cargo', None) in CARGOS else "Empleado_Admin"
                sector_val = empleado.sector if getattr(empleado, 'sector', None) in SECTORES else "Administración"
                vinculo_val = empleado.tipo_vinculo if getattr(empleado, 'tipo_vinculo', None) in TIPOS_VINCULO else "Planta"

                cursor.execute("""
                    UPDATE empleados
                    SET legajo = ?, cargo = ?, sector = ?, tipo_vinculo = ?, sueldo = ?
                    WHERE id = ?
                """, (getattr(empleado, 'legajo', ""), cargo_val, sector_val, vinculo_val,
                      getattr(empleado, 'sueldo', 0.0), getattr(empleado, 'id_empleado', None)))
            return True
        except Exception as e:
            print(f"Error al actualizar empleado: {e}")
            return False

    @staticmethod
    def cambiar_estado_empleado(id_empleado: int, nuevo_estado: int) -> bool:
        """ Baja Lógica / Reinstalación (Soft Delete). Preserva auditoría e historial. """

        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # RepositorioRRHH.asegurar_columnas()
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # try:
        #     cursor.execute("UPDATE empleados SET activo = ? WHERE id = ?", (nuevo_estado, id_empleado))
        #     conn.commit()
        #     return True
        # except Exception as e:
        #     conn.rollback()
        #     ...

        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()
                cursor.execute("UPDATE empleados SET activo = ? WHERE id = ?", (nuevo_estado, id_empleado))
            return True
        except Exception as e:
            print(f"Error al cambiar estado del empleado: {e}")
            return False

    @staticmethod
    def listar_empleados(criterio_busqueda: str = "", incluir_inactivos: bool = False) -> List[Empleado]:
        """ Recupera empleados uniendo 'empleados' y 'personas' mediante JOIN. """

        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # RepositorioRRHH.asegurar_columnas()
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # ... fetchall ...
        
        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()
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
        #  CÓDIGO ORIGINAL
        # -----------------
        #
        # conn = _obtener_conexion_segura()
        # cursor = conn.cursor()
        # ... 

        #  NUEVO CÓDIGO REFACCIONADO
        # ---------------------------

        try:
            with ConexionDB() as db:
                cursor = db.cursor()
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



"""
================================================================================
 📝 EXPLICACIÓN DEL REFACTORING PARA EL EQUIPO (Lectura recomendada)
================================================================================

Chicos, apliqué una refactorización en este archivo para alinear el código con 
el contrato de arquitectura que definimos en la Semana 1. Les detallo los 3 
cambios clave de forma sencilla para que los tengamos en cuenta en los próximos 
módulos (Ventas y Stock):

1. Borré `_obtener_conexion_segura`:

   Teníamos una función instanciando conexiones a la base de datos a mano. 
   En SQLite, si dos partes del programa (ej. Ventas y RRHH) intentan abrir la 
   base por separado al mismo tiempo, el sistema se bloquea y tira el error 
   'database is locked'. Al remover esto y usar directamente nuestra clase 
   `ConexionDB` (Patrón Singleton), garantizamos que todo el sistema comparta 
   una única "puerta de entrada". ¡Cero embotellamientos!


2. Borré `asegurar_columnas()` (y también los ALTER TABLE):

   La regla de oro de nuestra arquitectura es que el Repositorio solo lee o 
   escribe datos, nunca modifica la estructura física de las tablas. Si 
   necesitamos columnas nuevas (como pasó con 'activo' o 'tipo_vinculo'), 
   eso se agrega exclusivamente en el archivo `db/esquema.sql`. Si dejamos 
   sentencias ALTER TABLE en el código de Python, perdemos el control del 
   esquema y rompemos la separación de responsabilidades.

3. El gestor `with ConexionDB() as db:` (Transacciones automáticas):

   Fíjense que borré todos los `conn.commit()` y `conn.rollback()` manuales 
   que estaban en los métodos. Al encapsular las consultas dentro del bloque 
   `with`, Python se encarga de la transacción por nosotros. Si el código se 
   ejecuta perfecto, guarda los cambios automáticamente. Si ocurre un error 
   (una excepción), deshace la operación (rollback) al instante, evitando que 
   queden datos corruptos o a medio cargar. Escribimos menos código y 
   hacemos que el sistema sea a prueba de balas.
================================================================================
"""