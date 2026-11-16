"""
===============================================================================
NÚCLEO DE DOMINIO: ENTIDAD PERSONA (src/dominio/entidades_persona.py)
===============================================================================
Define la entidad base 'Persona' y sus funciones de saneamiento de datos.
Al ser un concepto transversal, es reutilizado por RRHH, Proveedores y Clientes.
===============================================================================
"""

from typing import Optional


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
        self.tipo_persona = "Fisica"  # Restricción estándar para base de datos