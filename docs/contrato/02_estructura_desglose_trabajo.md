# Estructura de Desglose del Trabajo (EDT / WBS)
**Proyecto:** Sistema de Gestión Comercial "Frankie"

```
1.0 Proyecto Sistema de Gestión Comercial "Frankie"
│
├── 1.1 Gestión, Documentación e Infraestructura Base
│   ├── 1.1.1 Documentación Fundacional PMI (Charter, WBS, Diccionario, RACI, Cronograma, Riesgos)
│   ├── 1.1.2 Diseño de Diagramas UML (Clases, Casos de Uso, Secuencia)
│   ├── 1.1.3 Base de Datos Relacional (`db/esquema.sql` - 10 tablas y 4 triggers)
│   └── 1.1.4 Gestor Singleton de Conexión SQLite (`src/infraestructura/conexion.py`)
│
├── 1.2 Módulo 1: Seguridad y Núcleo del Sistema (Core) - [David]
│   ├── 1.2.1 Entidades `Usuario` y `Rol` (`entidades_core.py`)
│   ├── 1.2.2 Repositorio de Autenticación con Hashing SHA-256 (`repo_core.py`)
│   ├── 1.2.3 Interfaz de Login con Control de Intentos (`ui_login.py`)
│   └── 1.2.4 Panel Principal RBAC y Copia de Seguridad (`ui_panel.py`)
│
├── 1.3 Módulo 2: Recursos Humanos y Nómina de Sueldos - [Alicia]
│   ├── 1.3.1 Entidades `Persona` y `Empleado` (`entidades_rrhh.py`)
│   ├── 1.3.2 Repositorio con Herencia Relacional (`repo_rrhh.py`)
│   ├── 1.3.3 Vista de Gestión de Personal (`ui_empleados.py`)
│   └── 1.3.4 Vista y Emisión de Recibos de Haberes (`ui_haberes.py`)
│
├── 1.4 Módulo 3: Ventas, Facturación y Clientes - [Uriel]
│   ├── 1.4.1 Entidades `Cliente`, `Factura` y `FacturaDetalle` (`entidades_ventas.py`)
│   ├── 1.4.2 Repositorio de Transacciones de Venta (`repo_ventas.py`)
│   ├── 1.4.3 Vista de Administración de Clientes (`ui_clientes.py`)
│   └── 1.4.4 Vista de Facturación Cabecera-Detalle (`ui_facturacion.py`)
│
└── 1.5 Módulo 4: Inventario y Cadena de Suministro - [Alicia]
    ├── 1.5.1 Entidades `Proveedor` y `Producto` (`entidades_stock.py`)
    ├── 1.5.2 Repositorio de Stock y Ajustes (`repo_stock.py`)
    ├── 1.5.3 Vista de Proveedores (`ui_proveedores.py`)
    ├── 1.5.4 Vista de Inventario con Alerta Visual (`ui_inventario.py`)
    └── 1.5.5 Pruebas Automatizadas QA (`tests/test_stock.py`)
```
# División del trabajo detallada
## MÓDULO 1: SEGURIDAD Y NÚCLEO DEL SISTEMA (CORE)
Misión: Garantizar el acceso seguro, el rendimiento del arranque y la navegación.

* Base de Datos / Dominio:
  - Tablas: usuarios, roles, usuarios_roles.
* Vistas (Tkinter) y Controladores:
  - main.py / ui_login.py: Autenticación, contraseñas con hash SHA-256 (BLOB) y límite de 3 intentos.
  - ui_panel.py: Menú orquestador con menú dinámico (RBAC), Lazy Imports y Hot Backup.
* Desafío Técnico: Administrar la matriz de permisos por rol para activar/desactivar botones.
## MÓDULO 2: RECURSOS HUMANOS Y NÓMINA DE SUELDOS
Misión: Administrar el legajo del personal y la generación de recibos de haberes.

* Base de Datos / Dominio:
  - Clase base 'Persona' y heredada 'Empleado'.
  - Tablas: personas, empleados.
* Vistas (Tkinter) y Controladores:
  - ui_empleados.py: CRUD completo de Empleados.
  - ui_haberes.py: Emisión y cálculo de Recibos de Haberes según el sueldo base del rol.
* Desafío Técnico: Mapear la herencia relacional (Persona -> Empleado) en SQLite.
## MÓDULO 3: VENTAS, FACTURACIÓN Y CLIENTES
Misión: El área comercial. Generar ventas e integrar comprobantes sin fallar en cálculos.

* Base de Datos / Dominio:
  - Tablas: clientes (hereda de personas), facturas, facturas_detalles.
* Vistas (Tkinter) y Controladores:
  - CRUD de Clientes.
  - ui_facturacion.py: Pantalla Cabecera-Detalle para seleccionar cliente, vendedor y productos (Treeview).
* Desafío Técnico / QA: Validar que los TRIGGERS 1 y 4 calculen subtotales y acumulados correctamente.
## MÓDULO 4: INVENTARIO Y CADENA DE SUMINISTRO
Misión: Controlar el stock disponible y gestionar proveedores de accesorios.

* Base de Datos / Dominio:
  - Tablas: proveedores (hereda de personas), productos.
* Vistas (Tkinter) y Controladores:
  - CRUD de Proveedores.
  - ui_inventario.py: CRUD de Productos (búsqueda, actualización de precios y alerta stock_minimo).
* Desafío Técnico / QA: Pruebas automatizadas (pytest) para TRIGGERS 2 y 3 (aborto por falta de stock y descuento).