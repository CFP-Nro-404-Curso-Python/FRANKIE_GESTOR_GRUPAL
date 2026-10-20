import tkinter as tk
from tkinter import messagebox, ttk

from infraestructura.repo_ventas import (
    guardar_factura,
    obtener_clientes,
    obtener_productos_disponibles,
)


class PantallaFacturacion(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.detalles = []  # Ítems acumulados en la factura actual

        self.crear_widgets()
        self.cargar_datos_iniciales()

    def crear_widgets(self):
        # Título del módulo
        tk.Label(
            self, text="Módulo de Facturación", font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Panel Datos del Cliente
        frame_cliente = tk.LabelFrame(
            self, text=" Datos del Cliente ", padx=10, pady=10
        )
        frame_cliente.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_cliente, text="Seleccionar Cliente:").grid(
            row=0, column=0, sticky="w"
        )
        self.combo_clientes = ttk.Combobox(
            frame_cliente, state="readonly", width=45
        )
        self.combo_clientes.grid(row=0, column=1, padx=5)

        # Panel Agregar Productos
        frame_prod = tk.LabelFrame(
            self, text=" Agregar Productos ", padx=10, pady=10
        )
        frame_prod.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_prod, text="Producto:").grid(row=0, column=0, sticky="w")
        self.combo_productos = ttk.Combobox(
            frame_prod, state="readonly", width=30
        )
        self.combo_productos.grid(row=0, column=1, padx=5)

        tk.Label(frame_prod, text="Cantidad:").grid(row=0, column=2, sticky="w")
        self.entry_cantidad = tk.Entry(frame_prod, width=8)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.grid(row=0, column=3, padx=5)

        btn_agregar = tk.Button(
            frame_prod,
            text="Agregar a Lista",
            bg="#007bff",
            fg="white",
            command=self.agregar_producto,
        )
        btn_agregar.grid(row=0, column=4, padx=10)

        # Tabla de Detalles (Treeview)
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("prod_id", "producto", "cantidad", "precio_u", "subtotal")
        self.tabla = ttk.Treeview(
            frame_tabla, columns=columns, show="headings", height=8
        )

        self.tabla.heading("prod_id", text="ID")
        self.tabla.heading("producto", text="Producto")
        self.tabla.heading("cantidad", text="Cant.")
        self.tabla.heading("precio_u", text="Precio U.")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("prod_id", anchor="center", width=60)
        self.tabla.column("producto", anchor="w", width=220)
        self.tabla.column("cantidad", anchor="center", width=70)
        self.tabla.column("precio_u", anchor="e", width=100)
        self.tabla.column("subtotal", anchor="e", width=110)

        scrollbar = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tabla.yview
        )
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Pie con Total y Botón de Confirmación
        frame_inferior = tk.Frame(self, pady=10)
        frame_inferior.pack(fill="x", padx=15)

        self.lbl_total = tk.Label(
            frame_inferior,
            text="Total Estimado: $0.00",
            font=("Arial", 14, "bold"),
        )
        self.lbl_total.pack(side="left")

        btn_emitir = tk.Button(
            frame_inferior,
            text="CONFIRMAR Y GUARDAR FACTURA",
            bg="#28a745",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.emitir_factura,
        )
        btn_emitir.pack(side="right")

    def cargar_datos_iniciales(self):
        try:
            self.dict_clientes = {}
            clientes = obtener_clientes()
            lista_cli = []
            for c in clientes:
                fmt = f"{c['nombre']} {c['apellido']} (CUIT: {c['cuit']})"
                self.dict_clientes[fmt] = c["id"]
                lista_cli.append(fmt)
            self.combo_clientes["values"] = lista_cli

            self.dict_productos = {}
            productos = obtener_productos_disponibles()
            lista_prod = []
            for p in productos:
                fmt = f"{p['nombre']} - ${p['precio']:.2f}"
                self.dict_productos[fmt] = p
                lista_prod.append(fmt)
            self.combo_productos["values"] = lista_prod
        except Exception as e:
            messagebox.showerror(
                "Error de Carga",
                f"No se pudieron cargar los datos iniciales:\n{str(e)}",
            )

    def agregar_producto(self):
        prod_sel = self.combo_productos.get()
        cant_str = self.entry_cantidad.get().strip()

        if not prod_sel:
            messagebox.showwarning("Atención", "Debe seleccionar un producto.")
            return

        if not cant_str.isdigit() or int(cant_str) <= 0:
            messagebox.showwarning(
                "Atención", "La cantidad debe ser un entero mayor a cero."
            )
            return

        cant = int(cant_str)
        prod = self.dict_productos[prod_sel]
        subtotal = prod["precio"] * cant

        item = {
            "id_producto": prod["id"],
            "nombre": prod["nombre"],
            "cantidad": cant,
            "precio_unitario": prod["precio"],
            "subtotal": subtotal,
        }

        self.detalles.append(item)
        self.tabla.insert(
            "",
            "end",
            values=(
                item["id_producto"],
                item["nombre"],
                item["cantidad"],
                f"${item['precio_unitario']:.2f}",
                f"${subtotal:.2f}",
            ),
        )
        self.actualizar_total()

    def actualizar_total(self):
        total = sum(i["subtotal"] for i in self.detalles)
        self.lbl_total.config(text=f"Total Estimado: ${total:.2f}")

    def emitir_factura(self):
        cli_sel = self.combo_clientes.get()
        if not cli_sel:
            messagebox.showwarning("Atención", "Debe seleccionar un cliente.")
            return
        if not self.detalles:
            messagebox.showwarning(
                "Atención", "Debe agregar al menos un producto a la lista."
            )
            return

        id_cliente = self.dict_clientes[cli_sel]
        total = sum(i["subtotal"] for i in self.detalles)

        try:
            id_factura = guardar_factura(id_cliente, total, self.detalles)
            if id_factura:
                messagebox.showinfo(
                    "Éxito", f"Factura #{id_factura} emitida correctamente."
                )
                self.limpiar_formulario()
            else:
                messagebox.showerror(
                    "Error", "Ocurrió un error al guardar la factura."
                )
        except Exception as e:
            messagebox.showerror(
                "Error de Sistema", f"Falló el guardado:\n{str(e)}"
            )

    def limpiar_formulario(self):
        self.detalles.clear()
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        self.actualizar_total()
        self.combo_clientes.set("")
        self.combo_productos.set("")
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")
