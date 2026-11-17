"""
===============================================================================
MÓDULO DE DOMINIO: STOCK E INVENTARIO (src/dominio/entidades_stock.py)
===============================================================================
Modela el catálogo de productos con stock mínimo (75) y regla clara de reposición.
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proveedor:
    """ Representa un Proveedor / Acreedor dentro del sistema comercial. """
    razon_social: str
    rubro: str
    tipo_documento: str = "CUIT"
    nro_documento: str = ""
    contacto_secundario: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    domicilio: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    tipo_persona: str = "Juridica"
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    id: Optional[int] = None
    id_persona: Optional[int] = None
    activo: bool = True

    @property
    def nombre_comercial(self) -> str:
        if self.tipo_persona == "Fisica":
            return f"{self.apellidos or ''}, {self.nombres or ''}".strip(", ")
        return self.razon_social or ""


@dataclass
class Producto:
    """ Representa un Artículo / Producto dentro del Inventario. """
    codigo: str
    descripcion: str
    id_proveedor: int
    precio_costo: float = 0.0
    precio_venta: float = 0.0
    id: Optional[int] = None
    stock_actual: int = 0
    stock_minimo: int = 75  # Regla de negocio: stock mínimo por defecto = 75
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    vencimiento: Optional[str] = None
    activo: bool = True

    nombre_proveedor: str = field(default="", repr=False)

    def __post_init__(self):
        if hasattr(self, 'stock') and self.stock is not None:
            self.stock_actual = self.stock

        if not self.stock_minimo or self.stock_minimo <= 0:
            self.stock_minimo = 75

        if not self.precio_venta or self.precio_venta == 0.0:
            self.precio_venta = round(float(self.precio_costo) * 1.20, 2)

    @property
    def stock(self) -> int:
        return self.stock_actual

    @stock.setter
    def stock(self, val: int):
        self.stock_actual = val

    @property
    def id_producto(self) -> Optional[int]:
        return self.id

    @property
    def requiere_reposicion(self) -> bool:
        """
        Regla de Negocio:
        Retorna True si el stock actual es inferior o igual al stock mínimo (75 unidades).
        """
        return self.stock_actual <= self.stock_minimo

    @property
    def margen_ganancia(self) -> float:
        return self.precio_venta - self.precio_costo

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.descripcion} - Stock: {self.stock_actual} (Mín: {self.stock_minimo})"