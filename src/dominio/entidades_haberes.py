"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE HABERES (src/dominio/entidades_haberes.py)
===============================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LiquidacionHaberes:
    """
    Entidad de dominio que representa el recibo o liquidación de haberes
    de un empleado para un período fiscal determinado.
    """
    id_empleado: int
    periodo: str  # Formato AAAA-MM
    sueldo_basico: float = 0.0
    antiguedad_monto: float = 0.0
    presentismo_monto: float = 0.0
    horas_extra_monto: float = 0.0
    feriados_monto: float = 0.0
    comisiones_ventas: float = 0.0
    total_remunerativo: float = 0.0
    jubilacion: float = 0.0
    pami: float = 0.0
    obra_social: float = 0.0
    sindicato: float = 0.0
    adelantos: float = 0.0
    total_descuentos: float = 0.0
    neto_a_cobrar: float = 0.0
    id: Optional[int] = None

    # --- Propiedades de compatibilidad para el Linter y Repositorio ---
    @property
    def id_liquidacion(self) -> Optional[int]:
        return self.id

    @id_liquidacion.setter
    def id_liquidacion(self, valor: Optional[int]):
        self.id = valor

    @property
    def sueldo_neto(self) -> float:
        return self.neto_a_cobrar

    @sueldo_neto.setter
    def sueldo_neto(self, valor: float):
        self.neto_a_cobrar = valor

    @property
    def periodo_formateado(self) -> str:
        parts = self.periodo.split("-")
        if len(parts) == 2:
            return f"Mes {parts[1]} / Año {parts[0]}"
        return self.periodo