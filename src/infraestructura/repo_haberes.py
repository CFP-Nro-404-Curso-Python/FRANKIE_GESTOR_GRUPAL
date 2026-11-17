"""
===============================================================================
REPOSITORIO DE HABERES Y LIQUIDACIONES (src/infraestructura/repo_haberes.py)
===============================================================================
"""

from typing import List, Dict, Any, Optional
import sqlite3

from dominio.entidades_haberes import LiquidacionHaberes
from infraestructura.conexion import ConexionDB


def _resolver_tabla_liquidaciones(cursor) -> str:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('liquidaciones', 'liquidaciones_haberes');"
    )
    nombres = {r[0] for r in cursor.fetchall()}
    if "liquidaciones_haberes" in nombres:
        return "liquidaciones_haberes"
    if "liquidaciones" in nombres:
        return "liquidaciones"
    return "liquidaciones_haberes"


class RepositorioHaberes:
    """
    Repositorio encargado de procesar, almacenar y recuperar las liquidaciones
    de sueldos e historial remunerativo de los empleados en SQLite.
    """

    @staticmethod
    def calcular_liquidacion(
        id_empleado: int,
        periodo: str,
        basico: float,
        antiguedad_anios: int = 0,
        aplica_presentismo: bool = False,
        horas_extra: float = 0.0,
        feriados: float = 0.0,
        ventas: float = 0.0,
        adelanto: float = 0.0,
        aplica_jubilacion: bool = True,
        aplica_pami: bool = True,
        aplica_obra_social: bool = True,
        aplica_sindicato: bool = True,
        conexion_alt: Optional[sqlite3.Connection] = None
    ) -> Dict[str, Any]:
        id_emp_seguro: int = int(id_empleado) if id_empleado is not None else 0

        # 1. Haberes Remunerativos
        monto_antiguedad = basico * (0.01 * antiguedad_anios)
        monto_presentismo = ((basico + monto_antiguedad) * 0.0833) if aplica_presentismo else 0.0

        valor_hora = basico / 200.0
        monto_horas_extra = horas_extra * (valor_hora * 1.5)

        valor_dia = basico / 20.0
        monto_feriados = feriados * (valor_dia * 2.0)

        monto_comision = ventas * 0.05

        total_remunerativo = (
            basico +
            monto_antiguedad +
            monto_presentismo +
            monto_horas_extra +
            monto_feriados +
            monto_comision
        )

        # 2. Haberes No Remunerativos
        total_no_remunerativo = 0.00

        # 3. Deducciones
        jubilacion = (total_remunerativo * 0.11) if aplica_jubilacion else 0.0
        pami = (total_remunerativo * 0.03) if aplica_pami else 0.0
        obra_social = (total_remunerativo * 0.03) if aplica_obra_social else 0.0
        cuota_sindical = (total_remunerativo * 0.025) if aplica_sindicato else 0.0

        total_descuentos = jubilacion + pami + obra_social + cuota_sindical + adelanto

        # 4. Neto a Cobrar
        neto_a_cobrar = (total_remunerativo + total_no_remunerativo) - total_descuentos

        # 5. Persistencia
        conn = conexion_alt or ConexionDB().conexion
        cursor = conn.cursor()
        try:
            if conexion_alt is None:
                conn.execute("BEGIN TRANSACTION;")

            tabla = _resolver_tabla_liquidaciones(cursor)
            cursor.execute(f"PRAGMA table_info({tabla});")
            cols_disponibles = [c[1] for c in cursor.fetchall()]

            valores = {
                "id_empleado": id_emp_seguro,
                "periodo": periodo,
                "sueldo_basico": basico,
                "total_remunerativo": round(total_remunerativo, 2),
                "total_no_remunerativo": round(total_no_remunerativo, 2),
                "total_descuentos": round(total_descuentos, 2),
                "neto_a_cobrar": round(neto_a_cobrar, 2),
            }

            cols_insert = [c for c in [
                "id_empleado", "periodo", "sueldo_basico",
                "total_remunerativo", "total_no_remunerativo",
                "total_descuentos", "neto_a_cobrar"
            ] if c in cols_disponibles]

            sql = f"INSERT INTO {tabla} ({', '.join(cols_insert)}) VALUES ({', '.join(['?'] * len(cols_insert))});"
            cursor.execute(sql, [valores[c] for c in cols_insert])

            if conexion_alt is None:
                conn.commit()

        except Exception as e:
            if conexion_alt is None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise e

        return {
            "remunerativo": round(total_remunerativo, 2),
            "no_remunerativo": round(total_no_remunerativo, 2),
            "descuentos": round(total_descuentos, 2),
            "neto": round(neto_a_cobrar, 2),
            "desglose_deducciones": {
                "jubilacion": round(jubilacion, 2),
                "pami": round(pami, 2),
                "obra_social": round(obra_social, 2),
                "sindicato": round(cuota_sindical, 2),
                "adelanto": round(adelanto, 2),
            }
        }

    def guardar_liquidacion(self, liquidacion: LiquidacionHaberes) -> int:
        id_emp_seguro: int = int(liquidacion.id_empleado) if liquidacion.id_empleado is not None else 0
        id_liq_seguro: int = int(liquidacion.id) if liquidacion.id is not None else 0

        with ConexionDB() as conexion:
            cursor = conexion.cursor()
            tabla = _resolver_tabla_liquidaciones(cursor)
            cursor.execute(f"PRAGMA table_info({tabla});")
            cols = [c[1] for c in cursor.fetchall()]
            id_col = "id_liquidacion" if "id_liquidacion" in cols else "id"

            if liquidacion.id is None:
                cols_insert = [c for c in ["id_empleado", "periodo", "sueldo_basico", "total_remunerativo", "total_no_remunerativo", "total_descuentos", "neto_a_cobrar"] if c in cols]
                valores = {
                    "id_empleado": id_emp_seguro,
                    "periodo": liquidacion.periodo,
                    "sueldo_basico": liquidacion.sueldo_basico,
                    "total_remunerativo": liquidacion.total_remunerativo,
                    "total_no_remunerativo": getattr(liquidacion, "total_no_remunerativo", 0.0),
                    "total_descuentos": liquidacion.total_descuentos,
                    "neto_a_cobrar": liquidacion.neto_a_cobrar,
                }
                sql = f"INSERT INTO {tabla} ({', '.join(cols_insert)}) VALUES ({', '.join(['?'] * len(cols_insert))});"
                cursor.execute(sql, [valores[c] for c in cols_insert])
                liquidacion.id = cursor.lastrowid
            else:
                sets = []
                vals = []
                if "id_empleado" in cols:
                    sets.append("id_empleado = ?"); vals.append(id_emp_seguro)
                if "periodo" in cols:
                    sets.append("periodo = ?"); vals.append(liquidacion.periodo)
                if "sueldo_basico" in cols:
                    sets.append("sueldo_basico = ?"); vals.append(liquidacion.sueldo_basico)
                if "total_remunerativo" in cols:
                    sets.append("total_remunerativo = ?"); vals.append(liquidacion.total_remunerativo)
                if "total_descuentos" in cols:
                    sets.append("total_descuentos = ?"); vals.append(liquidacion.total_descuentos)
                if "neto_a_cobrar" in cols:
                    sets.append("neto_a_cobrar = ?"); vals.append(liquidacion.neto_a_cobrar)
                vals.append(id_liq_seguro)
                cursor.execute(f"UPDATE {tabla} SET {', '.join(sets)} WHERE {id_col} = ?;", vals)

        return int(liquidacion.id) if liquidacion.id is not None else 0

    def listar_liquidaciones(self) -> List[LiquidacionHaberes]:
        with ConexionDB() as conexion:
            cursor = conexion.cursor()
            tabla = _resolver_tabla_liquidaciones(cursor)
            cursor.execute(f"SELECT * FROM {tabla};")
            filas = cursor.fetchall()

            liquidaciones = []
            for fila in filas:
                liq = LiquidacionHaberes(
                    id_empleado=int(fila["id_empleado"]),
                    periodo=str(fila["periodo"]),
                    sueldo_basico=float(fila["sueldo_basico"]) if "sueldo_basico" in fila.keys() else 0.0,
                    total_remunerativo=float(fila["total_remunerativo"]),
                    total_descuentos=float(fila["total_descuentos"]),
                    neto_a_cobrar=float(fila["neto_a_cobrar"]),
                    id=int(fila["id_liquidacion"]) if "id_liquidacion" in fila.keys() else int(fila["id"]),
                )
                liquidaciones.append(liq)

            return liquidaciones