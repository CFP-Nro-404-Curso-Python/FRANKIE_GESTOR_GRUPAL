"""
===============================================================================
SCRIPT INTELIGENTE DE INICIALIZACIÓN DE BASE DE DATOS
===============================================================================
"""

import sqlite3
from pathlib import Path


def encontrar_raiz_proyecto():
    # Busca la raíz subiendo de nivel hasta encontrar la carpeta 'db' o el archivo 'esquema.sql'
    actual = Path(__file__).resolve().parent
    for parent in [actual, actual.parent, actual.parent.parent]:
        if (parent / "db").exists() or (parent / "esquema.sql").exists():
            return parent
    return actual


def inicializar_base_datos():
    raiz = encontrar_raiz_proyecto()

    # Definir rutas exactas basadas en la raíz detectada
    ruta_db = raiz / "db" / "frankie_gestor.db"
    ruta_db.parent.mkdir(parents=True, exist_ok=True)

    ruta_esquema = raiz / "db" / "esquema.sql"
    if not ruta_esquema.exists():
        ruta_esquema = raiz / "esquema.sql"

    print(f"[INFO] Ruta raíz detectada con éxito: {raiz}")
    print(f"[INFO] Conectando a la base de datos en: {ruta_db}")
    print(f"[INFO] Buscando esquema en: {ruta_esquema}")

    conn = sqlite3.connect(str(ruta_db))
    conn.execute("PRAGMA foreign_keys = ON;")

    if ruta_esquema.exists():
        with open(ruta_esquema, "r", encoding="utf-8") as f:
            script_sql = f.read()

        conn.executescript(script_sql)
        conn.commit()
        print("[EXITO] ¡Todas las tablas del esquema fueron creadas correctamente!")
    else:
        print("[ERROR CRITICO] No se encontró el archivo 'esquema.sql'.")

    # Verificación final
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [fila[0] for fila in cursor.fetchall()]
    print(f"[VERIFICACION] Tablas existentes en la BD: {tablas}")

    conn.close()


if __name__ == "__main__":
    inicializar_base_datos()