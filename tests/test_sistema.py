import sys
import os

# Fix de rutas para ejecutar desde la carpeta tests/
ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ruta_src not in sys.path:
    sys.path.insert(0, ruta_src)

from infraestructura.conexion import ConexionDB
from infraestructura.repo_core import RepoCore
from infraestructura.repo_rrhh import RepositorioRRHH
from dominio.entidades_rrhh import Empleado



def ejecutar_test_global():
    print("==================================================")
    print(" INICIANDO TEST DE INTEGRACIÓN GLOBAL (M1 + M2)   ")
    print("==================================================\n")

    # 1. INICIALIZACIÓN DE BASE DE DATOS Y SINGLETON.
    print("[1] Verificando Inicialización y Semillas (esquema.sql)...")
    ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ruta_esquema = os.path.join(ruta_raiz, "db", "esquema.sql")
    
    if not os.path.exists(ruta_esquema):
        print(f" ERROR: No se encontró el esquema en {ruta_esquema}")
        return

    with open(ruta_esquema, "r", encoding="utf-8") as f:
        sql_script = f.read()

    with ConexionDB() as conn:
        cursor = conn.cursor()
        cursor.executescript(sql_script)
    print(" OK: Base de datos construida y operativa.\n")


    # 2. PRUEBA MÓDULO 1: CORE (Autenticación SHA-256).
    print("[2] Probando Módulo 1 (Core - Autenticación)...")
    repo_core = RepoCore()
    
    usuario_mal = repo_core.autenticar_usuario("admin", "clave_falsa")
    if not usuario_mal:
        print(" OK: Bloqueo de credenciales inválidas funciona correctamente.")
    else:
        print(" ERROR: El sistema permitió el ingreso con una clave falsa.")
        return

    usuario_bien = repo_core.autenticar_usuario("admin", "admin123")
    if usuario_bien and usuario_bien.roles[0].nombre == "Administrador":
        print(f" OK: Autenticación exitosa. Usuario '{usuario_bien.username}' cargado con rol '{usuario_bien.roles[0].nombre}'.\n")
    else:
        print(" ERROR: Falló la autenticación con credenciales válidas o no cargó los roles.")
        return


    # 3. PRUEBA MÓDULO 2: RRHH (Persistencia Transaccional).
    print("[3] Probando Módulo 2 (RRHH - Persistencia Atómica)...")
    cuit_test = "20998887776"
    
    # Limpiamos al usuario de prueba si ya existe (para que el test sea repetible).
    with ConexionDB() as db:
        db.cursor().execute("DELETE FROM personas WHERE nro_documento = ?", (cuit_test,))

    empleado_nuevo = Empleado(
        nro_documento=cuit_test,
        nombres="Marta",
        apellidos="Sánchez",
        legajo="EMP-999",
        cargo="Gerente",
        sector="Gestión",
        sueldo=1250000.0,
        email="marta@frankie.com"
    )

    resultado = RepositorioRRHH.crear_empleado(empleado_nuevo)
    if resultado:
        print(" OK: Empleado guardado correctamente (Personas + Empleados).")
    else:
        print(" ERROR: Falló la inserción del empleado.")
        return

    # Verificamos la lectura.
    lista = RepositorioRRHH.listar_empleados(criterio_busqueda="Marta")
    if lista and lista[0].nro_documento == cuit_test:
        print(f" OK: Lectura correcta. Empleado recuperado: {lista[0].obtener_nombre_completo()}")
    else:
        print(" ERROR: No se pudo recuperar al empleado de la base de datos.")
        return

    print("\n==================================================")
    print(" TEST FINALIZADO CON ÉXITO. EL SISTEMA ES ESTABLE.")
    print("==================================================")

if __name__ == "__main__":
    ejecutar_test_global()