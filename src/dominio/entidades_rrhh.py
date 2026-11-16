"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE RECURSOS HUMANOS (src/dominio/entidades_rrhh.py)
===============================================================================
"""

from typing import Optional
from dominio.entidades_persona import Persona

CARGOS = [
    "Gerente",
    "Administrador",
    "Empleado_Admin",
    "Empleado_Ventas",
    "Empleado_Compras"
]

SECTORES = [
    "Administración",
    "Ventas",
    "Compras",
    "Inventario",
    "Gerencia"
]

TIPOS_VINCULO = [
    "Planta",
    "Contratado",
    "Pasante",
    "Propietario"
]


class Empleado(Persona):
    """
    Entidad que representa a un empleado de la empresa.
    """
    def __init__(
        self,
        nro_documento: str,
        nombres: str,
        legajo: str,
        cargo: str,
        sector: str,
        sueldo: float,
        apellidos: Optional[str] = None,
        tipo_documento: str = "CUIT",
        tipo_vinculo: str = "Planta",
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        domicilio: Optional[str] = None,
        ciudad: Optional[str] = None,
        provincia: Optional[str] = None,
        codigo_postal: Optional[str] = None,
        id_empleado: Optional[int] = None,
        id_persona: Optional[int] = None,
        activo: bool = True
    ):
        super().__init__(
            id_persona=id_persona,
            nro_documento=nro_documento,
            nombres=nombres,
            apellidos=apellidos or "",
            email=email or "",
            telefono=telefono or ""
        )
        self.tipo_documento = tipo_documento
        self.id_empleado = id_empleado
        self.id_persona = id_persona
        self.legajo = legajo
        self.cargo = cargo
        self.sector = sector
        self.tipo_vinculo = tipo_vinculo
        self.sueldo = float(sueldo or 0.0)
        self.activo = activo
        self.domicilio = domicilio or ""
        self.ciudad = ciudad or ""
        self.provincia = provincia or ""
        self.codigo_postal = codigo_postal or ""

    def obtener_nombre_completo(self) -> str:
        if self.apellidos and self.nombres:
            return f"{self.apellidos}, {self.nombres}"
        return self.nombres or self.apellidos or "Sin Nombre"

    def __str__(self) -> str:
        return f"Empleado [{self.legajo}] - {self.obtener_nombre_completo()} ({self.cargo})"