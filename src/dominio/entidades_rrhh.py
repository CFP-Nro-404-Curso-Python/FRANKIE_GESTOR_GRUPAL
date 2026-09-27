"""
Módulo de Dominio: Entidades de Recursos Humanos
Define las clases Persona (superclase) y Empleado (subclase) alineadas al esquema oficial de Frankie.
"""


def limpiar_documento(doc: str) -> str:
    """
    Elimina guiones, puntos y espacios, dejando únicamente los caracteres numéricos.
    """
    if not doc:
        return ""
    return "".join(caracter for caracter in str(doc) if caracter.isdigit())


class Persona:
    """
    Clase base que representa a una persona dentro del sistema.
    Coincide con la estructura de la tabla 'personas'.
    """

    def __init__(self, nro_documento, nombres, apellidos=None,
                 tipo_documento="CUIT",
                 tipo_persona="Fisica", email=None, telefono=None,
                 razon_social=None,
                 domicilio=None, ciudad=None, provincia=None,
                 codigo_postal=None, id=None):
        self.id = id
        self.tipo_persona = tipo_persona
        self.nombres = nombres
        self.apellidos = apellidos
        self.razon_social = razon_social
        self.tipo_documento = tipo_documento
        # Sanitización: Guarda solo los números del CUIT/DNI
        self.nro_documento = limpiar_documento(nro_documento)
        self.telefono = telefono
        self.email = email
        self.domicilio = domicilio
        self.ciudad = ciudad
        self.provincia = provincia
        self.codigo_postal = codigo_postal

    def obtener_nombre_completo(self):
        """Retorna el nombre completo o la razón social."""
        if self.tipo_persona == "Fisica" and self.apellidos:
            return f"{self.apellidos}, {self.nombres}"
        return self.razon_social or self.nombres


class Empleado(Persona):
    """
    Clase derivada que representa a un empleado de la empresa.
    Hereda de Persona y suma atributos laborales según la BD.
    """

    def __init__(self, nro_documento, nombres, legajo, cargo, sector, sueldo,
                 apellidos=None, id_usuario=None, tipo_documento="CUIT",
                 email=None,
                 telefono=None, domicilio=None, ciudad=None, provincia=None,
                 codigo_postal=None, id_empleado=None, id_persona=None):
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
            id=id_persona
        )

        self.id_empleado = id_empleado
        self.id_usuario = id_usuario
        self.legajo = legajo
        self.cargo = cargo
        self.sector = sector
        self.sueldo = sueldo

    def __repr__(self):
        return f"<Empleado Legajo={self.legajo} Nombre='{self.obtener_nombre_completo()}'>"