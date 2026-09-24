import sqlite3
import os



class ConexionDB:
    """
    Patrón Singleton: Garantiza que toda la aplicación use una única conexión a la base de datos.
    Esto evita el error 'database is locked' cuando varios módulos intentan acceder al mismo tiempo.
    """
    _instancia = None   # Variable de clase para guardar la única conexión creada.

    def __new__(cls):
        # Si la instancia no existe, la creamos. Si ya existe, devolvemos la que está guardada.
        if cls._instancia is None:
            cls._instancia = super(ConexionDB, cls).__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self):
        # Calculamos la ruta al archivo db subiendo tres niveles desde este script:
        # 1. infraestructura -> 2. src -> 3. directorio raíz, y luego bajamos a la carpeta 'db'.
        ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ruta_db = os.path.join(ruta_base, 'db', 'frankie_gestor.db')
        
        # Conectamos a la base de datos. check_same_thread=False permite que distintas ventanas de Tkinter la usen.
        self.conexion = sqlite3.connect(ruta_db, check_same_thread=False)
        
        # Habilitamos las validaciones de las llaves foráneas (fundamental en SQLite).
        self.conexion.execute("PRAGMA foreign_keys = ON;")
        
        # Configuramos la conexión para poder acceder a las columnas por su nombre (ej: fila['nombre']).
        self.conexion.row_factory = sqlite3.Row

    # __enter__ y __exit__ permiten usar la conexión con la estructura 'with ConexionDB() as conn:'
    # Esto administra automáticamente los guardados (commit) y reversiones (rollback) si hay errores.
    def __enter__(self):
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exc_type captura si ocurrió algún error de Python (excepción).
        if exc_type:
            self.conexion.rollback() # Si hubo un error, descartamos los cambios.
        else:
            self.conexion.commit()   # Si todo salió bien, guardamos los cambios.
        
        # OJO: No cerramos la conexión (self.conexion.close()) porque al ser Singleton queremos mantenerla viva 
        # para los demás módulos del sistema.