"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE RECURSOS HUMANOS (entidades_rrhh.py)
===============================================================================
Estrategia y Reglas de Dominio:
1. Python Puro: Cero dependencias de librerías externas, bases de datos o Tkinter.
2. Jerarquía de Clases: Superclase 'Persona' (datos fiscales/contacto) y
   subclase 'Empleado' (legajos, cargos, sectores y sueldo base).
3. Constantes de Dominio: Listas oficiales para combos de selección en UI.
===============================================================================
"""

from typing import Optional

# =============================================================================
# CONSTANTES GLOBALES DE DOMINIO (RRHH) - Sincronizadas con la BD
# =============================================================================
CARGOS = [
    "Gerente",
    "Administrador",
    "Empleado_Admin",
    "Empleado_Ventas",
    "Empleado_Compras"
]

SECTORES = [
    "Gestión",
    "Ventas",
    "Compras",
    "Administración",
    "Recursos Humanos"
]

TIPOS_VINCULO = [
    "Planta",
    "Contratado",
    "Pasante",
    "Propietario"
]


def limpiar_documento(doc: str) -> str:
    """
    Elimina guiones, puntos y espacios, dejando únicamente los caracteres numéricos.
    Vital para estandarizar CUITs/DNI en las validaciones defensivas.
    """
    if not doc:
        return ""
    return "".join(caracter for caracter in str(doc) if caracter.isdigit())


class Persona:
    """
    Clase base que representa a una persona dentro del sistema.
    Coincide estructuralmente con la tabla normalizada 'personas' (3FN).
    """

    def __init__(
            self,
            nro_documento: str,
            nombres: str,
            apellidos: Optional[str] = None,
            tipo_documento: str = "CUIT",
            tipo_persona: str = "Fisica",
            email: Optional[str] = None,
            telefono: Optional[str] = None,
            razon_social: Optional[str] = None,
            domicilio: Optional[str] = None,
            ciudad: Optional[str] = None,
            provincia: Optional[str] = None,
            codigo_postal: Optional[str] = None,
            id: Optional[int] = None,
            id_persona: Optional[int] = None
    ) -> None:
        self.id = id if id is not None else id_persona
        self.tipo_persona = tipo_persona
        self.nombres = nombres
        self.apellidos = apellidos
        self.razon_social = razon_social
        self.tipo_documento = tipo_documento
        self.nro_documento = limpiar_documento(nro_documento)
        self.telefono = telefono
        self.email = email
        self.domicilio = domicilio
        self.ciudad = ciudad
        self.provincia = provincia
        self.codigo_postal = codigo_postal

    @property
    def id_persona(self) -> Optional[int]:
        """Alias retrocompatible para evitar cualquier error de atributo."""
        return self.id

    @id_persona.setter
    def id_persona(self, val: Optional[int]) -> None:
        self.id = val

    def obtener_nombre_completo(self) -> str:
        """ Retorna el nombre formateado o la razón social según corresponda. """
        if self.tipo_persona == "Fisica" and self.apellidos:
            return f"{self.apellidos}, {self.nombres}"
        return self.razon_social or self.nombres


class Empleado(Persona):
    """
    Clase derivada que representa a un empleado de la empresa.
    Hereda de Persona e incorpora los atributos laborales de la tabla 'empleados'.
    """

    def __init__(
            self,
            nro_documento: str,
            nombres: str,
            legajo: str,
            cargo: str,
            sector: str,
            sueldo: float,
            tipo_vinculo: str = "Planta",
            apellidos: Optional[str] = None,
            id_usuario: Optional[int] = None,
            tipo_documento: str = "CUIT",
            email: Optional[str] = None,
            telefono: Optional[str] = None,
            domicilio: Optional[str] = None,
            ciudad: Optional[str] = None,
            provincia: Optional[str] = None,
            codigo_postal: Optional[str] = None,
            id_empleado: Optional[int] = None,
            id_persona: Optional[int] = None,
            id: Optional[int] = None,
            activo: bool = True
    ) -> None:
        super().__init__(
            nro_documento=nro_documento,
            nombres=nombres,
            apellidos=apellidos,
            tipo_documento=tipo_documento,
            tipo_persona="Fisica",
            email=email,
            telefono=telefono,
            domicilio=domicilio,
            ciudad=ciudad,
            provincia=provincia,
            codigo_postal=codigo_postal,
            id=id,
            id_persona=id_persona
        )

        self.id_empleado = id_empleado
        self.id_usuario = id_usuario
        self.legajo = legajo
        self.cargo = cargo if cargo in CARGOS else CARGOS[0]
        self.sector = sector if sector in SECTORES else SECTORES[0]
        self.sueldo = float(sueldo) if sueldo is not None else 0.0
        self.tipo_vinculo = tipo_vinculo if tipo_vinculo in TIPOS_VINCULO else TIPOS_VINCULO[0]
        self.activo = bool(activo)

    def __repr__(self) -> str:
        return f"<Empleado Legajo={self.legajo} Nombre='{self.obtener_nombre_completo()}' Activo={self.activo}>"