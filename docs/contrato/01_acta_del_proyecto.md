
# Acta de Constitución del Proyecto (Project Charter)
**Nombre del Proyecto:** Sistema de Gestión Comercial "Frankie"
**Fecha:** 22 de Septiembre de 2026
**Duración:** 6 Semanas
**Documentalista:** Alicia López
# 1. Propósito y Justificación del Proyecto
Desarrollar e implementar un sistema de escritorio integral de gestión comercial denominado "Frankie", construido en Python (Tkinter/CustomTkinter) y SQLite. El sistema automatizará procesos transaccionales clave (seguridad, nómina de haberes, facturación e inventarios) bajo una arquitectura modular y una base de datos relacional sólida en 3FN.
# 2. Objetivos del Proyecto (Criterios SMART)
* **Objetivo de Alcance:** Entregar 4 módulos funcionales e integrados (Core, RRHH/Nómina, Ventas/Facturación, Inventario/Stock) con persistencia relacional en SQLite y reglas de negocio automatizadas mediante 4 triggers.
* **Objetivo de Tiempo:** Completar el desarrollo, integración y pruebas automatizadas en un plazo estricto de 6 semanas.
* **Objetivo de Calidad:** Garantizar 0 contraseñas en texto plano, integridad referencial mediante claves foráneas y un 100% de aprobación en pruebas unitarias críticas (`pytest`).
# 3. Equipo de Trabajo y Asignación de Módulos
* **David:** Responsable de Módulo 1 (Seguridad, Núcleo del Sistema / Core y UI Base).
* **Uriel:** Responsable de Módulo 3 (Ventas, Facturación, Clientes y FacturaDetalle).
* **Alicia:** Responsable de Módulo 2 (Recursos Humanos y Nómina) y Módulo 4 (Inventario y Cadena de Suministro).
# 4. Asignación de Responsabilidades Técnicas
| Integrante | Módulo Asignado                | Componentes Principales                                                                 |
| :--------- | :----------------------------- | :-------------------------------------------------------------------------------------- |
| **David**  | Módulo 1: Core y Seguridad     | Autenticación SHA-256, RBAC, `ui_login.py`, `ui_panel.py`, Singleton BD, Backup.        |
| **Alicia** | Módulo 2: RRHH y Haberes       | Entidad `Empleado` (hereda de `Persona`), CRUD personal, cálculo de Recibos de Haberes. |
| **Uriel**  | Módulo 3: Ventas y Facturación | Entidad `Cliente`, comprobantes `Factura` / `FacturaDetalle`, `ui_facturacion.py`.      |
| **Alicia** | Módulo 4: Inventario y Stock   | Entidad `Proveedor`, `Producto`, alertas de stock crítico, `tests/test_stock.py`.       |
# 5. Criterios de Éxito del Proyecto
1. Ejecución completa del script DDL (`db/esquema.sql`) con 10 tablas relacionales activas.
2. Control de acceso con 3 intentos fallidos máximos y menú adaptativo por roles.
3. Descuento automático e imborrable de inventario ante cada venta registrada.
4. Cumplimiento total del cronograma de 6 semanas sin desvíos en la fecha de entrega final.