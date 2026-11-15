"""
===============================================================================
ENTIDAD DE DOMINIO: PROVEEDOR (dominio/entidades_proveedores.py)
===============================================================================
Modelo de datos puro que representa a un proveedor o suministrador comercial
dentro del sistema de gestión "Frankie".
===============================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Proveedor:
    """
    Entidad que encapsula los datos comerciales, fiscales y de contacto de un proveedor,
    compatible con la herencia de la tabla 'personas' en 3FN.
    """
    razon_social: str
    nro_documento: str
    rubro: str = ""
    telefono: str = ""
    email: str = ""
    contacto_secundario: str = ""
    tipo_persona: str = "Juridica"
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento: str = "CUIT"
    domicilio: str = ""
    ciudad: str = ""
    provincia: str = ""
    codigo_postal: str = ""
    id: Optional[int] = None
    id_persona: Optional[int] = None

    @property
    def id_proveedor(self) -> Optional[int]:
        """Alias retrocompatible para la capa visual."""
        return self.id

    @property
    def nombre_comercial(self) -> str:
        """Retorna la razón social o nombre comercial del proveedor."""
        if self.razon_social and self.razon_social.strip():
            return self.razon_social.strip()
        return f"{self.nombres or ''} {self.apellidos or ''}".strip()