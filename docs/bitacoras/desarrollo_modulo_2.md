# 1. desarrollo_modulo_2
## 1. `src/dominio/entidades_rrhh.py`
**Propósito:** Definir el modelo de objetos y la lógica de negocio del módulo de Recursos Humanos.
**Descripción:** Archivo del dominio que contiene la definición de la clase base `Persona` y la clase derivada `Empleado` (mediante herencia). Encapsula los atributos de datos personales y laborales, así como las validaciones asociadas a la gestión del personal.
**Responsabilidades clave:**    
- Representar la entidad `Persona` (superclase) con datos como CUIT, nombre, email, etc.
- Representar la entidad `Empleado` (subclase) sumando datos laborales específicos (legajo, sueldo, fecha de ingreso, etc.).
## 2. `src/infraestructura/repo_rrhh.py`
**Propósito:** Gestionar la persistencia de datos en la base de datos SQLite para las personas y empleados.
**Descripción:** Capa de acceso a datos (Repositorio) que traduce las operaciones sobre el objeto `Empleado` a consultas SQL. Maneja la comunicación con SQLite utilizando el gestor de conexión (`conexion.py`) y asegura transacciones compuestas para mantener la integridad de las tablas `personas` y `empleados`.
**Responsabilidades clave:**
- Registrar un nuevo empleado ejecutando una transacción atómica en dos pasos (`INSERT INTO personas` y luego `INSERT INTO empleados`).
 - Consultar empleados mediante sentencias `JOIN` para unir los datos de ambas tablas y reconstruir las instancias de los objetos.
 - Actualizar y deshabilitar registros de personal.
## 3. `src/vistas/ui_empleados.py`
**Propósito:** Proveer la interfaz gráfica (UI) para la interacción del usuario con la gestión de empleados.
**Descripción breve:** Capa de presentación gráfica desarrollada para la administración del personal. Permite visualizar el listado de empleados, ingresar nuevos registros a través de formularios con validaciones y gestionar altas, modificaciones o bajas.
**Responsabilidades clave:**
- Renderizar los formularios de captura de datos (nombre, CUIT, legajo, sueldo, etc.).        
- Invocar los métodos del `repo_rrhh.py` para guardar o consultar información sin incluir lógica directa de base de datos ni SQL.
- Mostrar mensajes de éxito o error al usuario.
# 2. Otros puntos de interés
1. En `esquema.sql`, el bloque  SEMILLAS (Datos Iniciales Obligatorios) se cambió INSERT INTO por INSERT OR IGNORE INTO (roles, usuarios y usuarios_roles)
2. Se creó el archivo de prueba temporal `test_rrhh.py` para testear el funcionamiento de los entregables.
3. En el CRUD, se implementa la baja lógica (Activado-Desactivado) en vez de la baja definitiva (Eliminar)
4. Se creó el archivo `estilos.py` como hoja de estilos para mantener la continuidad visual de las pantallas. Los archivos `iu_login.py,` `iu_empleados.py`, `clientes.py`, `proveedores.py`, etc. se referencian a través de nombres de clases de estilo de `ttk` (`TLabel`, `TEntry`, `TButton`, `Header.TLabel`, etc.). 