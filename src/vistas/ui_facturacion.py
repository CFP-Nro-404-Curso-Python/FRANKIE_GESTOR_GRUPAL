import tkinter as tk
from tkinter import ttk, messagebox


class UiFacturacion(ttk.Frame):
    """
    Vista de Facturación integrada al Panel Principal de Tkinter.
    Hereda de ttk.Frame para insertarse dinámicamente en el contenedor central.
    """
    def __init__(self, parent, repo_ventas):
        super().__init__(parent)
        self.repo_ventas = repo_ventas
        self.detalles_temporales = []
        self.total_visual = 0.0

        self._configurar_ui()

    def _configurar_ui(self):
        # Configurar expansión del frame principal
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- 1. ENCABEZADO (Cliente y Vendedor) ---
        frame_encabezado = ttk.LabelFrame(self, text="Datos de la Factura", padding=10)
        frame_encabezado.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(frame_encabezado, text="ID Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.txt_id_cliente = ttk.Entry(frame_encabezado, width=15)
        self.txt_id_cliente.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_encabezado, text="ID Vendedor:").grid(row=0, column=2, padx=5, pady=5)
        self.txt_id_vendedor = ttk.Entry(frame_encabezado, width=15)
        self.txt_id_vendedor.grid(row=0, column=3, padx=5, pady=5)

        # --- 2. PANEL DE INGRESO (Productos) ---
        frame_inputs = ttk.LabelFrame(self, text="Agregar Ítem", padding=10)
        frame_inputs.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(frame_inputs, text="ID Prod:").grid(row=0, column=0, padx=2)
        self.txt_id_producto = ttk.Entry(frame_inputs, width=10)
        self.txt_id_producto.grid(row=0, column=1, padx=4)

        ttk.Label(frame_inputs, text="Cant:").grid(row=0, column=2, padx=2)
        self.txt_cantidad = ttk.Entry(frame_inputs, width=8)
        self.txt_cantidad.grid(row=0, column=3, padx=4)

        ttk.Label(frame_inputs, text="Precio U:").grid(row=0, column=4, padx=2)
        self.txt_precio = ttk.Entry(frame_inputs, width=10)
        self.txt_precio.grid(row=0, column=5, padx=4)

        ttk.Label(frame_inputs, text="% Desc:").grid(row=0, column=6, padx=2)
        self.txt_descuento = ttk.Entry(frame_inputs, width=8)
        self.txt_descuento.grid(row=0, column=7, padx=4)

        btn_agregar = ttk.Button(frame_inputs, text="Agregar a Lista", command=self.agregar_producto)
        btn_agregar.grid(row=0, column=8, padx=8)

        # --- 3. TABLA DE DETALLES (Treeview) ---
        frame_tabla = ttk.Frame(self, padding=10)
        frame_tabla.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id_prod", "cant", "precio", "desc", "subtotal")
        self.tabla_detalles = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        self.tabla_detalles.heading("id_prod", text="ID Producto")
        self.tabla_detalles.heading("cant", text="Cantidad")
        self.tabla_detalles.heading("precio", text="Precio U.")
        self.tabla_detalles.heading("desc", text="% Desc.")
        self.tabla_detalles.heading("subtotal", text="Subtotal")

        self.tabla_detalles.column("id_prod", anchor="center", width=100)
        self.tabla_detalles.column("cant", anchor="center", width=80)
        self.tabla_detalles.column("precio", anchor="e", width=100)
        self.tabla_detalles.column("desc", anchor="center", width=80)
        self.tabla_detalles.column("subtotal", anchor="e", width=120)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_detalles.yview)
        self.tabla_detalles.configure(yscrollcommand=scrollbar.set)

        self.tabla_detalles.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- 4. PIE (Total y Confirmación) ---
        frame_pie = ttk.Frame(self, padding=10)
        frame_pie.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.lbl_total = ttk.Label(frame_pie, text="Total Estimado: $0.00", font=("Arial", 12, "bold"))
        self.lbl_total.pack(side="left")

        btn_guardar = ttk.Button(frame_pie, text="CONFIRMAR Y GUARDAR FACTURA", command=self.procesar_guardado)
        btn_guardar.pack(side="right")

    # --- LÓGICA DE INTERFAZ ---
    def agregar_producto(self):
        id_prod = self.txt_id_producto.get().strip()
        if not id_prod:
            messagebox.showwarning("Error", "Debe ingresar el ID del producto.")
            return

        try:
            cant = int(self.txt_cantidad.get().strip())
            precio = float(self.txt_precio.get().strip())
            desc = float(self.txt_descuento.get().strip() or 0.0)
        except ValueError:
            messagebox.showwarning("Error de Formato", "Cantidad debe ser entero. Precio y Descuento numéricos.")
            return

        subtotal = (cant * precio) * (1 - (desc / 100.0))
        self.total_visual += subtotal

        # Guardar en memoria temporal de la UI
        item_detalle = {
            'id_producto': int(id_prod),
            'cantidad': cant,
            'precio': precio,
            'descuento': desc
        }
        self.detalles_temporales.append(item_detalle)

        # Insertar en la tabla de Tkinter
        self.tabla_detalles.insert("", "end", values=(id_prod, cant, f"${precio:.2f}", f"{desc}%", f"${subtotal:.2f}"))

        self.lbl_total.config(text=f"Total Estimado: ${self.total_visual:.2f}")
        self._limpiar_inputs()

    def procesar_guardado(self):
        id_cliente = self.txt_id_cliente.get().strip()
        id_vendedor = self.txt_id_vendedor.get().strip()

        if not id_cliente or not id_vendedor:
            messagebox.showwarning("Faltan Datos", "Debe ingresar el ID del Cliente y del Vendedor.")
            return

        if not self.detalles_temporales:
            messagebox.showwarning("Factura Vacía", "Debe agregar al menos un producto a la lista.")
            return

        # Llamada al Repositorio (Infraestructura)
        try:
            id_factura = self.repo_ventas.guardar_factura(
                id_cliente=int(id_cliente),
                id_vendedor=int(id_vendedor),
                detalles=self.detalles_temporales
            )
            messagebox.showinfo("Éxito", f"Factura #{id_factura} guardada correctamente.")
            self._limpiar_todo()

        except ValueError as e:
            messagebox.showwarning("Atención", str(e))
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"No se pudo guardar la factura:\n{str(e)}")

    def _limpiar_inputs(self):
        self.txt_id_producto.delete(0, tk.END)
        self.txt_cantidad.delete(0, tk.END)
        self.txt_precio.delete(0, tk.END)
        self.txt_descuento.delete(0, tk.END)
        self.txt_id_producto.focus()

    def _limpiar_todo(self):
        self.txt_id_cliente.delete(0, tk.END)
        self.txt_id_vendedor.delete(0, tk.END)
        self._limpiar_inputs()
        self.detalles_temporales.clear()
        self.total_visual = 0.0
        self.lbl_total.config(text="Total Estimado: $0.00")
        for fila in self.tabla_detalles.get_children():
            self.tabla_detalles.delete(fila)
