"""
===============================================================================
MÓDULO DE VISTAS: FACTURACIÓN Y VENTAS (src/vistas/ui_facturacion.py)
===============================================================================
Interfaz gráfica para la emisión de comprobantes de venta, selección de clientes,
incorporación de ítems de stock al detalle y registro transaccional.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from dominio.entidades_ventas import Cliente, Factura, DetalleFactura
from dominio.entidades_stock import Producto
from infraestructura.repo_ventas import RepositorioVentas
from infraestructura.repo_stock import RepositorioStock


class InterfazFacturacion(ttk.Frame):
    """
    Vista modular para la gestión comercial, selección de productos y facturación.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=15, pady=15)

        self.detalles_actuales: List[DetalleFactura] = []
        self.productos_disponibles: List[Producto] = []

        self._crear_widgets()
        self.cargar_datos_iniciales()

    def _crear_widgets(self):
        # 1. Título de la Sección
        lbl_titulo = ttk.Label(self, text="Módulo de Facturación y Ventas", style="Subtitulo.TLabel")
        lbl_titulo.pack(anchor="w", pady=(0, 15))

        # Contenedor Principal dividido en dos columnas
        contenedor = ttk.Frame(self)
        contenedor.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # PANEL IZQUIERDO: Datos de Cabecera e Ítems
        # -------------------------------------------------------------
        frame_izq = ttk.Frame(contenedor)
        frame_izq.pack(side="left", fill="both", padx=(0, 15), expand=False)

        # Datos del Cliente / Venta
        frame_cabecera = ttk.LabelFrame(frame_izq, text=" Datos del Comprobante ", padding=12)
        frame_cabecera.pack(fill="x", pady=(0, 10))

        ttk.Label(frame_cabecera, text="ID Cliente:").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_id_cliente = ttk.Entry(frame_cabecera, width=15)
        self.entry_id_cliente.grid(row=0, column=1, sticky="w", pady=4, padx=(5, 10))
        self.entry_id_cliente.insert(0, "1")

        ttk.Label(frame_cabecera, text="ID Vendedor:").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_id_vendedor = ttk.Entry(frame_cabecera, width=15)
        self.entry_id_vendedor.grid(row=1, column=1, sticky="w", pady=4, padx=(5, 10))
        self.entry_id_vendedor.insert(0, "1")

        # Agregar Ítems al Detalle
        frame_item = ttk.LabelFrame(frame_izq, text=" Agregar Producto al Detalle ", padding=12)
        frame_item.pack(fill="x", pady=(0, 10))

        ttk.Label(frame_item, text="Producto:").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_productos = ttk.Combobox(frame_item, state="readonly", width=30)
        self.combo_productos.grid(row=0, column=1, sticky="w", pady=4, padx=(5, 0))
        self.combo_productos.bind("<<ComboboxSelected>>", self._al_seleccionar_producto)

        ttk.Label(frame_item, text="Cantidad:").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_cantidad = ttk.Entry(frame_item, width=15)
        self.entry_cantidad.grid(row=1, column=1, sticky="w", pady=4, padx=(5, 0))
        self.entry_cantidad.insert(0, "1")

        ttk.Label(frame_item, text="Desc. (%):").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_descuento = ttk.Entry(frame_item, width=15)
        self.entry_descuento.grid(row=2, column=1, sticky="w", pady=4, padx=(5, 0))
        self.entry_descuento.insert(0, "0.0")

        btn_agregar = ttk.Button(frame_item, text="Agregar Ítem", command=self.agregar_detalle)
        btn_agregar.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # -------------------------------------------------------------
        # PANEL DERECHO: Grilla de Detalles y Totales
        # -------------------------------------------------------------
        frame_der = ttk.Frame(contenedor)
        frame_der.pack(side="right", fill="both", expand=True)

        frame_tabla = ttk.LabelFrame(frame_der, text=" Detalle de Factura ", padding=10)
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))

        columnas = ("id_prod", "descripcion", "cantidad", "precio_unit", "descuento", "subtotal")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id_prod", text="ID Prod")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("cantidad", text="Cant.")
        self.tree.heading("precio_unit", text="Precio Unit.")
        self.tree.heading("descuento", text="Desc. %")
        self.tree.heading("subtotal", text="Subtotal")

        self.tree.column("id_prod", width=60, anchor="center")
        self.tree.column("descripcion", width=180, anchor="w")
        self.tree.column("cantidad", width=60, anchor="center")
        self.tree.column("precio_unit", width=90, anchor="e")
        self.tree.column("descuento", width=70, anchor="center")
        self.tree.column("subtotal", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Pie de Factura / Totales y Botón de Emisión
        frame_pie = ttk.Frame(frame_der)
        frame_pie.pack(fill="x", pady=5)

        self.lbl_total = ttk.Label(frame_pie, text="TOTAL A PAGAR: $0.00", style="Subtitulo.TLabel")
        self.lbl_total.pack(side="left", padx=5)

        btn_emitir = ttk.Button(frame_pie, text="Emitir Factura", command=self.emitir_factura)
        btn_emitir.pack(side="right", padx=5)

        btn_limpiar = ttk.Button(frame_pie, text="Limpiar", command=self.limpiar_factura)
        btn_limpiar.pack(side="right", padx=5)

    def cargar_datos_iniciales(self):
        """Carga el catálogo de productos disponibles para la venta desde el inventario."""
        try:
            self.productos_disponibles = RepositorioStock.listar_productos()
            nombres_productos = [f"[{p.codigo}] {p.descripcion} (${p.precio_venta:,.2f})" for p in self.productos_disponibles]
            self.combo_productos["values"] = nombres_productos
            if nombres_productos:
                self.combo_productos.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los productos: {e}")

    def _al_seleccionar_producto(self, _event):
        """Acción al seleccionar un producto del desplegable."""
        pass

    def agregar_detalle(self):
        """Agrega un renglón de detalle a la factura actual."""
        seleccion_idx = self.combo_productos.current()
        if seleccion_idx < 0 or seleccion_idx >= len(self.productos_disponibles):
            messagebox.showwarning("Selección inválida", "Debe seleccionar un producto válido.")
            return

        prod = self.productos_disponibles[seleccion_idx]

        try:
            cantidad = int(self.entry_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "La cantidad debe ser un número entero mayor a cero.")
            return

        try:
            descuento = float(self.entry_descuento.get().strip())
            if not (0 <= descuento <= 100):
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "El porcentaje de descuento debe estar entre 0 y 100.")
            return

        precio_unit = float(prod.precio_venta)
        subtotal = cantidad * precio_unit * (1.0 - descuento / 100.0)

        detalle = DetalleFactura(
            id_producto=prod.id if prod.id is not None else 0,
            cantidad=cantidad,
            precio_unitario=precio_unit,
            descuento_porcentaje=descuento,
            subtotal=subtotal
        )

        self.detalles_actuales.append(detalle)
        self.actualizar_tabla_detalles()

    def actualizar_tabla_detalles(self):
        """Refresca la grilla de ítems y calcula el total general."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_general = 0.0

        for det in self.detalles_actuales:
            prod_desc = f"Producto ID {det.id_producto}"
            for p in self.productos_disponibles:
                if p.id == det.id_producto:
                    prod_desc = p.descripcion
                    break

            self.tree.insert(
                "",
                "end",
                values=(
                    det.id_producto,
                    prod_desc,
                    det.cantidad,
                    f"${det.precio_unitario:,.2f}",
                    f"{det.descuento_porcentaje:.1f}%",
                    f"${det.subtotal:,.2f}"
                )
            )
            total_general += det.subtotal

        self.lbl_total.config(text=f"TOTAL A PAGAR: ${total_general:,.2f}")

    def emitir_factura(self):
        """Persiste la factura mediante el repositorio de ventas y procesa el descuento de stock."""
        if not self.detalles_actuales:
            messagebox.showwarning("Sin ítems", "La factura debe contener al menos un producto en el detalle.")
            return

        try:
            id_cliente = int(self.entry_id_cliente.get().strip())
            id_vendedor = int(self.entry_id_vendedor.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El ID de cliente y vendedor deben ser numéricos.")
            return

        cliente_obj = RepositorioVentas.obtener_cliente_por_id(id_cliente)
        if not cliente_obj:
            cliente_obj = Cliente(nombres="Consumidor", apellidos="Final", id_cliente=id_cliente)

        total_fac = sum(d.subtotal for d in self.detalles_actuales)

        factura = Factura(
            id_factura=None,
            cliente=cliente_obj,
            id_vendedor=id_vendedor,
            total=total_fac,
            detalles=self.detalles_actuales
        )

        try:
            factura_guardada = RepositorioVentas.guardar_factura(factura)
            messagebox.showinfo("Éxito", f"¡Factura #{factura_guardada.id_factura} emitida correctamente!\nTotal: ${factura_guardada.total:,.2f}")
            self.limpiar_factura()
            self.cargar_datos_iniciales()
        except Exception as e:
            messagebox.showerror("Error al Emitir", f"No se pudo guardar la factura: {e}")

    def limpiar_factura(self):
        """Reinicia el formulario de facturación."""
        self.detalles_actuales = []
        self.actualizar_tabla_detalles()
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, "1")
        self.entry_descuento.delete(0, tk.END)
        self.entry_descuento.insert(0, "0.0")