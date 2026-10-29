import sys
import os
from pathlib import Path

# Inyectamos la ruta 'src' para que Pytest encuentre nuestros módulos sin tirar error
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from infraestructura.conexion import ConexionDB
from dominio.entidades_core import Usuario, Rol
from infraestructura.repo_core import RepoCore
from controladores.orquestador_core import OrquestadorCore

# =====================================================================
# 1. TEST DE INFRAESTRUCTURA (Patrón Singleton)
# =====================================================================
def test_singleton_conexion():
    """Verifica que el patrón Singleton funcione y no abra múltiples conexiones."""
    db1 = ConexionDB()
    db2 = ConexionDB()
    # 'is' evalúa si ambas variables apuntan exactamente al mismo espacio en memoria
    assert db1 is db2

# =====================================================================
# 2. TEST DE DOMINIO (Entidades Core)
# =====================================================================
def test_creacion_usuario_y_rol():
    """Verifica que los 'moldes' de memoria se instancien correctamente."""
    # Creamos un usuario y un rol de prueba en memoria
    usuario = Usuario(id_usuario=99, username="test_user", password_hash="hashfalso123")
    rol = Rol(id_rol=1, nombre="Gerente")
    
    # Probamos el método de la entidad
    usuario.agregar_rol(rol)
    
    # Validaciones (asserts)
    assert usuario.username == "test_user"
    assert len(usuario.roles) == 1
    assert usuario.roles[0].nombre == "Gerente"

# =====================================================================
# 3. TEST DE REPOSITORIO Y SEGURIDAD (Base de Datos)
# =====================================================================
def test_hashing_password():
    """Verifica que el algoritmo SHA-256 esté devolviendo 64 caracteres."""
    repo = RepoCore()
    hash_result = repo._hashear_password("admin123")
    assert len(hash_result) == 64
    assert type(hash_result) is str

def test_autenticacion_exitosa():
    """
    Prueba contra la base de datos real. 
    Verifica que 'admin' y 'admin123' (semilla de esquema.sql) devuelvan la Entidad completa.
    """
    repo = RepoCore()
    usuario = repo.autenticar_usuario("admin", "admin123")
    
    assert usuario is not None
    assert usuario.username == "admin"
    # Verificamos que traiga los roles desde la tabla intermedia
    roles_nombres = [r.nombre for r in usuario.roles]
    assert "Administrador" in roles_nombres

def test_autenticacion_fallida():
    """Verifica que el sistema rechace credenciales incorrectas."""
    repo = RepoCore()
    usuario = repo.autenticar_usuario("admin", "clave_equivocada")
    assert usuario is None

# =====================================================================
# 4. TEST DE ORQUESTADOR (Backup en caliente)
# =====================================================================
def test_ejecucion_backup():
    """Verifica que el controlador pueda clonar la base de datos sin crashear."""
    orquestador = OrquestadorCore()
    resultado = orquestador.ejecutar_backup()
    
    # El string devuelto debe contener la palabra 'exitoso'
    assert "exitoso" in resultado.lower()
    
    # Verificamos físicamente que la carpeta backups se haya creado
    ruta_base = Path(__file__).resolve().parent.parent
    carpeta_backups = ruta_base / 'db' / 'backups'
    assert carpeta_backups.exists()