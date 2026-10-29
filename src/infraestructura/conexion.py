"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: CONEXIÓN A BASE DE DATOS (infraestructura/conexion.py)
===============================================================================
"""

import sqlite3

class ConexionDB:
    """ Maneja la conexión con la base de datos SQLite del sistema. """
    def __init__(self, db_path: str = "frankie_gestor.db"):
        self.db_path = db_path

    def obtener_conexion(self):
        conexion = sqlite3.connect(self.db_path)
        conexion.row_factory = sqlite3.Row
        return conexion
        