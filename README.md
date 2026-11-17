# 🚀 Frankie - Sistema de Gestión Comercial

Sistema de escritorio integral desarrollado en **Python** bajo los principios de **Clean Architecture**, diseñado para automatizar y optimizar la administración comercial, control de inventario, padrón de proveedores y gestión de recursos humanos de PyMEs.

---

## ✨ Características Principales

### 📦 1. Inventario y Control de Stock
* **Stock Mínimo Inteligente:** Configurado por defecto en **75 unidades**.
* **Alertas de Reposición:** Detección automática de artículos con stock crítico (≤ 75 unidades).
* **Cálculo Automático de Precios:** El precio de venta se calcula de forma automática aplicando un **20% de ganancia sobre el precio de costo**.
* **Órdenes de Compra:** Emisión automatizada de Órdenes de Compra ante stock crítico, con opción de exportación a formato **HTML / impresión a PDF**.
* **CRUD Completo:** Alta, modificación, listado con filtros y baja lógica (desactivación).

### 🤝 2. Gestión de Proveedores
* **Padrón Comercial:** Registro completo de personas físicas y jurídicas (CUIT, razón social, rubro, datos de contacto y domicilio).
* **Baja Lógica:** Desactivación y reactivación segura de proveedores sin perder la integridad referencial histórica.

### 👥 3. Módulos Adicionales (RRHH y Ventas)
* Gestión de Empleados, liquidación de Haberes y control de recibos.
* Módulo de Facturación y Ventas integrado con el stock en tiempo real.

---

## 🏛️ Arquitectura y Tecnologías

El proyecto sigue una estructura modular orientada a **Clean Architecture**:
* **Lenguaje:** Python 
* **Interfaz Gráfica (UI):** Tkinter / ttk (Diseño nativo moderno y adaptable).
* **Persistencia de Datos:** SQLite con transacciones seguras e integridad referencial (`FOREIGN KEY` activas).
* **Control de Esquema:** Script de inicialización automatizada (`inicializar_db.py`) que permite aplicar migraciones de estructura al vuelo sin pérdida de datos.

---

## 🛠️ Guía de Instalación y Configuración para el Equipo e Interesados

### 1. Clonar el repositorio
Clona el repositorio oficial (la versión estable y completa se encuentra disponible directamente en la rama principal **`main`**):
```bash
git clone [https://github.com/CFP-Nro-404-Curso-Python/FRANKIE_GESTOR_GRUPAL.git](https://github.com/CFP-Nro-404-Curso-Python/FRANKIE_GESTOR_GRUPAL.git)
cd FRANKIE_GESTOR_GRUPAL
