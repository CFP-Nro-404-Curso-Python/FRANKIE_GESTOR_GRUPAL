# Cronograma de Hitos y Análisis de Camino Crítico (CPM)
**Proyecto:** Sistema de Gestión Comercial "Frankie"
**Duración Total:** 6 Semanas
# 1. Cronograma por Semanas

* **Semana 1:** Aprobación de Documentación PMI, DDL `db/esquema.sql` e Infraestructura Singleton de BD.
* **Semana 2:** Desarrollo de Módulo 1 (Core/Seguridad) y Modelado de la Superclase `personas`.
* **Semana 3:** Desarrollo en paralelo de Módulo 2 (RRHH/Nómina) y Módulo 4 (Inventario/Stock).
* **Semana 4:** Desarrollo de Módulo 3 (Ventas/Facturación) e integración con Stock via Triggers.
* **Semana 5:** Integración de UI (Panel Principal RBAC + Módulos) y Pruebas Automatizadas con `pytest`.
* **Semana 6:** Pruebas de Aceptación, Auditoría de Código, Backup y Entrega Final.
# 2. Secuencia de Dependencias y Camino Crítico (Critical Path)

## Fase 1: Infraestructura Base y Esqueleto Común (Semanas 1 y 2)
Esta es la fase de mayor dependencia. Si estos componentes se retrasan, detienen a todo el equipo.
1. **Definición e inicialización del Esquema SQL (`db/esquema.sql`)**
       - **Responsable:** Módulo 1 (Core) / Módulo 2 (RRHH).
    - **Entregable:** Creación de las tablas base (`roles`, `usuarios`, `personas`) y habilitación de claves foráneas.
       
2. **Conexión a la Base de Datos (`src/infraestructura/conexion.py`)** 
    - **Responsable:** Compartido.
    - **Entregable:** Gestor Singleton para la apertura y cierre de conexiones con SQLite.
    
3. **Modelado de la Superclase `Persona` (`src/dominio/entidades_rrhh.py`)**
    - **Responsable:** Módulo 2 (RRHH).      
    - **Razón Crítica:** La clase `Persona` y la tabla `personas` deben existir previamente para que el Módulo 3 (`Clientes`) y el Módulo 4 (`Proveedores`) puedan heredar sus estructuras sin conflictos en Git.
## Fase 2: Desarrollo Paralelo por Módulos Verticales (Semanas 3 y 4)

Una vez definida la infraestructura base, el trabajo se desacopla y cada integrante desarrolla de forma autónoma.

- **Módulo 1 (Core):** Implementación de la autenticación (`ui_login.py`), cifrado SHA-256/BLOB y estructura del panel principal con menú dinámico RBAC (`ui_panel.py`).
    
- **Módulo 2 (RRHH):** Desarrollo del CRUD de Empleados (`ui_empleados.py`), vinculación con usuarios y emisión de Recibos de Haberes.
    
- **Módulo 3 (Ventas):** Desarrollo del CRUD de Clientes e interfaz de Facturación (`ui_facturacion.py`) con tabla interactiva `Treeview`.
    
- **Módulo 4 (Inventario):** Desarrollo del CRUD de Proveedores y CRUD de Productos (`ui_inventario.py`) con control de `stock_minimo`.
    
## Fase 3: Integración de Triggers y Pruebas Transaccionales (Semana 5)
En esta etapa los módulos se entrelazan mediante las transacciones comerciales.
1. **Vinculación Ventas - Inventario (Triggers 2 y 3)**
       - **Hito Crítico:** El Módulo 3 (Ventas) no puede dar por finalizada la facturación sin que el Módulo 4 (Inventario) valide la respuesta de los _Triggers_ de SQLite.
    - **Acción:** Ejecución de pruebas con `pytest` para verificar el aborto automático por falta de stock y el descuento físico de mercadería.
       
2. **Cálculo de Totales de Factura (Triggers 1 y 4)**   
    - **Acción:** Verificación automatizada de subtotales y acumulados en la cabecera de la factura.
## Fase 4: Ensamble Final, Seguridad y Cierre (Semana 6)
1. **Orquestación en `ui_panel.py`** 
    - Integración de los menús de cada módulo en la ventana principal respetando la matriz de permisos por rol (RBAC).
        
    - Verificación de la técnica de _Lazy Imports_ para asegurar el rendimiento al abrir cada ventana.
        
2. **Cierre de Documentación y QA**
    - Consolidación del archivo `01-Frankie Project Charter.md` y ejecución de la suite completa de pruebas unitarias (`tests/`).