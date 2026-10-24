"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: CONEXIÓN A LA BASE DE DATOS (infraestructura/conexion.py)
===============================================================================
Patrón Singleton: Garantiza que toda la aplicación use una única conexión a la base de datos,
evitando el error 'database is locked' y gestionando automáticamente transacciones.
===============================================================================
"""

import sqlite3
import os
from pathlib import Path


class ConexionDB:
    """
    Patrón Singleton con soporte de Administrador de Contexto (__enter__ / __exit__).
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(ConexionDB, cls).__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self):
        # Resolver ruta segura al archivo de base de datos dentro de la carpeta 'db'
        ruta_base = Path(__file__).resolve().parent.parent.parent
        ruta_db = ruta_base / 'db' / 'frankie_gestor.db'

        # Asegurar que la carpeta 'db' exista físicamente
        ruta_db.parent.mkdir(parents=True, exist_ok=True)

        # Conexión persistente compatible con múltiples hilos de Tkinter
        self.conexion = sqlite3.connect(str(ruta_db), check_same_thread=False)
        self.conexion.execute("PRAGMA foreign_keys = ON;")
        self.conexion.row_factory = sqlite3.Row

    def __enter__(self):
        # Asegurar que la conexión exista ante cualquier llamado de contexto
        if not hasattr(self, 'conexion') or self.conexion is None:
            self._inicializar_conexion()
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
        # Nota: No se cierra la conexión para mantener vivo el Singleton global.