class Rol:
    """
    Molde (Entidad) que representa los niveles de acceso del sistema.
    Ejemplo: Administrador, Gerente, Empleado.
    """
    def __init__(self, id_rol: int, nombre: str, descripcion: str = ""):
        # self.atributo = valor_recibido.
        self.id_rol = id_rol
        self.nombre = nombre
        self.descripcion = descripcion



class Usuario:
    """
    Molde (Entidad) que representa a quien inicia sesión en el sistema.
    Ojo: 'password' acá almacenará el texto cifrado (hash), no la clave real.
    """
    def __init__(self, id_usuario: int, username: str, password_hash: str, activo: int = 1):
        self.id_usuario = id_usuario
        self.username = username
        self.password_hash = password_hash
        self.activo = activo
        
        # Un usuario puede tener varios roles. Iniciamos con una lista vacía.
        # Más adelante, la base de datos se encargará de llenar esta lista.
        self.roles = []

    def agregar_rol(self, rol: Rol):
        """Método simple para añadir un objeto Rol a la lista del usuario."""
        self.roles.append(rol)



# ==============================================================================================
#  ⚠️ ATENCIÓN ALICIA Y URIEL:
#                                                                     
#  NO deben agregar código en este archivo. Ustedes trabajarán en sus propios
#  archivos (entidades_rrhh.py, entidades_ventas.py, entidades_stock.py).
# 
#  QUÉ DEBEN IMITAR DE ACÁ:
#
#  1. Sus archivos deben tener esta misma estructura: Clases simples con __init__.
#  2. Regla de Oro de la Capa Dominio: NADA de 'import sqlite3' ni 'import tkinter'. 
#     El dominio es Python puro, desconoce por completo la base de datos y la interfaz gráfica.
# ==============================================================================================