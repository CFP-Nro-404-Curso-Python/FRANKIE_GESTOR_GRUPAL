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
## 5. `src/infraestructura/repo_haberes.py`
- **Propósito**: Actuar como el repositorio de infraestructura encargado del cálculo de conceptos salariales (remunerativos y deducciones) y de la persistencia de las liquidaciones de sueldos en la base de datos SQLite.
- **Descripción breve**: Es un módulo desacoplado de la interfaz gráfica que procesa la lógica de la liquidación de haberes para un empleado en un periodo determinado y guarda o actualiza el resultado final en la base de datos, soportando inyección de conexiones para pruebas aisladas. 
- **Responsabilidades clave**:
    - *Cálculo de haberes remunerativos*: Procesar el sueldo básico, antigüedad (1% por año), presentismo (8.33%), horas extras (150%), feriados trabajados (200%) y comisiones por ventas (1.5%).
    - *Cálculo de deducciones de ley*: Aplicar los porcentajes de retención correspondientes a Jubilación (11%), PAMI (3%), Obra Social (3%), Cuota Sindical (2.5%) y descontar adelantos solicitados.
    - *Persistencia segura (`UPSERT`)*: Ejecutar las consultas SQL (`INSERT OR REPLACE` / `ON CONFLICT DO UPDATE`) para guardar los montos calculados (totales y salario neto) en la tabla `liquidaciones`.
    - *Desacoplamiento y testabilidad*: Permitir la recepción de conexiones opcionales a bases de datos (`conexion_alt`) para facilitar pruebas unitarias aisladas sin afectar la conexión Singleton global (`ConexionDB`) ni la BD de producción.
## 6. `src/vistas/iu_haberes.py
- **Propósito**: Proveer la interfaz gráfica de usuario (UI) para la carga de variables de liquidación, visualización de importes calculados y previsualización de los recibos de sueldo dentro de la aplicación Tkinter.
- **Descripción breve**: Es el módulo de la capa de presentación que interactúa de forma directa con el usuario, capturando los datos de haberes/descuentos del legajo seleccionado, invocando la lógica de cálculo del repositorio y desplegando los resultados en pantalla con opción de impresión.
- **Responsabilidades clave**:
    - *Captura de entradas de usuario*: Renderizar el formulario con controles (`ttk.Entry`, `ttk.Checkbutton`, `ttk.Combobox`) para ingresar básico, antigüedad, presentismo, horas extra, feriados, ventas, adelantos y retenciones de ley.
    - *Gestión de eventos y validaciones*: Validar que los campos numéricos contengan valores válidos antes de procesar la liquidación y reaccionar a cambios de selección de empleados o periodos.
    - *Comunicación con la capa de infraestructura*: Invocar a `RepositorioHaberes.calcular_liquidacion(...)` enviando los parámetros seleccionados y procesando la respuesta recibida para refrescar las etiquetas de montos netos y totales.
    - *Modal de previsualización e impresión*: Generar una ventana emergente (`Toplevel`) que maqueta el recibo de sueldo en formato de texto estandarizado con la instrucción para captura de pantalla / impresión directa (`Print Screen`).
# 3. Liquidación de haberes
Involucra `iu_haberes.py`, `repo_haberes.py`
Administrador cobra por contrato de locación de servicios monotributo categoría D
Gerente Monotributo categoría F

Empleados
*Haberes remunerativos*
Salario básico: 1200000
Antigüedad: 1% por año trabajado
Presentismo: 8,33%
Horas extra: 50% por hora trabajado
Feriado trabajado: 100% por día trabajado
Comisión por ventas: 5%
*Haberes no remunerativos*
Asignaciones familiares (comentada, se va a utilizar más tarde con una API)
*Deducciones y descuentos*
Aportes jubilatorios: 11%
Ley 19032 (PAMI): 3%
Obra social: 3%
Cuota sindical: 2,5% (no aplica a pasantes)
Adelanto de haberes (según corresponda)
