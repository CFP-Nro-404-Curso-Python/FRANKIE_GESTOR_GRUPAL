# Contrato de Arquitectura y Estructura de Directorios
**Proyecto:** Sistema de Gestión Comercial "Frankie"
**Patrón:** Clean Architecture (Arquitectura Limpia)
**Módulos:** 4 Módulos Verticales Autónomos

## 1. Reglas Estrictas de Integración
Este árbol define los límites de cada desarrollador. Para mitigar el Riesgo R-01 (Conflictos de Merge), queda **estrictamente prohibido** modificar archivos asignados a otro módulo sin previa autorización formal en la Matriz RACI.

## 2. Árbol de Directorios Oficial

📦 frankie_gestor_grupal  
│  
├── 📁 .venv/                       # Entorno virtual de Python  
├── 📁 db/                          # Persistencia y Modelo Relacional  
│   ├── 📜 esquema.sql              # DDL SQLite (10 tablas, 4 triggers)  
│   └── 🗄️ frankie_gestor.db        # Archivo binario de base de datos  
├── 📁 diagramas/                   # UML (Clases, Secuencia, Casos de Uso)  
├── 📁 docs/                        # Documentación PMI y Contratos  
├── 📁 src/                         # Código Fuente  
│   ├── 📁 dominio/                 # Capa 1: Entidades (Cero dependencias)  
│   │   ├── 🛡️ excepciones.py       # Compartido: Errores personalizados  
│   │   ├── 👤 entidades_core.py    # Módulo 1 (Seguridad)  
│   │   ├── 👥 entidades_rrhh.py    # Módulo 2 (RRHH)  
│   │   ├── 🛒 entidades_ventas.py  # Módulo 3 (Ventas)  
│   │   └── 📦 entidades_stock.py   # Módulo 4 (Inventario)  
│   │  
│   ├── 📁 infraestructura/         # Capa 2: Adaptadores de Base de Datos  
│   │   ├── 🔌 conexion.py          # Compartido: Patrón Singleton  
│   │   ├── 💾 repo_core.py         # Módulo 1  
│   │   ├── 💾 repo_rrhh.py         # Módulo 2  
│   │   ├── 💾 repo_ventas.py       # Módulo 3  
│   │   └── 💾 repo_stock.py        # Módulo 4  
│   │  
│   ├── 📁 controladores/           # Capa 3: Orquestadores y Lógica de Negocio  
│   │   ├── 🧠 orquestador_core.py  
│   │   ├── 🧠 orquestador_rrhh.py  
│   │   ├── 🧠 orquestador_ventas.py  
│   │   └── 🧠 orquestador_stock.py  
│   │  
│   └── 📁 vistas/                  # Capa 4: Interfaces (Tkinter)  
│       ├── 🖥️ ui_login.py          # Módulo 1: Autenticación  
│       ├── 🖥️ ui_panel.py          # Módulo 1: RBAC y Navegación  
│       ├── 🖥️ ui_empleados.py      # Módulo 2: CRUD Personal  
│       ├── 🖥️ ui_haberes.py        # Módulo 2: Recibos  
│       ├── 🖥️ ui_clientes.py       # Módulo 3: CRUD Clientes  
│       ├── 🖥️ ui_facturacion.py    # Módulo 3: Transaccional  
│       ├── 🖥️ ui_proveedores.py    # Módulo 4: CRUD Proveedores  
│       └── 🖥️ ui_inventario.py     # Módulo 4: Stock y Alertas  
│  
├── 📁 tests/                       # Entorno QA y Pruebas  
│   └── 🧪 test_stock.py            # Automatización pytest (Triggers)  
│  
└── 🚀 main.py                      # Punto de entrada del sistema  