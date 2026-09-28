# 1. desarrollo_modulo_2
Todos los archivos mencionados tienen notas para facilitar la comprensión y el aprendizaje. 
## 1. `src/dominio/entidades_rrhh.py`
**Propósito:** Definir el modelo de objetos y la lógica de negocio del módulo de Recursos Humanos.
**Descripción:** Archivo del dominio que contiene la definición de la clase base `Persona` y la clase derivada `Empleado` (mediante herencia). Encapsula los atributos de datos personales y laborales, así como las validaciones asociadas a la gestión del personal.
**Responsabilidades clave:**    
- Representar la entidad `Persona` (superclase) con datos como CUIT, nombre, email, etc.
- Representar la entidad `Empleado` (subclase) sumando datos laborales específicos (legajo, sueldo, fecha de ingreso, etc.).
**Notas de aprendizaje**: 
1. *Reutilización y DRY (Don't Repeat Yourself)*: La herencia mediante `super().__init__(**kwargs)` permite instanciar un `Empleado` pasando tanto sus datos laborales como sus datos personales sin duplicar código.
2. *Evitar _Name Shadowing_*: Usar `id_persona` en los parámetros en lugar de `id` evita sobreescribir la función integrada de Python `id()`, manteniendo PyCharm sin alertas.
3. *Protección ante valores nulos (`Optional`)*: Usar `Optional[int] = None` refleja la realidad de las entidades en memoria antes de ser persistidas en la BD.
4. *Encapsulamiento del Comportamiento*: El método `obtener_nombre_completo()` concentra la lógica de presentación del nombre en la clase, liberando a la UI de esa responsabilidad.
## 2. `src/infraestructura/repo_rrhh.py`
**Propósito:** Gestionar la persistencia de datos en la base de datos SQLite para las personas y empleados.
**Descripción:** Capa de acceso a datos (Repositorio) que traduce las operaciones sobre el objeto `Empleado` a consultas SQL. Maneja la comunicación con SQLite utilizando el gestor de conexión (`conexion.py`) y asegura transacciones compuestas para mantener la integridad de las tablas `personas` y `empleados`.
**Responsabilidades clave:**
- Registrar un nuevo empleado ejecutando una transacción atómica en dos pasos (`INSERT INTO personas` y luego `INSERT INTO empleados`).
 - Consultar empleados mediante sentencias `JOIN` para unir los datos de ambas tablas y reconstruir las instancias de los objetos.
 - Actualizar y deshabilitar registros de personal.
 **Notas de aprendizaje**: 
 
## 3. `src/vistas/ui_empleados.py`
**Propósito:** Proveer la interfaz gráfica (UI) para la interacción del usuario con la gestión de empleados.
**Descripción breve:** Capa de presentación gráfica desarrollada para la administración del personal. Permite visualizar el listado de empleados, ingresar nuevos registros a través de formularios con validaciones y gestionar altas, modificaciones o bajas.
**Responsabilidades clave:**
- Renderizar los formularios de captura de datos (nombre, CUIT, legajo, sueldo, etc.).        
- Invocar los métodos del `repo_rrhh.py` para guardar o consultar información sin incluir lógica directa de base de datos ni SQL.
- Mostrar mensajes de éxito o error al usuario.
## 4. `db/esquema.sql`
+  En el bloque  SEMILLAS (Datos Iniciales Obligatorios) se cambió INSERT INTO por INSERT OR IGNORE INTO (roles, usuarios y usuarios_roles)
- Restricción `CHECK` en `cargo`: Se limitaron los valores a `'Gerente'`, `'Administrador'`, `'Empleado_Admin'`, `'Empleado_Ventas'`, `'Empleado_Compras'`.
- Restricción `CHECK` en `sector`: Se limitaron los valores a `'Gestión'`, `'Staff'`, `'Ventas'`, `'Compras'`, `'Administración'`.
- Inclusión de `tipo_vinculo`: Se agregó la columna con su restricción `CHECK` (`'Propietario'`, `'Contratado'`, `'Pasante'`, `'Planta'`).
- Inclusión de `activo`: Se agregó con valor por defecto `1` para permitir la baja lógica de empleados (_Soft Delete_).
# 3. Otros puntos de interés
1.
1. Se creó el archivo de prueba temporal `test_rrhh.py` para testear el funcionamiento de los entregables.
2. En el CRUD, se implementa la baja lógica (Activado-Desactivado) en vez de la baja definitiva (Eliminar)
3. Se creó el archivo `estilos.py` como hoja de estilos para mantener la continuidad visual de las pantallas. Los archivos `iu_login.py,` `iu_empleados.py`, `clientes.py`, `proveedores.py`, etc. se referencian a través de nombres de clases de estilo de `ttk` (`TLabel`, `TEntry`, `TButton`, `Header.TLabel`, etc.). 