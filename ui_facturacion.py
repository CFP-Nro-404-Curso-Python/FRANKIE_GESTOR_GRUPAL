import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)

# ==========================================
# 1. CAPA DE SERVICIO / BASE DE DATOS
# ==========================================
class FacturacionService:
    """Maneja exclusivamente la comunicación con la base de datos."""
    def __init__(self, db_name: str = "frankie_gestor.db"):
        self.db_name = db_name

    def guardar_factura(self, id_cliente: int, id_vendedor: int, detalles: list) -> int:
        """Guarda la cabecera y el detalle en una sola transacción."""
        conexion = sqlite3.connect(self.db_name)
        try:
            conexion.execute("PRAGMA foreign_keys = ON;")
            cursor = conexion.cursor()

            # Insertar cabecera
            cursor.execute(
                "INSERT INTO facturas (id_cliente, id_vendedor) VALUES (?, ?)", 
                (id_cliente, id_vendedor)
            )
            id_factura = cursor.lastrowid

            # Insertar detalles
            for item in detalles:
                cursor.execute(
                    """INSERT INTO facturas_detalles 
                       (id_factura, id_producto, cantidad, precio_unitario, descuento_porcentaje) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (id_factura, item['id_producto'], item['cantidad'], item['precio'], item['descuento'])
                )

            conexion.commit()
            return id_factura

        except Exception as e:
            conexion.rollback()
            raise e  # Lanza la excepción para que la UI la maneje
        
        finally:
            conexion.close()


# ==========================================
# 2. CAPA DE INTERFAZ GRÁFICA (UI)
# ==========================================
class UiFacturacion(QMainWindow):
    def __init__(self, db_service: FacturacionService):
        super().__init__()
        self.db_service = db_service
        self.total_visual = 0.0

        self.setWindowTitle("Frankie Gestor - Nueva Factura")
        self.resize(700, 500)
        self._configurar_ui()

    # --- MÉTODOS DE CONFIGURACIÓN VISUAL ---
    def _configurar_ui(self):
        widget_central = QWidget()
        layout_principal = QVBoxLayout(widget_central)

        layout_principal.addLayout(self._crear_encabezado())
        layout_principal.addLayout(self._crear_panel_ingreso())
        
        self.tabla_detalles = self._crear_tabla()
        layout_principal.addWidget(self.tabla_detalles)
        
        layout_principal.addLayout(self._crear_pie())

        self.setCentralWidget(widget_central)

    def _crear_encabezado(self):
        layout = QHBoxLayout()
        self.txt_id_cliente = QLineEdit(placeholderText="ID Cliente")
        self.txt_id_vendedor = QLineEdit(placeholderText="ID Vendedor")
        
        layout.addWidget(QLabel("Cliente (ID):"))
        layout.addWidget(self.txt_id_cliente)
        layout.addWidget(QLabel("Vendedor (ID):"))
        layout.addWidget(self.txt_id_vendedor)
        return layout

    def _crear_panel_ingreso(self):
        layout = QHBoxLayout()
        self.txt_id_producto = QLineEdit(placeholderText="ID Producto")
        self.txt_cantidad = QLineEdit(placeholderText="Cantidad")
        self.txt_precio = QLineEdit(placeholderText="Precio Unitario")
        self.txt_descuento = QLineEdit(placeholderText="% Desc (Ej: 10)")
        
        btn_agregar = QPushButton("Agregar a Lista")
        btn_agregar.clicked.connect(self.agregar_producto)

        layout.addWidget(self.txt_id_producto)
        layout.addWidget(self.txt_cantidad)
        layout.addWidget(self.txt_precio)
        layout.addWidget(self.txt_descuento)
        layout.addWidget(btn_agregar)
        return layout

    def _crear_tabla(self):
        tabla = QTableWidget(0, 5)
        tabla.setHorizontalHeaderLabels(["ID Prod.", "Cantidad", "Precio U.", "% Desc.", "Subtotal"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return tabla

    def _crear_pie(self):
        layout = QHBoxLayout()
        self.lbl_total = QLabel("Total Estimado: $0.00")
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: blue;")
        
        btn_guardar = QPushButton("CONFIRMAR Y GUARDAR FACTURA")
        btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        btn_guardar.clicked.connect(self.procesar_guardado)

        layout.addStretch()
        layout.addWidget(self.lbl_total)
        layout.addWidget(btn_guardar)
        return layout

    # --- LÓGICA DE INTERACCIÓN ---
    def agregar_producto(self):
        """Valida y agrega visualmente el ítem a la tabla."""
        id_producto = self.txt_id_producto.text().strip()
        
        if not id_producto:
            QMessageBox.warning(self, "Error", "Debe ingresar el ID del producto.")
            return

        try:
            cantidad = int(self.txt_cantidad.text())
            precio = float(self.txt_precio.text())
            descuento = float(self.txt_descuento.text() or 0.0)
        except ValueError:
            QMessageBox.warning(self, "Error de formato", "Cantidad debe ser entero. Precio y Descuento numéricos.")
            return

        subtotal = (cantidad * precio) * (1 - (descuento / 100.0))
        self.total_visual += subtotal

        # Insertar en tabla
        fila = self.tabla_detalles.rowCount()
        self.tabla_detalles.insertRow(fila)
        datos_fila = [id_producto, str(cantidad), str(precio), str(descuento), f"{subtotal:.2f}"]
        
        for col, texto in enumerate(datos_fila):
            self.tabla_detalles.setItem(fila, col, QTableWidgetItem(texto))

        # Actualizar UI
        self.lbl_total.setText(f"Total Estimado: ${self.total_visual:.2f}")
        for txt in (self.txt_id_producto, self.txt_cantidad, self.txt_precio, self.txt_descuento):
            txt.clear()
        self.txt_id_producto.setFocus()

    def procesar_guardado(self):
        """Recolecta los datos de la UI y los envía al servicio de Base de Datos."""
        id_cliente = self.txt_id_cliente.text().strip()
        id_vendedor = self.txt_id_vendedor.text().strip()

        if not id_cliente or not id_vendedor:
            QMessageBox.warning(self, "Faltan datos", "Debe ingresar el ID del Cliente y del Vendedor.")
            return
            
        if self.tabla_detalles.rowCount() == 0:
            QMessageBox.warning(self, "Factura vacía", "Debe agregar al menos un producto.")
            return

        # Recolectar detalles de la tabla a una lista de diccionarios
        detalles = []
        for i in range(self.tabla_detalles.rowCount()):
            detalles.append({
                'id_producto': int(self.tabla_detalles.item(i, 0).text()),
                'cantidad': int(self.tabla_detalles.item(i, 1).text()),
                'precio': float(self.tabla_detalles.item(i, 2).text()),
                'descuento': float(self.tabla_detalles.item(i, 3).text())
            })

        # Llamar al servicio para guardar
        try:
            id_factura = self.db_service.guardar_factura(int(id_cliente), int(id_vendedor), detalles)
            QMessageBox.information(self, "Éxito", f"Factura {id_factura} guardada correctamente.")
            self._limpiar_todo()
            
        except sqlite3.IntegrityError as e:
            QMessageBox.critical(self, "Error de Integridad", f"Revise que los IDs existan:\n{str(e)}")
        except sqlite3.DatabaseError as e:
            QMessageBox.critical(self, "Error en Base de Datos", f"Operación cancelada por la BD:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", str(e))

    def _limpiar_todo(self):
        self.txt_id_cliente.clear()
        self.tabla_detalles.setRowCount(0)
        self.total_visual = 0.0
        self.lbl_total.setText("Total Estimado: $0.00")

# ==========================================
# 3. PUNTO DE ENTRADA (MAIN)
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Inyectamos el servicio en la UI
    servicio_bd = FacturacionService("frankie_gestor.db")
    ventana = UiFacturacion(servicio_bd)
    
    ventana.show()
    sys.exit(app.exec())