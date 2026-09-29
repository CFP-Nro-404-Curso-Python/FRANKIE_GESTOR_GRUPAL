"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE RRHH (entidades_rrhh.py)
===============================================================================
Estrategia y Buenas Prácticas Aplicadas:
1. Listas de Opciones Validadas (Enumerados de Negocio):
   Definición centralizada de SECTORES, TIPOS_VINCULO y CARGOS para poblar
   la UI y asegurar que no ingresen valores fuera de regla.

2. Opciones de Descarte (Fallback Defensivo):
   Si un campo obligatorio llega vacío o inválido, la entidad asigna automáticamente
   un valor por defecto seguro (Administración, Planta, Empleado_Admin).

3. Encapsulamiento de Reglas de Negocio:
   Métodos explícitos en la entidad para evaluar requerimientos tributarios/facturación.
===============================================================================
"""

from typing import Optional

# Listas fijas reutilizables por la UI y el Dominio
TIPOS_VINCULO = ["Propietario", "Contratado", "Pasante", "Planta"]
SECTORES = ["Gestión", "Staff", "Ventas", "Compras", "Administración"]
CARGOS = ["Gerente", "Administrador", "Empleado_Admin", "Empleado_Ventas", "Empleado_Compras"]


def limpiar_documento(doc: str) -> str:
    """ Sanitiza la cadena del documento eliminando guiones y espacios vacíos. """
    if not doc:
        return ""
    return str(doc).replace("-", "").replace(" ", "").strip()


class Persona:
    """ Entidad Base de Dominio para representar a una persona física o jurídica. """

    def __init__(self, id_persona: Optional[int] = None, nro_documento: str = "",
                 nombres: str = "", apellidos: str = "", email: str = "", telefono: str = ""):
        self.id = id_persona
        self.nro_documento = limpiar_documento(nro_documento)
        self.nombres = nombres.strip()
        self.apellidos = apellidos.strip()
        self.email = email.strip()
        self.telefono = telefono.strip()
        self.tipo_persona = "FISICA"  # Exigido por restricción CHECK en BD

    def obtener_nombre_completo(self) -> str:
        """ Devuelve el nombre formateado. Útil para la UI y reportes. """
        if self.apellidos and self.nombres:
            return f"{self.apellidos}, {self.nombres}"
        return self.nombres or "Sin Nombre"


class Empleado(Persona):
    """ Entidad de Dominio que representa a un trabajador dentro de la organización. """

    def __init__(self, id_empleado: Optional[int] = None, id_persona: Optional[int] = None,
                 nro_documento: str = "", nombres: str = "", apellidos: str = "",
                 legajo: str = "", cargo: str = "Empleado_Admin", sector: str = "Administración",
                 tipo_vinculo: str = "Planta", sueldo: float = 0.0,
                 email: str = "", telefono: str = "", id_usuario: int = 1):

        super().__init__(id_persona=id_persona, nro_documento=nro_documento,
                         nombres=nombres, apellidos=apellidos, email=email, telefono=telefono)

        self.id_empleado = id_empleado
        self.legajo = legajo.strip()

        # Validaciones defensivas contra las listas de opciones (Valores por descarte/fallback)
        self.cargo = cargo if cargo in CARGOS else "Empleado_Admin"
        self.sector = sector if sector in SECTORES else "Administración"
        self.tipo_vinculo = tipo_vinculo if tipo_vinculo in TIPOS_VINCULO else "Planta"

        self.sueldo = float(sueldo) if sueldo else 0.0
        self.id_usuario = id_usuario
        self.activo = True

    @property
    def requiere_factura(self) -> bool:
        """ Regla de Negocio: Personal contratado debe presentar factura por locación. """
        return self.tipo_vinculo == "Contratado"

    @property
    def requiere_comprobante_afip(self) -> bool:
        """ Regla de Negocio: Monotributistas/Contratados requieren comprobante de pago AFIP/ARCA. """
        return self.tipo_vinculo in ["Contratado", "Propietario"]