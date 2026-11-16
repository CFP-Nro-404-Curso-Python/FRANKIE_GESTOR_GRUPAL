"""
Script de Inicialización: Carga el esquema oficial (esquema.sql)
en la base de datos SQLite de la carpeta 'db/' de forma automatizada.
"""
from pathlib import Path
import sqlite3


def inicializar_base():
    raiz = Path(__file__).resolve().parent

    # Ruta exacta que utiliza la aplicación (carpeta 'db/frankie_gestor.db')
    ruta_db_dir = raiz / "db"
    ruta_db_dir.mkdir(parents=True, exist_ok=True)
    ruta_db = ruta_db_dir / "frankie_gestor.db"

    # Buscar el archivo esquema.sql en la raíz o dentro de la carpeta db
    ruta_esquema = raiz / "esquema.sql"
    if not ruta_esquema.exists():
        ruta_esquema = raiz / "db" / "esquema.sql"

    print(f"🔄 Conectando y creando tablas en: {ruta_db}")

    if not ruta_esquema.exists():
        print("❌ Error crítico: No se encuentra el archivo 'esquema.sql' en el proyecto.")
        return

    with sqlite3.connect(str(ruta_db)) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON;")

        with open(ruta_esquema, "r", encoding="utf-8") as f:
            script_sql = f.read()

        conexion.executescript(script_sql)

        # 🛡️ ASEGURAR COLUMNA ACTIVO EN PROVEEDORES Y PRODUCTOS
        cursor = conexion.cursor()

        cursor.execute("PRAGMA table_info(proveedores);")
        cols_prov = [col[1] for col in cursor.fetchall()]
        if "activo" not in cols_prov:
            cursor.execute("ALTER TABLE proveedores ADD COLUMN activo INTEGER DEFAULT 1;")
            print("🔧 [Actualización] Se añadió la columna 'activo' a la tabla proveedores.")

        cursor.execute("PRAGMA table_info(productos);")
        cols_prod = [col[1] for col in cursor.fetchall()]
        if "activo" not in cols_prod:
            cursor.execute("ALTER TABLE productos ADD COLUMN activo INTEGER DEFAULT 1;")
            print("🔧 [Actualización] Se añadió la columna 'activo' a la tabla productos.")

        conexion.commit()

    print("✅ ¡Base de datos inicializada y esquema aplicado con éxito en 'db/frankie_gestor.db'!")


if __name__ == "__main__":
    inicializar_base()