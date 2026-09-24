# Bitácora de Desarrollo - Módulo 1 (Core y Seguridad) & Infraestructura Base

**Proyecto:** Sistema de Gestión Comercial "Frankie"
**Responsable:** David
**Arquitectura:** Clean Architecture (Arquitectura Limpia)
**Tecnologías:** Python 3, SQLite3, Tkinter

## 1. Introducción y Alcance

Este documento detalla el paso a paso del desarrollo correspondiente a las responsabilidades de infraestructura general y del Módulo 1. El objetivo de este módulo es sentar las bases operativas y de seguridad del sistema para que los Módulos 2 (RRHH), 3 (Ventas) y 4 (Inventario) puedan desarrollarse de forma paralela y autónoma.

Nuestro alcance estricto abarca:
1. **Infraestructura Base:** Diseño del esquema relacional DDL (`esquema.sql`) y el gestor de conexión Singleton para SQLite.
2. **Seguridad (Módulo 1):** Gestión de Entidades `Usuario` y `Rol`, cifrado de contraseñas (SHA-256) y bloqueo por intentos fallidos (`ui_login.py`).
3. **Orquestación (Módulo 1):** Desarrollo del Panel Principal (`ui_panel.py`) con Control de Acceso Basado en Roles (RBAC) y ejecución de Backups.


## 2. Flujo de Datos (Regla de Dependencia)

Para mantener el sistema escalable y evitar el acoplamiento (código espagueti), respetamos el flujo de la Arquitectura Limpia aislando las capas:
1. **Vista (Tkinter):** Capa externa. Captura la acción del usuario y delega el trabajo al Controlador. No contiene reglas de negocio ni ejecuta SQL.
2. **Controlador (Orquestador):** Capa intermedia. Recibe órdenes de la Vista, aplica la lógica de negocio y coordina con la Infraestructura para buscar o guardar información.
3. **Infraestructura (Repositorios/Conexión):** Capa externa de persistencia. Ejecuta sentencias SQL mediante la conexión Singleton. Recibe y devuelve Entidades de Dominio.
4. **Dominio (Entidades/Excepciones):** Capa central. Define los objetos del negocio (`Usuario`, `Rol`) y errores personalizados. Es Python puro, no depende de ninguna otra capa.


## 3. Infraestructura: Conexión Centralizada (Semana 1)

**Archivo:** `src/infraestructura/conexion.py`
**Objetivo:** Crear un punto de acceso único a la base de datos SQLite para evitar bloqueos y corrupción de datos durante el desarrollo paralelo.

### 3.1 El Patrón Singleton
Para resolver el problema del acceso concurrente, implementamos el patrón de diseño Singleton (Instancia Única). 

**¿Para qué sirve?**
Garantiza que toda la aplicación comparta una y solo una conexión a la base de datos en todo momento. En SQLite, si múltiples módulos intentan abrir su propia conexión simultáneamente, ocurre el error fatal `database is locked`. El Singleton funciona como un administrador: si le pedís una conexión y no existe, la crea; si ya existe, te presta la que está en uso.

### 3.2 Reglas de Uso para el Equipo (¡Importante!)
Para que el sistema no colapse, todos los repositorios (`repo_rrhh.py`, `repo_ventas.py`, etc.) deben respetar estas dos directivas:

1. **Gestor de Contexto (`with`):** Toda consulta a la base de datos debe hacerse usando la estructura `with`. Esto automatiza el guardado de datos (commit) y revierte los cambios si ocurre un error (rollback), manteniendo la base segura.
2. **Prohibido Cerrar:** Jamás utilicen `conexion.close()`. Como la conexión es compartida (Singleton), cerrarla provocaría la caída de los módulos de sus compañeros.

### 3.3 Ejemplo Práctico de Implementación
Así es como deben utilizar la conexión dentro de sus repositorios de infraestructura:

```python
from infraestructura.conexion import ConexionDB

def obtener_usuarios_activos():
    # El bloque 'with' asegura el inicio de la transacción y el manejo de errores.
    with ConexionDB() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE activo = 1")
        usuarios = cursor.fetchall()
        
        for u in usuarios:
            # La configuración 'sqlite3.Row' nos permite llamar a las columnas por su nombre.
            print(u['username']) 

    # Al salir de la indentación del 'with', se ejecuta el commit automáticamente.
    # No es necesario cerrar la conexión (db.close()).

---
*(Los siguientes apartados se irán completando a medida que desarrollemos cada componente de la Infraestructura y el Módulo 1).*