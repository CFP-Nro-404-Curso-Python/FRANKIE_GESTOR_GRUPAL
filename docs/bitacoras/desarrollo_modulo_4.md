## 1. Resumen de Objetivos e Innovaciones
- **Refactorización del Dominio:** Implementación del patrón `@dataclass` para modelar de forma limpia las entidades `Producto` y `Proveedor`.
- **Persistencia Robusta:** Adopción del patrón _Repository_ (`repo_stock.py`) para aislar completamente las consultas SQL de la lógica de negocio y la interfaz gráfica.
- **Garantía de Integridad y Reglas de Negocio:**
    - Freno absoluto a valores físicamente imposibles en el inventario (**Stock Negativo**).
    - Monitoreo y alertas automáticas al alcanzar el **Stock Mínimo** de reposición.
    - Gestión de proveedores y sanitización de datos de entrada.
        
- **Estrategia de QA sin Impacto:** Desarrollo de suite de pruebas unitarias (`test_stock.py`) e interfaz gráfica (`test_ui_stock.py`) ejecutadas exclusivamente en una **base de datos temporal en memoria (`:memory:`)**, garantizando no alterar la base de datos de producción (`frankie_gestor.db`).
## 2.Componentes Desarrollados y Refactorizados
### A. Capa de Dominio (`dominio/entidades_stock.py`)
- Modelado mediante `@dataclass` con tipado estricto.
- Método `requiere_reposicion` para evaluar dinámicamente si el `stock_actual` cayó por debajo del `stock_minimo`.
### B. Capa de Infraestructura (`infraestructura/repo_stock.py`)
- **`guardar_proveedor` / `listar_proveedores`:** Alta y consulta de proveedores asociados a la tabla base `personas`.
- **`guardar_producto` / `listar_productos`:** Carga y filtrado de productos con soporte para listados generales o únicamente alertas de stock.
- **`ajustar_stock`:** Método transaccional que valida que el ajuste no genere un stock menor a cero, lanzando un `ValueError` preventivo antes del `COMMIT`.
### C. Batería de Pruebas Unitarias (`test/test_stock.py`)
- **`test_guardar_y_listar_proveedor`:** Valida la persistencia del proveedor.
- **`test_guardar_producto_y_evaluar_alerta_stock`:** Verifica la activación de luces rojas/alertas cuando el stock es inferior al mínimo.
- **`test_ajustar_stock_valido_e_insuficiente`:** Confirma que el sistema permita sumar/restar stock válido y bloquee los intentos de dejar el inventario en negativo.
### D. Pruebas de Interfaz Gráfica (`test/test_ui_stock.py`)
- Simulación de formularios Tkinter, tablas `Treeview` e inyección de comportamiento (_Mocking_) para validar la experiencia de usuario sin escribir en el disco rígido.
## 3. Documentación Gráfica (UML)
Se generaron los diagramas UML estandarizados para el módulo en formato **PlantUML / Mermaid** (listos para Obsidian y documentación formal):
1. **Casos de Uso:** Registro de Proveedores, Carga de Productos, Ajustes de Stock y Consultas de Stock Mínimo. 
2. **Clases:** Relaciones relacionales entre `Proveedor`, `Producto` y los métodos del `RepositorioStock`.
3. **Secuencia:** Flujo completo de validación al ajustar stock (evaluación de stock actual, manejo de excepciones y actualización en BD)