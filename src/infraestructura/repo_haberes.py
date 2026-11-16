"""
===============================================================================
REPOSITORIO DE HABERES Y LIQUIDACIONES (src/infraestructura/repo_haberes.py)
===============================================================================
Estrategia y Buenas Prácticas Aplicadas:
1. Conexión Centralizada: Utiliza 'ConexionDB' mediante el gestor de contexto (with),
   garantizando transacciones atómicas seguras, commits automáticos y control de errores.
2. Sintonizado con la Base de Datos: Persiste directamente en la tabla oficial
   'liquidaciones_haberes' respetando las claves foráneas del proyecto.
===============================================================================
"""

from typing import List, Dict, Any
from dominio.entidades_haberes import LiquidacionHaberes
from infraestructura.conexion import ConexionDB


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
        aplica_presentismo: bool = True,
        horas_extra: float = 0.0,
        feriados: float = 0.0,
        ventas: float = 0.0,
        adelanto: float = 0.0,
        aplica_jubilacion: bool = True,
        aplica_pami: bool = True,
        aplica_obra_social: bool = True,
        aplica_sindicato: bool = True
    ) -> Dict[str, Any]:
        """
        Realiza el cálculo de conceptos remunerativos, deducciones de ley
        y persiste automáticamente el resultado en la tabla 'liquidaciones_haberes'.
        """
        # Conversión segura a entero para satisfacer el tipado estricto
        id_emp_seguro: int = int(id_empleado) if id_empleado is not None else 0

        # 1. Haberes Remunerativos
        monto_antiguedad = basico * (0.01 * antiguedad_anios)
        monto_presentismo = (basico * 0.0833) if aplica_presentismo else 0.0

        valor_hora = basico / 160.0
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

        # 5. Persistencia atómica en la tabla oficial 'liquidaciones_haberes'
        with ConexionDB() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO liquidaciones_haberes (
                    id_empleado, periodo, sueldo_basico, 
                    total_remunerativo, total_no_remunerativo, 
                    total_descuentos, neto_a_cobrar
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id_emp_seguro,
                    periodo,
                    basico,
                    total_remunerativo,
                    total_no_remunerativo,
                    total_descuentos,
                    neto_a_cobrar
                )
            )

        return {
            "remunerativo": total_remunerativo,
            "no_remunerativo": total_no_remunerativo,
            "descuentos": total_descuentos,
            "neto": neto_a_cobrar,
            "desglose_deducciones": {
                "jubilacion": jubilacion,
                "pami": pami,
                "obra_social": obra_social,
                "sindicato": cuota_sindical,
                "adelanto": adelanto
            }
        }

    def guardar_liquidacion(self, liquidacion: LiquidacionHaberes) -> int:
        """
        Inserta una nueva liquidación o actualiza una existente usando el objeto de dominio.
        """
        id_emp_seguro: int = int(liquidacion.id_empleado) if liquidacion.id_empleado is not None else 0
        id_liq_seguro: int = int(liquidacion.id) if liquidacion.id is not None else 0

        with ConexionDB() as conexion:
            cursor = conexion.cursor()

            if liquidacion.id is None:
                cursor.execute(
                    """
                    INSERT INTO liquidaciones_haberes (
                        id_empleado, periodo, sueldo_basico, 
                        total_remunerativo, total_no_remunerativo, 
                        total_descuentos, neto_a_cobrar
                    )
                    VALUES (?, ?, ?, ?, 0.00, ?, ?)
                    """,
                    (
                        id_emp_seguro,
                        liquidacion.periodo,
                        liquidacion.sueldo_basico,
                        liquidacion.total_remunerativo,
                        liquidacion.total_descuentos,
                        liquidacion.neto_a_cobrar
                    )
                )
                liquidacion.id = cursor.lastrowid
            else:
                cursor.execute(
                    """
                    UPDATE liquidaciones_haberes 
                    SET id_empleado = ?, periodo = ?, sueldo_basico = ?, 
                        total_remunerativo = ?, total_descuentos = ?, neto_a_cobrar = ?
                    WHERE id_liquidacion = ?
                    """,
                    (
                        id_emp_seguro,
                        liquidacion.periodo,
                        liquidacion.sueldo_basico,
                        liquidacion.total_remunerativo,
                        liquidacion.total_descuentos,
                        liquidacion.neto_a_cobrar,
                        id_liq_seguro
                    )
                )
        return int(liquidacion.id) if liquidacion.id is not None else 0

    def listar_liquidaciones(self) -> List[LiquidacionHaberes]:
        """
        Recupera el historial completo de liquidaciones de haberes registradas.
        """
        with ConexionDB() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                SELECT id_liquidacion, id_empleado, periodo, sueldo_basico, 
                       total_remunerativo, total_descuentos, neto_a_cobrar
                FROM liquidaciones_haberes
                """
            )
            filas = cursor.fetchall()

            liquidaciones = []
            for fila in filas:
                liq = LiquidacionHaberes(
                    id_empleado=int(fila["id_empleado"]),
                    periodo=str(fila["periodo"]),
                    sueldo_basico=float(fila["sueldo_basico"]),
                    total_remunerativo=float(fila["total_remunerativo"]),
                    total_descuentos=float(fila["total_descuentos"]),
                    neto_a_cobrar=float(fila["neto_a_cobrar"]),
                    id=int(fila["id_liquidacion"])
                )
                liquidaciones.append(liq)

            return liquidaciones