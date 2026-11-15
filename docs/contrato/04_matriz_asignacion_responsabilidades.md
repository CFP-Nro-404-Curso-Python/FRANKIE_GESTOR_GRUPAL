# Matriz de Asignación de Responsabilidades (Matriz RACI)
**Proyecto:** Sistema de Gestión Comercial "Frankie"
# 1. Leyenda
* **R - Responsable (Responsible):** Quien ejecuta la tarea técnica.
* **A - Aprobador (Accountable):** Quien responde por el resultado final y aprueba la calidad.
* **C - Consultado (Consulted):** Quien provee información clave para el desarrollo.
* **I - Informado (Informed):** Quien es notificado sobre los avances.
# 2. Matriz de Responsabilidades

| Código WBS | Paquete de Trabajo / Entregable          | David (M1: Core) |   Uriel (M3: Ventas)   | Alicia (M2/M4: RRHH y Stock) |
| :--------: | :--------------------------------------- | :--------------: | :--------------------: | :--------------------------: |
|  **1.1**   | **Gestión e Infraestructura Base**       |                  |                        |                              |
|   1.1.1    | Documentación Fundacional PMI            |      **C**       |         **C**          |          **A / R**           |
|   1.1.2    | Diagramas UML y Arquitectura             |      **C**       |         **C**          |          **A / R**           |
|   1.1.3    | Esquema SQL Base y Triggers              |    **A / R**     |         **C**          | **R** (Superclase Personas)  |
|  **1.2**   | **Módulo 1: Core y Seguridad**           |                  |                        |                              |
|   1.2.1    | Hashing, Autenticación y Dominio         |    **A / R**     |         **I**          |            **I**             |
|   1.2.2    | Interfaces UI Login y Panel RBAC         |    **A / R**     |         **I**          |            **I**             |
|  **1.3**   | **Módulo 2: Recursos Humanos y Haberes** |                  |                        |                              |
|   1.3.1    | Herencia Relacional e Interfaces RRHH    |      **I**       |         **I**          |          **A / R**           |
|   1.3.2    | Emisión de Recibos de Haberes            |      **I**       |         **I**          |          **A / R**           |
|  **1.4**   | **Módulo 3: Ventas y Facturación**       |                  |                        |                              |
|   1.4.1    | Dominio Clientes y Facturación           |      **I**       |       **A / R**        |            **I**             |
|   1.4.2    | UI Facturación Cabecera-Detalle          |      **I**       |       **A / R**        |  **C** (Integración Stock)   |
|  **1.5**   | **Módulo 4: Inventario y Pruebas**       |                  |                        |                              |
|   1.5.1    | Dominio Productos y Proveedores          |      **I**       |         **I**          |          **A / R**           |
|   1.5.2    | Alertas de Stock y Test QA (`pytest`)    |      **I**       | **C** (Triggers Venta) |          **A / R**           |
