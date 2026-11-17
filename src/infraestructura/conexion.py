"""
Módulo de Infraestructura: Conexión Centralizada a SQLite
Gestiona la apertura transaccional, activación de claves foráneas y cierre seguro de la base de datos.
"""
import sqlite3
from pathlib import Path


class ConexionDB:
    """
    Patrón Singleton que conecta con la base de datos centralizada en 'db/frankie_gestor.db'.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConexionDB, cls).__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self):
        # Ruta fija hacia 'db/frankie_gestor.db' asegurando que coincida con el inicializador
        ruta_base = Path(__file__).resolve().parent.parent.parent
        ruta_db_dir = ruta_base / 'db'
        ruta_db_dir.mkdir(parents=True, exist_ok=True)
        ruta_db = ruta_db_dir / 'frankie_gestor.db'

        self.conexion = sqlite3.connect(str(ruta_db), check_same_thread=False)
        self.conexion.execute("PRAGMA foreign_keys = ON;")
        self.conexion.row_factory = sqlite3.Row

    def __enter__(self):
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self.conexion.rollback()
            except Exception:
                pass
        else:
            try:
                self.conexion.commit()
            except Exception:
                pass