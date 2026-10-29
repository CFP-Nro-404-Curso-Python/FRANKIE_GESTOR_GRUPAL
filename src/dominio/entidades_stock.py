"""
===============================================================================
MÓDULO DE DOMINIO: STOCK E INVENTARIO (dominio/entidades_stock.py)
===============================================================================
Modelo de datos puro que representa los productos y artículos del inventario
dentro del sistema de gestión "Frankie".
===============================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """
    Entidad que representa un artículo dentro del inventario físico y de stock.
    """
    codigo: str
    descripcion: str
    categoria: str
    id_proveedor: int
    stock_actual: int = 0
    stock_minimo: int = 5
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    ubicacion: str = ""
    vencimiento: Optional[str] = None
    id: Optional[int] = None
    nombre_proveedor: Optional[str] = None

    @property
    def id_producto(self) -> Optional[int]:
        """Alias retrocompatible para la capa visual."""
        return self.id

    @property
    def requiere_reposicion(self) -> bool:
        """Evalúa si el stock actual está por debajo o en el mínimo."""
        stock_act = self.stock_actual if self.stock_actual is not None else 0
        stock_min = self.stock_minimo if self.stock_minimo is not None else 0
        return stock_act <= stock_min