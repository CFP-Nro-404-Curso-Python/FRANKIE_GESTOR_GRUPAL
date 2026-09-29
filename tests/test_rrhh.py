import sys
import os

# ==============================================================================
# ⚠️ MODIFICACIÓN DAVID: FIX DE RUTAS (sys.path)
# ==============================================================================
# Al ejecutar este script suelto desde la carpeta /tests, Python no sabe 
# que existe la carpeta /src. Calculamos la ruta absoluta hacia /src y se la 
# inyectamos al sistema ANTES de hacer los imports de nuestros módulos.
# ==============================================================================
ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ruta_src not in sys.path:
    sys.path.insert(0, ruta_src)

from infraestructura.conexion import ConexionDB
from dominio.entidades_rrhh import Empleado
from infraestructura.repo_rrhh import RepositorioRRHH


def inicializar_bd():
    """
    Carga el archivo db/esquema.sql en la base de datos local si las tablas no existen.
    """
    
    # Como este script se puede correr desde la raíz o desde /tests,
    # calculamos la ruta a la BD dinámicamente para que no falle.
    ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ruta_esquema = os.path.join(ruta_raiz, "db", "esquema.sql")
    
    if os.path.exists(ruta_esquema):
        with open(ruta_esquema, "r", encoding="utf-8") as f:
            sql_script = f.read()

        with ConexionDB() as conn:
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            print(
                " Base de datos e inicialización de tablas verificada con éxito.")
    else:
        print(f" No se encontró el archivo de esquema en: {ruta_esquema}")


# 1. Asegurar que las tablas existan en frankie.db
inicializar_bd()

# 2. Probar la creación del empleado
empleado_prueba = Empleado(
    nro_documento="20-35999888-9",
    nombres="Carlos",
    apellidos="Gómez",
    email="carlos.gomez@frankie.com",
    telefono="223-5551234",
    legajo="EMP-001",
    cargo="Vendedor",
    sector="Ventas",
    sueldo=650000.0
)

print("\n--- Guardando empleado de prueba ---")
resultado = RepositorioRRHH.crear_empleado(empleado_prueba)

if resultado:
    print(" ¡Éxito! El empleado y la persona se insertaron de forma atómica.")
else:
    print(" Falla en la inserción.")

print("\n--- Consultando lista de empleados desde la BD ---")
empleados = RepositorioRRHH.listar_empleados()
for emp in empleados:
    print(
        f"ID Empleado: {emp.id_empleado} | Legajo: {emp.legajo} | Nombre: {emp.obtener_nombre_completo()} | Documento: {emp.nro_documento}")