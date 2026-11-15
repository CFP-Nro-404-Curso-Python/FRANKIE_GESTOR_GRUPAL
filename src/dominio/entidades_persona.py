"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE PERSONA (dominio/entidades_persona.py)
===============================================================================
Estrategia y Buenas Prácticas Aplicadas:
1. Regla de Oro del Dominio: Ausencia total de librerías de base de datos (sqlite3)
   o de interfaz gráfica (tkinter). Es código Python puro y agnóstico.
2. Núcleo Compartido (Shared Kernel): Define la entidad base 'Persona' que será
   heredada o utilizada por Empleados, Proveedores y Clientes, unificando los
   datos de identidad, documento y contacto en todo el sistema.
3. Funciones de Sanitización: Incluye validaciones y limpiezas de datos base.
===============================================================================
"""

from typing import Optional


def limpiar_documento(doc: str) -> str:
    """
    Función de utilidad pura para sanitizar la cadena del documento fiscal o identidad.
    Elimina guiones y espacios vacíos para estandarizar el formato de almacenamiento.
    """
    if not doc:
        return ""
    return str(doc).replace("-", "").replace(" ", "").strip()


class Persona:
    """
    Entidad Base de Dominio que representa a una persona (física o jurídica)
    dentro del ecosistema de gestión del sistema comercial, sincronizada
    exactamente con la tabla 'personas' del esquema relacional.
    """

    def __init__(
            self,
            id_persona: Optional[int] = None,
            tipo_persona: str = "FISICA",
            nombres: str = "",
            apellidos: str = "",
            razon_social: str = "",
            tipo_documento: str = "DNI",
            nro_documento: str = "",
            telefono: str = "",
            email: str = "",
            domicilio: str = "",
            ciudad: str = "",
            provincia: str = "",
            codigo_postal: str = ""
    ):
        # Identificador único (Clave primaria 'id' en la tabla 'personas')
        self.id_persona = id_persona

        # Clasificación de la persona (FISICA / JURIDICA)
        self.tipo_persona = tipo_persona.strip().upper()

        # Datos de identidad nominal
        self.nombres = nombres.strip()
        self.apellidos = apellidos.strip()
        self.razon_social = razon_social.strip()

        # Documentación fiscal y de identidad
        self.tipo_documento = tipo_documento.strip().upper()
        self.nro_documento = limpiar_documento(nro_documento)

        # Datos de contacto
        self.telefono = telefono.strip()
        self.email = email.strip()

        # Datos de localización y domicilio
        self.domicilio = domicilio.strip()
        self.ciudad = ciudad.strip()
        self.provincia = provincia.strip()
        self.codigo_postal = codigo_postal.strip()

    def nombre_completo_o_razon(self) -> str:
        """
        Método de dominio útil para la UI: devuelve la razón social si es jurídica,
        o la combinación de apellidos y nombres si es persona física.
        """
        if self.tipo_persona == "JURIDICA" and self.razon_social:
            return self.razon_social

        partes = [p for p in [self.apellidos, self.nombres] if p]
        return ", ".join(partes) if partes else "Sin Identificación"

    def __repr__(self) -> str:
        return (
            f"<Persona(id={self.id_persona}, tipo={self.tipo_persona}, "
            f"nombre='{self.nombre_completo_o_razon()}', doc={self.nro_documento})>"
        )