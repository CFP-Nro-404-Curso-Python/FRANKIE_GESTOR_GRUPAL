"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: CAPA DE PRESENTACIÓN DE VENTAS (vistas/ui_facturacion.py)
===============================================================================
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

DIR_ACTUAL = Path(__file__).resolve().parent
RAIZ_PROYECTO = DIR_ACTUAL.parent

for path in (DIR_ACTUAL, RAIZ_PROYECTO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from controladores.orquestador_ventas import OrquestadorVentas
from vistas.ui_estilos import COLOR_TEXTO_MUTED


class InterfazFacturacion(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.orquestador = OrquestadorVentas()
        self.items_pantalla: List[Dict] = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

        self._crear_encabezado()
        self._crear_panel_formulario()
        self._crear_panel_tabla()

    def _crear_encabezado(self):
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        ttk.Label(frame_top, text="Módulo de Facturación y Ventas", style="Subtitulo.TLabel").pack(anchor="w")
        ttk.Label(frame_top, text="Emisión de comprobantes y detalle de ventas", foreground=COLOR_TEXTO_MUTED).pack(anchor="w")

    def _crear_panel_formulario(self):
        self.frame_form = ttk.LabelFrame(self, text=" Datos de la Transacción ")
        self.frame_form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_form.columnconfigure((1, 3, 5, 7), weight=1)

        ttk.Label(self.frame_form, text="ID Cliente:").grid(row=0, column=0, padx=10, pady=4, sticky="w")
        self.txt_id_cliente = ttk.Entry(self.frame_form)
        self.txt_id_cliente.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="ID Vendedor:").grid(row=0, column=2, padx=10, pady=4, sticky="w")
        self.txt_id_vendedor = ttk.Entry(self.frame_form)
        self.txt_id_vendedor.grid(row=0, column=3, padx=10, pady=4, sticky="ew")

        self.var_iva = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.frame_form, text="Aplicar IVA (21%)", variable=self.var_iva, command=self._recalcular_vista).grid(row=0, column=4, columnspan=2, padx=10, pady=4, sticky="w")

        ttk.Label(self.frame_form, text="ID Producto:").grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.txt_id_producto = ttk.Entry(self.frame_form)
        self.txt_id_producto.grid(row=1, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Cantidad:").grid(row=1, column=2, padx=10, pady=4, sticky="w")
        self.txt_cantidad = ttk.Entry(self.frame_form)
        self.txt_cantidad.grid(row=1, column=3, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Precio U. ($):").grid(row=1, column=4, padx=10, pady=4, sticky="w")
        self.txt_precio = ttk.Entry(self.frame_form)
        self.txt_precio.grid(row=1, column=5, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="% Desc:").grid(row=1, column=6, padx=10, pady=4, sticky="w")
        self.txt_descuento = ttk.Entry(self.frame_form)
        self.txt_descuento.grid(row=1, column=7, padx=10, pady=4, sticky="ew")

        frame_botones = ttk.Frame(self.frame_form)
        frame_botones.grid(row=2, column=0, columnspan=8, pady=10, sticky="w")

        ttk.Button(frame_botones, text="Agregar Ítem", command=self._agregar_item).pack(side="left", padx=(10, 5))
        ttk.Button(frame_botones, text="Limpiar Formulario", command=self._limpiar_todo).pack(side="left", padx=5)

    def _crear_panel_tabla(self):
        frame_tabla = ttk.LabelFrame(self, text=" Detalle de la Factura ")
        frame_tabla.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id_prod", "cant", "precio", "desc", "subtotal")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=6)

        self.tabla.heading("id_prod", text="ID Producto")
        self.tabla.heading("cant", text="Cantidad")
        self.tabla.heading("precio", text="Precio U.")
        self.tabla.heading("desc", text="% Descuento")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("id_prod", width=100, anchor="center")
        self.tabla.column("cant", width=80, anchor="center")
        self.tabla.column("precio", width=110, anchor="e")
        self.tabla.column("desc", width=90, anchor="center")
        self.tabla.column("subtotal", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="nsew")
        scrollbar.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ns")

        frame_pie = ttk.Frame(frame_tabla)
        frame_pie.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.lbl_desglose = ttk.Label(frame_pie, text="Neto: $ 0.00 | IVA: $ 0.00 | TOTAL: $ 0.00", font=("Arial", 10, "bold"))
        self.lbl_desglose.pack(side="left", padx=10)

        ttk.Button(frame_pie, text="EMITIR FACTURA", command=self._emitir_factura).pack(side="right", padx=10)

    def _agregar_item(self):
        try:
            id_prod = int(self.txt_id_producto.get().strip())
            cant = int(self.txt_cantidad.get().strip())
            precio = float(self.txt_precio.get().strip())
            desc = float(self.txt_descuento.get().strip() or 0.0)
        except ValueError:
            messagebox.showwarning("Atención", "Verifique que los valores ingresados sean numéricos.")
            return

        subtotal_item = self.orquestador.calcular_renglon(cant, precio, desc)
        self.items_pantalla.append({
            "id_producto": id_prod,
            "cantidad": cant,
            "precio_unitario": precio,
            "descuento": desc,
            "subtotal": subtotal_item
        })

        self.tabla.insert("", "end", values=(id_prod, cant, f"$ {precio:,.2f}", f"{desc:.1f}%", f"$ {subtotal_item:,.2f}"))
        self._recalcular_vista()
        self._limpiar_inputs_item()

    def _recalcular_vista(self):
        from dominio.entidades_ventas import DetalleFactura
        detalles_tmp = [
            DetalleFactura(it["id_producto"], it["cantidad"], it["precio_unitario"], it["descuento"], subtotal=it["subtotal"])
            for it in self.items_pantalla
        ]
        subtotal_base, monto_iva, total = self.orquestador.calcular_totales_factura(detalles_tmp, aplicar_iva=self.var_iva.get())
        self.lbl_desglose.configure(text=f"Neto: $ {subtotal_base:,.2f} | IVA: $ {monto_iva:,.2f} | TOTAL: $ {total:,.2f}")

    def _limpiar_inputs_item(self):
        self.txt_id_producto.delete(0, "end")
        self.txt_cantidad.delete(0, "end")
        self.txt_precio.delete(0, "end")
        self.txt_descuento.delete(0, "end")
        self.txt_id_producto.focus()

    def _limpiar_todo(self):
        self.txt_id_cliente.delete(0, "end")
        self.txt_id_vendedor.delete(0, "end")
        self._limpiar_inputs_item()
        self.items_pantalla.clear()
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        self._recalcular_vista()

    def _emitir_factura(self):
        try:
            id_cli = int(self.txt_id_cliente.get().strip())
            id_vend = int(self.txt_id_vendedor.get().strip())
        except ValueError:
            messagebox.showwarning("Atención", "ID Cliente e ID Vendedor deben ser enteros.")
            return

        if not self.items_pantalla:
            messagebox.showwarning("Atención", "Agregue al menos un ítem a la factura.")
            return

        try:
            factura_emitida = self.orquestador.emitir_factura(
                id_cliente=id_cli,
                id_vendedor=id_vend,
                items_raw=self.items_pantalla,
                aplicar_iva=self.var_iva.get()
            )
            messagebox.showinfo("Éxito", f"Factura #{factura_emitida.id_factura} emitida correctamente.\nTotal: $ {factura_emitida.total:,.2f}")
            self._limpiar_todo()
        except ValueError as err:
            messagebox.showerror("Error de Validación", str(err))
        except Exception as err:
            messagebox.showerror("Error Inesperado", str(err))
