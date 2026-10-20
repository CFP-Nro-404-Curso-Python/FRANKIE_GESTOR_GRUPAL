"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO DE HABERES (repo_haberes.py)
===============================================================================
Maneja la lógica de cálculo e inserción de liquidaciones utilizando la conexión
centralizada (ConexionDB).
===============================================================================
"""

import sqlite3
from typing import Dict, Any, Optional
from infraestructura.conexion import ConexionDB


class RepositorioHaberes:
    """ Repositorio encargado de los cálculos y persistencia de liquidaciones. """

    @classmethod
    def calcular_liquidacion(
            cls,
            id_empleado: int,
            periodo: str,
            basico: float = 0.0,
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
    ) -> Dict[str, float]:
        """
        Calcula la liquidación de haberes e inserta/actualiza el registro en la BD.
        """
        # 1. Cálculos de Conceptos Remunerativos
        monto_antiguedad = basico * (0.01 * antiguedad_anios)
        subtotal_base = basico + monto_antiguedad

        monto_presentismo = (subtotal_base * 0.0833) if aplica_presentismo else 0.0

        valor_hora = basico / 200.0 if basico > 0 else 0.0
        monto_horas_extra = horas_extra * valor_hora * 1.5
        monto_feriados = feriados * valor_hora * 2.0
        monto_comision_ventas = ventas * 0.015

        remunerativo = subtotal_base + monto_presentismo + monto_horas_extra + monto_feriados + monto_comision_ventas
        no_remunerativo = 0.0

        # 2. Cálculos de Deducciones
        desc_jubilacion = (remunerativo * 0.11) if aplica_jubilacion else 0.0
        desc_pami = (remunerativo * 0.03) if aplica_pami else 0.0
        desc_obra_social = (remunerativo * 0.03) if aplica_obra_social else 0.0
        desc_sindicato = (remunerativo * 0.025) if aplica_sindicato else 0.0

        descuentos = desc_jubilacion + desc_pami + desc_obra_social + desc_sindicato + adelanto
        neto = (remunerativo + no_remunerativo) - descuentos

        resultado = {
            "remunerativo": round(remunerativo, 2),
            "no_remunerativo": round(no_remunerativo, 2),
            "descuentos": round(descuentos, 2),
            "neto": round(neto, 2)
        }

        # 3. Persistencia en la Base de Datos
        cls._guardar_en_bd(id_empleado, periodo, resultado, conexion_alt)

        return resultado

    @classmethod
    def _guardar_en_bd(
            cls,
            id_empleado: int,
            periodo: str,
            res: Dict[str, float],
            conexion_alt: Optional[sqlite3.Connection] = None
    ) -> None:
        """
        Guarda los resultados usando el Singleton ConexionDB() o una conexión
        alternativa si se le provee (para tests).
        """
        query = """
                INSERT INTO liquidaciones (id_empleado, periodo, total_remunerativo, total_no_remunerativo, \
                                           total_descuentos, neto_a_cobrar) \
                VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(id_empleado, periodo) DO \
                UPDATE SET
                    total_remunerativo = excluded.total_remunerativo, \
                    total_no_remunerativo = excluded.total_no_remunerativo, \
                    total_descuentos = excluded.total_descuentos, \
                    neto_a_cobrar = excluded.neto_a_cobrar; \
                """

        # Si le pasamos una conexión directa (ej. BD temporal de prueba), la usa.
        # De lo contrario, utiliza la conexión Singleton compartida con todo el equipo.
        if conexion_alt:
            cursor = conexion_alt.cursor()
            cursor.execute(query, (
                id_empleado, periodo, res["remunerativo"],
                res["no_remunerativo"], res["descuentos"], res["neto"]
            ))
            conexion_alt.commit()
        else:
            with ConexionDB() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    id_empleado, periodo, res["remunerativo"],
                    res["no_remunerativo"], res["descuentos"], res["neto"]
                ))
                # Nota: __exit__ de ConexionDB hace el conn.commit() automáticamente.