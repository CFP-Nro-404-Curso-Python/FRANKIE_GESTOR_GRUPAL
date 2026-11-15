"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES CORE (dominio/entidades_core.py)
===============================================================================
"""

class Persona:
    """ Superclase base para las entidades del sistema. """
    def __init__(self, nombre: str, apellido: str, dni: str, **kwargs):
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni