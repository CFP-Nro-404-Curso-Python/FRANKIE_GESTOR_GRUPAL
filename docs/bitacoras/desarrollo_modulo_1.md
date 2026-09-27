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
```
## 4. Capa de Dominio: Entidades Core (Semana 2)

**Archivo:** `src/dominio/entidades_core.py`
**Objetivo:** Definir las estructuras de datos puras (Entidades) que representarán a los Usuarios y Roles dentro de la memoria temporal del sistema.

### 4.1 ¿Qué es una Entidad en nuestro diseño?
En la Capa de Dominio, las Entidades funcionan como "moldes". La clase `Usuario` no es un registro directo de la base de datos ni un elemento visual de la pantalla; es la definición estricta de qué estructura debe tener un usuario. Cuando el sistema recupera datos mediante SQL, instancia este "molde" a través del método `__init__` y lo pasa a las demás capas como un objeto ordenado.

### 4.2 Especificaciones Técnicas Implementadas
*   **Type Hinting (Pistas de tipado):** Se aplicó el uso de anotaciones (ej. `id_usuario: int`, `username: str`). Aunque en Python no son restrictivas a nivel de compilación, sirven como documentación viva. Le avisan al entorno de desarrollo y a los demás programadores qué tipo de dato específico se espera, reduciendo drásticamente los errores de tipeo.
*   **Mapeo de Relaciones (Muchos a Muchos):** Para representar en memoria la tabla intermedia `usuarios_roles`, la entidad `Usuario` inicializa el atributo `self.roles` como una lista vacía (`[]`). Posteriormente, el controlador correspondiente buscará los roles asignados y los inyectará usando el método `agregar_rol()`.

### 4.3 Directiva Arquitectónica para el Equipo (Regla de Aislamiento)
Para los desarrolladores (Alicia y Uriel) encargados de replicar esta lógica en sus respectivos módulos (`entidades_rrhh.py`, `entidades_ventas.py`, `entidades_stock.py`), es obligatorio cumplir con la **Regla de Aislamiento Total**:

1.  **Cero Dependencias:** Los archivos dentro de la carpeta `dominio` son islas de lógica. Solo admiten Python puro.
2.  **Prohibición de Imports de Infraestructura/UI:** Queda terminantemente prohibido utilizar sentencias como `import sqlite3`, `import tkinter` o librerías de terceros en esta capa. 
3.  **Separación de Responsabilidades:** Toda lógica relacionada a guardar en la base de datos o dibujar botones en la pantalla corresponde a los repositorios y a las vistas, respectivamente. El dominio es ignorante de cómo se guarda o cómo se muestra la información.

## 5. Capa de Infraestructura: Repositorio Core (Semana 2)

**Archivo:** `src/infraestructura/repo_core.py`
**Objetivo:** Centralizar las consultas a la base de datos para la autenticación, transformando registros crudos en Entidades limpias.

### 5.1 ¿Qué es y cómo funciona el Repositorio?
El Repositorio actúa como un traductor entre SQLite y nuestro sistema. La base de datos responde con registros puros (filas y columnas), pero nuestra aplicación en Python trabaja con objetos. El trabajo del Repositorio es ir a la base, buscar la información cruda, y empaquetarla dentro del "molde" (Entidad) que creamos en el paso anterior.

*Ejemplo:* Imaginate pedir un mueble. La base de datos te entrega una caja con maderas y tornillos. El Repositorio es el operario que lee el manual, ensambla la silla (la Entidad) y se la entrega armada a la interfaz gráfica.

### 5.2 Especificaciones Técnicas Implementadas
*   **Hashing de Contraseñas (SHA-256):** Es un mecanismo de seguridad unidireccional. Pasa la contraseña por una función criptográfica que devuelve un código extenso e irrecuperable (no se puede desencriptar). Para validar un login, el sistema aplica este algoritmo a lo que tipea el usuario y lo compara con el código seguro almacenado en la base de datos.
*   **Prevención de Inyección SQL (`?`):** Para evitar que un usuario malicioso ingrese comandos SQL en el formulario y manipule la base de datos, las consultas se parametrizan. El motor de SQLite sanitiza automáticamente cualquier variable que se pase a través del símbolo `?`.

### 5.3 Directivas Estrictas para el Equipo (Módulos 2, 3 y 4)
Al momento de crear sus propios repositorios (`repo_rrhh.py`, `repo_ventas.py`, `repo_stock.py`), Uriel y Alicia deben acatar estas tres reglas innegociables:

1.  **Regla de Retorno (Cero datos crudos):** Los métodos del repositorio jamás deben devolver diccionarios, tuplas o listas sueltas. Toda función (ej. `buscar_cliente()`) debe instanciar y retornar su Entidad correspondiente (ej. un objeto `Cliente`).
2.  **Parametrización Obligatoria:** Queda estrictamente prohibido usar `f-strings` o concatenación con `+` para inyectar variables en las sentencias SQL. Deben usar siempre tuplas y el símbolo `?` para prevenir vulnerabilidades de seguridad.
3.  **Cero Interfaz Gráfica:** El Repositorio ignora por completo a Tkinter. Si ocurre un error (ej. "proveedor no existe"), el repositorio no hace `print()` ni lanza ventanas emergentes. Simplemente devuelve `None` o levanta un error técnico (ej. `raise ValueError`), delegando a la capa visual la responsabilidad de mostrar el aviso al usuario.

## 6. Capa de Vistas: Interfaz de Autenticación (Semana 2)

**Archivo:** `src/vistas/ui_login.py`
**Objetivo:** Renderizar la pantalla de ingreso al sistema y gestionar las reglas de seguridad visuales (bloqueo tras 3 intentos fallidos).

### 6.1 El Rol de la Vista en Clean Architecture
La Vista es la interfaz gráfica (construida con Tkinter) y su única responsabilidad es interactuar con el usuario: dibuja ventanas, botones, y escucha eventos (clicks, tipeos). Las Vistas son "tontas" por diseño; no toman decisiones de negocio ni saben de dónde vienen o cómo se almacenan los datos.

*Ejemplo Práctico:* La Vista funciona como el recepcionista de un edificio cerrado. Cuando llegás, te pide tu DNI. El recepcionista no tiene la lista de inquilinos; llama por teléfono al guardia de seguridad (el Repositorio/Controlador) y le pregunta. Si el guardia dice "dejalo pasar", te abre la puerta. Si dice que no, te avisa que el ingreso está denegado.

### 6.2 Especificaciones Técnicas Implementadas
*   **Enmascaramiento de Seguridad (`show="*"`):** El componente `tk.Entry` destinado a la contraseña se configuró para ocultar los caracteres tipeados detrás de asteriscos, una medida básica pero vital para evitar la exposición de credenciales.
*   **Estado Persistente en Memoria (`self.intentos_fallidos`):** Se utilizó una variable de instancia (usando `self`) para llevar el conteo de errores. Como la ventana queda abierta esperando interacción, esta variable mantiene vivo el conteo en la memoria RAM hasta llegar al límite, momento en el que se ejecuta `config(state=tk.DISABLED)` para apagar el botón.
*   **Asignación de Eventos (`command`):** La acción del botón se vinculó mediante `command=self.procesar_login` (sin paréntesis). Esto es crucial en Tkinter: le indica al motor gráfico que guarde la referencia a la función y la ejecute únicamente al hacer click, en lugar de ejecutarla automáticamente al abrir el programa.

### 6.3 Directivas Arquitectónicas para el Equipo (UI)
Tkinter es propenso a generar "código espagueti" si no se estructura correctamente. Al desarrollar pantallas como `ui_empleados.py` o `ui_inventario.py`, Alicia y Uriel deben acatar estas tres reglas de hierro:

1.  **Regla de Ignorancia (Cero Base de Datos):** Queda terminantemente prohibido hacer un `import sqlite3` o ejecutar consultas SQL (ej. `SELECT`) en la carpeta `vistas`. La Vista no sabe cómo se guardan los datos, solo los pide a las capas inferiores y los dibuja.
2.  **Diseño Orientado a Objetos (Clases obligatorias):** No se debe escribir código Tkinter suelto en el archivo. Toda pantalla nueva debe estar encapsulada en una Clase (`class VentanaInventario:`). Esto aísla el entorno y evita que las variables de una ventana choquen con las de otra.
3.  **Separar Dibujo de Lógica:** Las clases visuales deben tener un método dedicado exclusivamente a colocar botones y etiquetas (ej. `_dibujar_interfaz()`), y métodos completamente separados para ejecutar acciones (ej. `guardar_cliente()`). Mezclar la creación del botón con la lógica del guardado en el mismo bloque hace que el código sea inmantenible.

---
*(Los siguientes apartados se irán completando a medida que desarrollemos cada componente de la Infraestructura y el Módulo 1).*