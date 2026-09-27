# Diccionario de la Estructura de Desglose del Trabajo (WBS Dictionary)
**Proyecto:** Sistema de Gestión Comercial "Frankie"
## Paquete de Trabajo 1.1: Gestión, Documentación e Infraestructura Base
* **Código WBS:** 1.1
* **Responsable Asignado:** Equipo Completo / Liderazgo de Documentación
* **Descripción del Trabajo:** Redacción de la suite documental PMI, modelado de diagramas UML, creación del script DDL `db/esquema.sql` (10 tablas y 4 triggers) e implementación de la conexión Singleton SQLite.
* **Entregables:** Carpeta `docs/` completa, `db/esquema.sql`, `src/infraestructura/conexion.py`.
* **Criterios de Aceptación:** Base de datos en 3FN con `PRAGMA foreign_keys = ON;` activado y documentos aprobados por la cátedra.
## Paquete de Trabajo 1.2: Módulo 1 - Seguridad y Núcleo del Sistema (Core)
* **Código WBS:** 1.2
* **Responsable Asignado:** David
* **Descripción del Trabajo:** Desarrollo de entidades de seguridad, hashing SHA-256 en BLOB, formulario de Login con bloqueo tras 3 intentos fallidos y Panel Principal con menú adaptativo según el rol (RBAC).
* **Entregables:** `entidades_core.py`, `repo_core.py`, `ui_login.py`, `ui_panel.py`, `main.py`.
* **Criterios de Aceptación:** Ninguna clave en texto plano y navegación bloqueada/permitida correctamente según permisos del rol.
## Paquete de Trabajo 1.3: Módulo 2 - Recursos Humanos y Nómina de Sueldos
* **Código WBS:** 1.3
* **Responsable Asignado:** Alicia
* **Descripción del Trabajo:** Implementación del patrón de herencia relacional entre `personas` y `empleados`, CRUD de personal y módulo de generación de Recibos de Haberes por escala salarial.
* **Entregables:** `entidades_rrhh.py`, `repo_rrhh.py`, `ui_empleados.py`, `ui_haberes.py`.
* **Criterios de Aceptación:** Inserción coordinada e integrada en tablas `personas` y `empleados`, con cálculo automático de haberes imborrables.
## Paquete de Trabajo 1.4: Módulo 3 - Ventas, Facturación y Clientes
* **Código WBS:** 1.4
* **Responsable Asignado:** Uriel
* **Descripción del Trabajo:** Desarrollo de entidades de clientes y facturación, captura de precio histórico de venta e interfaz transaccional Cabecera-Detalle en `ui_facturacion.py`.
* **Entregables:** `entidades_ventas.py`, `repo_ventas.py`, `ui_clientes.py`, `ui_facturacion.py`.
* **Criterios de Aceptación:** Emisión exitosa de comprobantes conectada con triggers de cálculo de totales y actualización de stock.
## Paquete de Trabajo 1.5: Módulo 4 - Inventario y Cadena de Suministro
* **Código WBS:** 1.5
* **Responsable Asignado:** Alicia
* **Descripción del Trabajo:** Modelado de proveedores y productos, interfaz de inventario con alerta de stock crítico (`stock_actual <= stock_minimo`) y suite de pruebas con `pytest`.
* **Entregables:** `entidades_stock.py`, `repo_stock.py`, `ui_proveedores.py`, `ui_inventario.py`, `tests/test_stock.py`.
* **Criterios de Aceptación:** Alerta de stock visible en interfaz gráfica y suite de pruebas `pytest` aprobada al 100%.