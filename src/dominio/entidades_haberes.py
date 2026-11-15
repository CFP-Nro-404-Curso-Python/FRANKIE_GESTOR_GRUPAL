"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE HABERES (dominio/entidades_haberes.py)
===============================================================================
Modela la entidad LiquidacionHaberes para el cálculo y gestión de haberes.
===============================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LiquidacionHaberes:
    """ Entidad de dominio que representa un recibo o liquidación de haberes. """
    id_empleado: int
    periodo: str
    sueldo_basico: float = 0.0
    total_remunerativo: float = 0.0
    total_no_remunerativo: float = 0.0
    total_descuentos: float = 0.0
    sueldo_neto: float = 0.0
    id_liquidacion: Optional[int] = None

    @property
    def neto_a_cobrar(self) -> float:
        """ Propiedad de conveniencia para acceder al neto. """
        return self.sueldo_neto