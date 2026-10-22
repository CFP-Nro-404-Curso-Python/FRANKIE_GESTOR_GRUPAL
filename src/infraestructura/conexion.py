import sqlite3
import os



class ConexionDB:
    """
    Patrón Singleton: Garantiza que toda la aplicación use una única conexión a la base de datos.
    Esto evita el error 'database is locked' cuando varios módulos intentan acceder al mismo tiempo.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConexionDB, cls).__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self):
        ruta_base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ruta_db = os.path.join(ruta_base, 'db', 'frankie_gestor.db')

        # AGREGADO: Ruta al archivo SQL que tiene las tablas y datos semilla.
        ruta_esquema = os.path.join(ruta_base, 'db', 'esquema.sql')
        
        self.conexion = sqlite3.connect(ruta_db, check_same_thread=False)
        self.conexion.execute("PRAGMA foreign_keys = ON;")
        self.conexion.row_factory = sqlite3.Row

        # AGREGADO: Validamos si la BD está vacía apenas nos conectamos.
        self._verificar_e_inicializar_esquema(ruta_esquema)

    def _verificar_e_inicializar_esquema(self, ruta_esquema):
        """
        Lee la estructura de SQLite. Si no hay tablas, ejecuta el esquema.sql.
        Esto garantiza que la base de datos se autoconstruya en la primera ejecución.
        """
        cursor = self.conexion.cursor()

        # Consultamos la tabla maestra de SQLite para ver si existe alguna tabla creada.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        # Si la lista de tablas está vacía, significa que el archivo db es nuevo.
        if not tablas:
            if os.path.exists(ruta_esquema):
                with open(ruta_esquema, 'r', encoding='utf-8') as archivo_sql:
                    script = archivo_sql.read()

                    # executescript permite correr múltiples sentencias SQL de una sola vez.
                    cursor.executescript(script)
                    self.conexion.commit()
            else:
                raise FileNotFoundError(f"Falta el archivo base para construir la BD: {ruta_esquema}")

    def __enter__(self):
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conexion.rollback()
        else:
            self.conexion.commit()