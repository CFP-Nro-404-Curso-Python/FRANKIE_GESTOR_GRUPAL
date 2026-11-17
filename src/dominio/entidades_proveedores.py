"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE PROVEEDORES (src/dominio/entidades_proveedores.py)
===============================================================================
Modela el proveedor comercial integrando la herencia de personas, datos fiscales
y propiedades de compatibilidad para la interfaz gráfica.
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
        """
        Propiedad inteligente: Retorna la razón social si es jurídica,
        o el apellido y nombre si es persona física.
        """
        if self.tipo_persona == "Fisica":
            return f"{self.apellidos or ''}, {self.nombres or ''}".strip(", ")
        return self.razon_social or ""

    def __str__(self) -> str:
        return f"{self.nombre_comercial} (Rubro: {self.rubro})"