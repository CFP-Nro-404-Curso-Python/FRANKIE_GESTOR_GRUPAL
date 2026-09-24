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

---
*(Los siguientes apartados se irán completando a medida que desarrollemos cada componente de la Infraestructura y el Módulo 1).*