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


## 6. Capa de Vistas: Interfaz de Autenticación (Semanas 2 y 3)

**Archivo:** `src/vistas/ui_login.py`
**Objetivo:** Renderizar la pantalla de ingreso al sistema y gestionar las reglas de seguridad visuales (bloqueo tras 3 intentos fallidos), aplicando los estilos globales del proyecto.

### 6.1 El Rol de la Vista en Clean Architecture
La Vista es la interfaz gráfica (construida con Tkinter) y su única responsabilidad es interactuar con el usuario: dibuja ventanas, botones, y escucha eventos (clicks, tipeos). Las Vistas son "tontas" por diseño; no toman decisiones de negocio ni saben de dónde vienen o cómo se almacenan los datos.

*Ejemplo Práctico:* La Vista funciona como el recepcionista de un edificio cerrado. Cuando llegás, te pide tu DNI. El recepcionista no tiene la lista de inquilinos; llama por teléfono al guardia de seguridad (el Repositorio/Controlador) y le pregunta. Si el guardia dice "dejalo pasar", te abre la puerta. Si dice que no, te avisa que el ingreso está denegado.

### 6.2 Especificaciones Técnicas Implementadas
*   **Enmascaramiento de Seguridad (`show="*"`):** El componente `ttk.Entry` destinado a la contraseña se configuró para ocultar los caracteres tipeados detrás de asteriscos, una medida básica pero vital para evitar la exposición de credenciales.
*   **Estado Persistente en Memoria (`self.intentos_fallidos`):** Se utilizó una variable de instancia (usando `self`) para llevar el conteo de errores. Como la ventana queda abierta esperando interacción, esta variable mantiene vivo el conteo en la memoria RAM hasta llegar al límite, momento en el que se ejecuta el bloqueo visual.
*   **Asignación de Eventos (`command`):** La acción del botón se vinculó mediante `command=self.procesar_login` (sin paréntesis)[cite: 19]. Esto le indica al motor gráfico que guarde la referencia a la función y la ejecute únicamente al hacer click, en lugar de ejecutarla automáticamente al abrir el programa.
*   **Integración de Themed Tkinter (`ttk`) [Actualización Sem 3]:** Se reemplazaron los componentes nativos de `tk` por las variantes de `ttk` (`ttk.Label`, `ttk.Entry`, `ttk.Button`) para heredar la paleta de colores y tipografías centralizadas en el archivo `estilos.py`.
*   **Gestión de Estados Avanzados:** Al migrar a `ttk`, el bloqueo temporal del botón de ingreso se actualizó utilizando el método `state(['disabled'])`, reemplazando la configuración legacy de Tkinter.

### 6.3 Directivas Arquitectónicas para el Equipo (UI)
Tkinter es propenso a generar "código espagueti" si no se estructura correctamente. Al desarrollar pantallas como `ui_empleados.py` o `ui_inventario.py`, el equipo debe acatar estas tres reglas de hierro:

1.  **Regla de Ignorancia (Cero Base de Datos):** Queda terminantemente prohibido hacer un `import sqlite3` o ejecutar consultas SQL en la carpeta `vistas`. La Vista no sabe cómo se guardan los datos, solo los pide a las capas inferiores y los dibuja.
2.  **Diseño Orientado a Objetos (Clases obligatorias):** No se debe escribir código Tkinter suelto en el archivo. Toda pantalla nueva debe estar encapsulada en una Clase (ej. `class VentanaInventario:`). Esto aísla el entorno y evita colisiones de variables.
3.  **Separar Dibujo de Lógica:** Las clases visuales deben tener un método dedicado exclusivamente a renderizar componentes (ej. `_dibujar_interfaz()`), y métodos separados para ejecutar acciones (ej. `guardar_cliente()`).


## 7. Capa de Vistas: Panel Principal y Orquestación (Semana 3)

**Archivo:** `src/vistas/ui_panel.py`
**Objetivo:** Actuar como el contenedor principal (chasis) del sistema, proporcionando un menú de navegación lateral (RBAC) y un área de trabajo central dinámica donde se renderizan los módulos de forma independiente.

### 7.1 El Chasis de la Aplicación
El Panel Principal utiliza el gestor de geometría `Grid` para dividir la pantalla en dos sectores inmutables:
*   **Menú Lateral (Columna 0):** Un panel estático y fijo que contiene los botones de acceso a cada módulo.
*   **Área Central (Columna 1):** Un contenedor dinámico configurado con `weight=1` para que absorba todo el espacio disponible al maximizar la ventana. Aquí es donde se "enchufan" las interfaces construidas por el resto del equipo.

### 7.2 Especificaciones Técnicas Implementadas
*   **Limpieza de Memoria en Interfaz (`limpiar_area_central()`):** Antes de cargar una nueva pantalla en el área de trabajo, se itera sobre los widgets existentes (`winfo_children()`) y se los destruye. Esto previene el apilamiento de frames invisibles que colapsarían la memoria RAM.
*   **Inyección de Dependencias Visuales:** Para mantener la Arquitectura Limpia, el panel no conoce el código interno de las vistas de Recursos Humanos o Ventas. Simplemente importa la clase principal del módulo (ej. `InterfazRRHH`) y le pasa como parámetro el contenedor en blanco (`frame_contenido`), indicándole que se dibuje allí adentro.

### 7.3 Directiva de Integración para el Equipo
Para que Uriel y Alicia integren sus respectivos módulos al Panel Principal, el flujo es estricto y sencillo:
1. Importar la clase principal de su vista al inicio de `ui_panel.py`.
2. Crear un método dedicado (ej. `abrir_modulo_ventas()`) que llame a `limpiar_area_central()` y luego instancie su clase pasándole `self.frame_contenido`.
3. Agregar un nuevo `ttk.Button` en el menú lateral que dispare ese método. Queda estrictamente prohibido alterar la geometría base o el sistema de grillas del contenedor general.


## 8. Controlador Central: Punto de Entrada (Semana 3)

**Archivo:** `main.py`
**Objetivo:** Archivo ejecutable raíz del sistema. Orquesta el ciclo de vida de la aplicación, controlando la transición entre la validación de credenciales (Login) y el acceso al sistema (Panel).

### 8.1 El Switchboard de la Aplicación
`main.py` es el único script diseñado para ser ejecutado directamente. Funciona como el orquestador principal: arranca los motores del entorno gráfico, levanta la ventana de autenticación y se queda en pausa. Solo si el usuario supera la validación con la base de datos, destruye el acceso y despliega el Panel Principal.

### 8.2 Especificaciones Técnicas Implementadas
*   **Inyección de Rutas en Tiempo de Ejecución:** Para evitar errores de "Módulo no encontrado" al compartir código o ejecutarlo desde distintas terminales, se utiliza `sys.path.insert()` combinado con la librería `pathlib` para localizar dinámicamente la carpeta `src/` e inyectarla en el entorno de Python antes de iniciar los imports.
*   **Intercepción de Eventos (Sobrescritura de `destroy`):** Tkinter borra los datos de los campos de texto apenas se destruye la ventana. Para validar el login de forma segura, se sobreescribió el método `destroy` del popup de acceso. Cuando el usuario intenta loguearse, el script intercepta la acción, captura las credenciales tipeadas, las manda al Repositorio Core, y recién entonces permite el cierre de la ventana.
*   **Ventanas Superpuestas (`Toplevel` y `withdraw`):** El motor `tk.Tk()` inicia siempre una ventana principal en blanco. El orquestador oculta esta ventana inmediatamente usando `withdraw()`, dibuja el Login como una ventana secundaria flotante (`Toplevel`), y al aprobar el acceso, vuelve a mostrar la ventana principal con `deiconify()`, ya poblada con el entorno del Panel Principal.


## 9. Controlador Core: Copias de Seguridad en Caliente (Semana 4 - Adelanto)

**Archivo:** `src/controladores/orquestador_core.py`
**Objetivo:** Actuar como el "cerebro" del Módulo 1, aislando la lógica compleja de negocio y operando herramientas de seguridad de la base de datos sin comprometer la interfaz gráfica.

### 9.1 Lógica de Hot Backup
Se implementó un sistema de copia de seguridad en caliente utilizando el método nativo `.backup()` de la librería `sqlite3`. A diferencia de una copia de archivos tradicional (que corrompe la base de datos si ocurre mientras un usuario guarda información), este método clona los datos de forma transaccional y segura, sin necesidad de bloquear el sistema o desconectar a los usuarios (empleados facturando).

### 9.2 Gestión Autónoma de Directorios
Para evitar fallos de ejecución si el entorno es nuevo, el orquestador utiliza la librería `os` para verificar la existencia de la carpeta `db/backups`. Si no existe, el parámetro `exist_ok=True` de la función `os.makedirs()` la genera automáticamente. Además, se estandarizó la nomenclatura de los respaldos agregando un *timestamp* (`respaldo_frankie_YYYYMMDD_HHMMSS.db`) para evitar la sobrescritura de archivos.

### 9.3 Directiva Arquitectónica para Controladores (Módulos 2, 3 y 4)
Al momento de programar `orquestador_ventas.py` u `orquestador_rrhh.py`, el equipo debe respetar:
1. **El Controlador Calcula, no Dibuja:** Prohibido importar `tkinter` o `messagebox`. El controlador devuelve valores puros (ej. un `string` con el mensaje de error o éxito, o un `float` con un cálculo de IVA). La Vista es quien decide cómo dibujarlo.
2. **Centralización de la Matemática:** Cualquier operación de cálculo (descuentos, liquidaciones, sumatorias) se procesa en esta capa, no en los repositorios ni en las vistas.


## 10. Refactorización del Panel Principal: Control de Acceso (RBAC)

**Archivo:** `src/vistas/ui_panel.py`
**Objetivo:** Inyectar la lógica de Control de Acceso Basado en Roles (RBAC) para habilitar o restringir módulos de la interfaz según los permisos del usuario logueado.

### 10.1 Filtrado Dinámico de Interfaz
Se modificó la renderización del menú lateral. En lugar de mostrar todos los botones por defecto, el sistema ahora itera sobre la lista `self.usuario_actual.roles` (cargada previamente por el Repositorio durante el Login). Mediante validaciones booleanas simples (ej. `es_admin = "Administrador" in nombres_roles`), el panel decide qué botones (`ttk.Button`) instanciar y empaquetar con `.pack()`. 

*   **Ventas:** Solo accesible para Administradores, Gerentes y Empleados de Ventas.
*   **Inventario/RRHH:** Restringido a perfiles de gestión y compras.
*   **Backup del Sistema:** Acceso exclusivo y excluyente para el Administrador.


## 11. Refactorización de Infraestructura: Despliegue Automatizado

**Archivo:** `src/infraestructura/conexion.py`
**Objetivo:** Modificar el motor Singleton para que detecte bases de datos vacías y autoconstruya la estructura relacional a partir del archivo DDL, eliminando la necesidad de configuración manual por parte de los desarrolladores.

### 11.1 Auto-Inicialización del Esquema (`sqlite_master`)
Se incorporó el método `_verificar_e_inicializar_esquema()`. Durante el arranque, el Singleton consulta la tabla oculta `sqlite_master` para verificar si existen tablas creadas. Si la base de datos es un archivo nuevo y en blanco, el motor lee el archivo `db/esquema.sql` y ejecuta todas las sentencias DDL (creación de tablas, constraints y triggers) e inserciones semilla (DML) de una sola vez utilizando `cursor.executescript()`.
Esto garantiza que cualquier desarrollador (o cliente futuro) que clone el repositorio tenga el entorno de base de datos operativo en el primer milisegundo de ejecución, previniendo errores de "tabla no encontrada".


## 12. Testing Unitario y Resolución Criptográfica

**Archivos:** `tests/test_core.py` y `db/esquema.sql`
**Objetivo:** Auditar la lógica de negocio y la persistencia de datos (Dominio, Infraestructura y Controladores) mediante `pytest` antes de la integración a la rama principal (main).

### 12.1 Pruebas de Integración (Pytest)
Se desarrollaron 6 pruebas unitarias que validan el comportamiento aislado y combinado del Módulo 1:
1. **Singleton:** Verificación de instancia única de conexión en memoria (`test_singleton_conexion`).
2. **Dominio:** Instanciación correcta de las entidades Usuario y Rol (`test_creacion_usuario_y_rol`).
3. **Criptografía:** Validación de la longitud de salida (64 caracteres) del algoritmo SHA-256 (`test_hashing_password`).
4. **Persistencia y Auth:** Validación del acceso exitoso y el rechazo ante credenciales inválidas (`test_autenticacion_exitosa`, `test_autenticacion_fallida`).
5. **Orquestación:** Ejecución exitosa de la copia de seguridad y verificación de creación física del archivo en el disco (`test_ejecucion_backup`).

### 12.2 Resolución de Fallo Criptográfico en Semilla
Durante la ejecución de las pruebas, se detectó un desajuste entre el Repositorio (que encripta los ingresos en SHA-256) y el dato semilla del usuario 'admin' en `esquema.sql`, el cual estaba guardado en texto plano (`admin123`). Se refactorizó la sentencia `INSERT` en el DDL para almacenar directamente el hash criptográfico (`240be518fabd272...`), alineando la base de datos con los estándares de seguridad del sistema y logrando la aprobación total (PASSED) de la auditoría de software.

---
*(Los siguientes apartados se irán completando a medida que desarrollemos cada componente de la Infraestructura y el Módulo 1).*