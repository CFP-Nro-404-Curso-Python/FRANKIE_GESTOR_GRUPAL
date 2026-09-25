# hashlib sirve para convertir la contraseña a un hash seguro (SHA-256) y no guardarla en texto plano.
import hashlib
from infraestructura.conexion import ConexionDB
from dominio.entidades_core import Usuario, Rol



class RepoCore:
    """
    Repositorio del Módulo Core (Seguridad).
    Se encarga de hablar con SQLite y devolver objetos (Entidades), no registros crudos.
    """

    def _hashear_password(self, password_plana: str) -> str:
        """
        Convierte la contraseña a un formato seguro irrecuperable (SHA-256).
        Nota: La semilla del 'admin' en esquema.sql está en texto plano ('admin123').
        Para que esto funcione en producción, la base debe guardar este hash, no la clave real.
        """
        # Codificamos el texto a bytes y aplicamos el algoritmo criptográfico SHA-256.
        return hashlib.sha256(password_plana.encode('utf-8')).hexdigest()

    def autenticar_usuario(self, username: str, password_plana: str):
        """
        Verifica si el usuario existe y si la clave coincide.
        Devuelve un objeto Usuario con sus Roles cargados. Si falla, devuelve None.
        """
        hash_ingresado = self._hashear_password(password_plana)

        # Usamos el Singleton de conexion.py. 
        # 'with' maneja la apertura y cierre transaccional automáticamente.
        with ConexionDB() as db:
            cursor = db.cursor()
            
            # 1. Buscamos al usuario por su username (evitamos Inyección SQL usando '?').
            cursor.execute("SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,))
            fila_usuario = cursor.fetchone()

            # Si no hay usuario, o la clave hasheada no es la que está en la base, rebotamos.
            if not fila_usuario or fila_usuario['password'] != hash_ingresado:
                return None

            # 2. Si pasó la validación, instanciamos el "molde" (Entidad).
            usuario = Usuario(
                id_usuario=fila_usuario['id'],
                username=fila_usuario['username'],
                password_hash=fila_usuario['password'],
                activo=fila_usuario['activo']
            )

            # 3. Buscamos los roles asociados en la tabla intermedia (usuarios_roles).
            cursor.execute("""
                SELECT r.id, r.nombre, r.descripcion 
                FROM roles r
                JOIN usuarios_roles ur ON r.id = ur.id_rol
                WHERE ur.id_usuario = ?
            """, (usuario.id_usuario,))
            
            filas_roles = cursor.fetchall()
            
            # Instanciamos cada Rol y se lo agregamos a la lista del Usuario.
            for fila in filas_roles:
                rol = Rol(id_rol=fila['id'], nombre=fila['nombre'], descripcion=fila['descripcion'])
                usuario.agregar_rol(rol)

            # Devolvemos la Entidad pura, lista para usar en la interfaz.
            return usuario



# ===================================================================================================
#  ⚠️ ATENCIÓN ALICIA Y URIEL (CÓMO DEBEN ARMAR SUS REPOSITORIOS):
# ===================================================================================================
#
#  Cuando creen repo_rrhh.py, repo_ventas.py y repo_stock.py, sigan esta estructura:
# 
#  1. IMPORTAR: Traigan 'ConexionDB' y las Entidades de su propio módulo (Persona, Cliente, etc).
#  2. CLASES REPOSITORIO: Agrupen sus funciones CRUD (Crear, Leer, Actualizar, Borrar) en una clase.
#  3. CONSULTAS SEGURAS (SQL Injection):
#     - NUNCA concatenen variables así: f"SELECT * FROM clientes WHERE nombre = '{nombre}'"
#     - SIEMPRE usen tuplas y el símbolo de interrogación: 
#       cursor.execute("SELECT * FROM clientes WHERE nombre = ?", (nombre,))
#  4. RETORNO: Sus métodos no deben devolver diccionarios ni listas crudas. Deben instanciar
#     sus Entidades y devolver los objetos listos (como hicimos acá con Usuario y Rol).
#  5. CERO INTERFAZ: Un repositorio interactúa con SQLite y Python puro. Si algo falla 
#     (ej. proveedor no encontrado), levanten un error (raise ValueError("...")) para que 
#     el controlador o la interfaz gráfica se encargue de mostrar el cartelito al usuario.
# ===================================================================================================