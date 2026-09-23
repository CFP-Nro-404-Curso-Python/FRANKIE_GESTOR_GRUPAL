# Documentación de Desarrollo - Módulo 1 (Core)
**Proyecto:** Frankie Gestor - Iteración 01  
**Arquitectura:** Clean Architecture (Arquitectura Limpia)  
**Tecnologías:** Python 3, SQLite3, Tkinter

## 1. Introducción al Módulo Core
Este documento detalla el desarrollo del Módulo 1, encargado de la gestión base del sistema: **Personas, Usuarios, Roles y Empleados**. 
El objetivo de este módulo es sentar las bases arquitectónicas para que los Módulos 2 (Ventas) y 3 (Stock) puedan desarrollarse de forma paralela y autónoma, compartiendo únicamente la capa de Dominio e Infraestructura básica.

## 2. Flujo de Datos (Regla de Dependencia)
Para mantener el sistema escalable y libre de acoplamiento espagueti, respetamos una regla estricta de adentro hacia afuera:
1. **Vista (Tkinter):** Captura la acción del usuario y llama al Controlador. No conoce a la Base de Datos.
2. **Controlador (Orquestador):** Aplica la lógica de negocio usando las Entidades de Dominio y llama a la Infraestructura.
3. **Infraestructura (Repositorio/Conexión):** Ejecuta las sentencias SQL y devuelve Entidades de Dominio.
4. **Dominio (Entidades/Excepciones):** No depende de absolutamente nada. Es Python puro.

---
*(Los siguientes apartados se irán completando a medida que desarrollemos cada archivo).*