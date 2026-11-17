"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES CORE (src/dominio/entidades_core.py)
===============================================================================
Define las clases base para la autenticación y control de acceso del sistema Frankie.
===============================================================================
"""


class Rol:
    """
    Molde (Entidad) que representa los niveles de acceso del sistema.
    Ejemplo: Administrador, Gerente, Empleado.
    """

    def __init__(self, id_rol: int, nombre: str, descripcion: str = ""):
        self.id_rol = id_rol
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return f"<Rol id={self.id_rol} nombre='{self.nombre}'>"


class Usuario:
    """
    Molde (Entidad) que representa a quien inicia sesión en el sistema.
    Nota: 'password_hash' almacena el texto cifrado, no la clave real.
    """

    def __init__(self, id_usuario: int, username: str, password_hash: str, activo: int = 1):
        self.id_usuario = id_usuario
        self.username = username
        self.password_hash = password_hash
        self.activo = activo

        # Un usuario puede tener varios roles asociados.
        self.roles = []

    def agregar_rol(self, rol: Rol):
        """Método simple para añadir un objeto Rol a la lista del usuario."""
        self.roles.append(rol)

    def __repr__(self):
        return f"<Usuario username='{self.username}'>"