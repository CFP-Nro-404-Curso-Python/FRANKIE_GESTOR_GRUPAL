"""
===============================================================================
MÓDULO DE VISTAS: INTERFAZ DE INVENTARIO Y STOCK (src/vistas/ui_inventario.py)
===============================================================================
Gestión de productos, control de stock mínimo (75), cálculo de precio de venta
y emisión de Órdenes de Compra con datos seguros y validados.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import webbrowser
from pathlib import Path

from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_stock import Producto


class InterfazInventario(ttk.Frame):
    """
    Panel de control y gestión del inventario físico y catálogo de productos.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.producto_seleccionado_id = None
        self.producto_estado_activo = True
        self.productos_cache = {}
        self.proveedores_map = {}

        self.var_codigo = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_proveedor_sel = tk.StringVar()
        self.var_stock = tk.StringVar(value="0")
        self.var_stock_minimo = tk.StringVar(value="75")
        self.var_costo = tk.StringVar(value="0.00")
        self.var_venta = tk.StringVar(value="0.00")
        self.var_ubicacion = tk.StringVar()

        self.var_busqueda = tk.StringVar()
        self.var_solo_alertas = tk.BooleanVar(value=False)
        self.var_mostrar_inactivos = tk.BooleanVar(value=False)

        self._construir_interfaz()
        self.cargar_proveedores_combo()
        self.cargar_tabla_productos()

    def _construir_interfaz(self):
        frame_form = ttk.LabelFrame(self, text=" Gestión de Artículos / Inventario ", padding=12)
        frame_form.pack(fill="x", padx=5, pady=5)

        lbl_aviso = ttk.Label(
            frame_form,
            text="💡 Nota: Stock mínimo predeterminado: 75 unidades. Alerta de reposición si stock ≤ 75. Precio venta = Costo + 20%.",
            font=("Arial", 9, "italic"),
            foreground="#2563EB"
        )
        lbl_aviso.grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 10))

        ttk.Label(frame_form, text="Código *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_codigo, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(frame_form, text="Descripción *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_descripcion, width=32).grid(row=1, column=3, sticky="ew", padx=5,
                                                                                pady=4)

        ttk.Label(frame_form, text="Categoría:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_categoria, width=20).grid(row=2, column=1, sticky="w", padx=5,
                                                                              pady=4)

        ttk.Label(frame_form, text="Proveedor *:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.combo_proveedores = ttk.Combobox(frame_form, textvariable=self.var_proveedor_sel, state="readonly",
                                              width=30)
        self.combo_proveedores.grid(row=2, column=3, sticky="ew", padx=5, pady=4)

        ttk.Label(frame_form, text="Stock Actual:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_stock, width=15).grid(row=3, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(frame_form, text="Stock Mínimo (75):").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_stock_minimo, width=15).grid(row=3, column=3, sticky="w", padx=5,
                                                                                 pady=4)

        ttk.Label(frame_form, text="Precio Costo ($) *:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        ent_costo = ttk.Entry(frame_form, textvariable=self.var_costo, width=15)
        ent_costo.grid(row=4, column=1, sticky="w", padx=5, pady=4)
        ent_costo.bind("<KeyRelease>", self._calcular_precio_venta_auto)

        ttk.Label(frame_form, text="Precio Venta ($) (+20%):").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_venta, width=15).grid(row=4, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(frame_form, text="Ubicación / Depósito:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(frame_form, textvariable=self.var_ubicacion, width=20).grid(row=5, column=1, sticky="w", padx=5,
                                                                              pady=4)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=6, column=0, columnspan=4, sticky="e", pady=12)

        ttk.Button(frame_botones, text="Limpiar / Nuevo", command=self.limpiar_formulario).pack(side="left", padx=5)

        self.btn_toggle_estado = ttk.Button(
            frame_botones,
            text="Deshabilitar",
            command=self.toggle_estado_producto,
            state="disabled"
        )
        self.btn_toggle_estado.pack(side="left", padx=5)

        self.btn_orden_compra = ttk.Button(
            frame_botones,
            text="📦 Emitir Orden de Compra",
            command=self.generar_orden_compra_seleccionado,
            state="disabled"
        )
        self.btn_orden_compra.pack(side="left", padx=5)

        self.btn_guardar = ttk.Button(frame_botones, text="Guardar Producto", command=self.guardar_producto)
        self.btn_guardar.pack(side="left", padx=5)

        frame_tabla = ttk.LabelFrame(self, text=" Catálogo de Productos y Alertas de Stock ", padding=12)
        frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        frame_filtros = ttk.Frame(frame_tabla)
        frame_filtros.pack(fill="x", pady=(0, 8))

        ttk.Label(frame_filtros, text="Filtrar:").pack(side="left", padx=(0, 5))
        entry_busq = ttk.Entry(frame_filtros, textvariable=self.var_busqueda, width=25)
        entry_busq.pack(side="left", padx=(0, 15))
        entry_busq.bind("<KeyRelease>", lambda _e: self.cargar_tabla_productos())

        chk_alertas = ttk.Checkbutton(
            frame_filtros,
            text="⚠️ Alertas Stock Crítico (≤ 75 u.)",
            variable=self.var_solo_alertas,
            command=self.cargar_tabla_productos
        )
        chk_alertas.pack(side="left", padx=10)

        chk_inact = ttk.Checkbutton(
            frame_filtros,
            text="Mostrar inactivos",
            variable=self.var_mostrar_inactivos,
            command=self.cargar_tabla_productos
        )
        chk_inact.pack(side="right")

        columnas = ("id", "codigo", "descripcion", "categoria", "proveedor", "stock", "minimo", "costo", "venta",
                    "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("proveedor", text="Proveedor")
        self.tabla.heading("stock", text="Stock")
        self.tabla.heading("minimo", text="Mín.")
        self.tabla.heading("costo", text="Costo ($)")
        self.tabla.heading("venta", text="Venta ($)")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=35, anchor="center")
        self.tabla.column("codigo", width=80, anchor="center")
        self.tabla.column("descripcion", width=160, anchor="w")
        self.tabla.column("categoria", width=90, anchor="w")
        self.tabla.column("proveedor", width=130, anchor="w")
        self.tabla.column("stock", width=60, anchor="center")
        self.tabla.column("minimo", width=55, anchor="center")
        self.tabla.column("costo", width=75, anchor="e")
        self.tabla.column("venta", width=75, anchor="e")
        self.tabla.column("estado", width=70, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tabla.pack(side="top", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def cargar_proveedores_combo(self):
        try:
            provs = RepositorioStock.listar_proveedores(incluir_inactivos=False)
            self.proveedores_map.clear()
            lista_nombres = []
            for p in provs:
                nombre_legible = f"{p.nombre_comercial} (ID: {p.id})"
                self.proveedores_map[nombre_legible] = p.id
                lista_nombres.append(nombre_legible)
            self.combo_proveedores['values'] = lista_nombres
            if lista_nombres:
                self.combo_proveedores.current(0)
        except Exception as e:
            print(f"[AVISO] No se pudieron cargar proveedores en inventario: {e}")

    def _calcular_precio_venta_auto(self, _event=None):
        try:
            costo_str = self.var_costo.get().strip().replace(",", ".")
            if not costo_str:
                self.var_venta.set("0.00")
                return
            costo = float(costo_str)
            venta = round(costo * 1.20, 2)
            self.var_venta.set(f"{venta:.2f}")
        except ValueError:
            pass

    def cargar_tabla_productos(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        self.productos_cache.clear()
        solo_alertas = self.var_solo_alertas.get()
        incluir_inactivos = self.var_mostrar_inactivos.get()

        try:
            productos = RepositorioStock.listar_productos(solo_alertas=False, incluir_inactivos=incluir_inactivos)
            criterio = self.var_busqueda.get().strip().lower()

            for prod in productos:
                if criterio and criterio not in prod.codigo.lower() and criterio not in prod.descripcion.lower():
                    continue

                # Filtro estricto por alerta si está marcado el checkbox
                if solo_alertas and prod.stock_actual > prod.stock_minimo:
                    continue

                self.productos_cache[str(prod.id)] = prod
                estado_str = "Activo" if getattr(prod, "activo", True) else "Inactivo"

                self.tabla.insert("", "end", values=(
                    prod.id,
                    prod.codigo,
                    prod.descripcion,
                    prod.categoria or "-",
                    prod.nombre_proveedor or "-",
                    prod.stock_actual,
                    prod.stock_minimo,
                    f"{prod.precio_costo:.2f}",
                    f"{prod.precio_venta:.2f}",
                    estado_str
                ))
        except Exception as e:
            print(f"[AVISO] No se pudo listar productos: {e}")

    def guardar_producto(self):
        codigo = self.var_codigo.get().strip()
        descripcion = self.var_descripcion.get().strip()
        prov_sel = self.var_proveedor_sel.get()

        if not codigo or not descripcion or not prov_sel:
            messagebox.showwarning("Campos Incompletos",
                                   "Por favor, complete Código, Descripción y seleccione un Proveedor.")
            return

        id_prov = self.proveedores_map.get(prov_sel)
        if not id_prov:
            messagebox.showerror("Error", "Proveedor no válido.")
            return

        try:
            stock = int(self.var_stock.get().strip() or 0)
            stock_min = int(self.var_stock_minimo.get().strip() or 75)
            costo = float(self.var_costo.get().strip().replace(",", ".") or 0.0)
            venta = float(self.var_venta.get().strip().replace(",", ".") or 0.0)
        except ValueError:
            messagebox.showerror("Formato Inválido", "Stock, Stock Mínimo, Costo y Venta deben ser numéricos.")
            return

        prod = Producto(
            id=self.producto_seleccionado_id,
            codigo=codigo,
            descripcion=descripcion,
            categoria=self.var_categoria.get().strip(),
            id_proveedor=id_prov,
            stock_actual=stock,
            stock_minimo=stock_min,
            precio_costo=costo,
            precio_venta=venta,
            ubicacion=self.var_ubicacion.get().strip(),
            activo=self.producto_estado_activo
        )

        try:
            es_edicion = self.producto_seleccionado_id is not None
            RepositorioStock.guardar_producto(prod)

            msg = "¡Producto actualizado con éxito!" if es_edicion else "¡Producto registrado con éxito!"
            messagebox.showinfo("Éxito", msg)
            self.limpiar_formulario()
            self.cargar_tabla_productos()
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo guardar el producto:\n{e}")

    def toggle_estado_producto(self):
        if not self.producto_seleccionado_id:
            return

        nuevo_estado = not self.producto_estado_activo
        accion = "reactivar" if nuevo_estado else "deshabilitar"

        if not messagebox.askyesno("Confirmar", f"¿Desea {accion} este producto?"):
            return

        try:
            exito = RepositorioStock.cambiar_estado_producto(self.producto_seleccionado_id, nuevo_estado)
            if exito:
                messagebox.showinfo("Listo", f"El producto ha sido {accion[:-1]}do correctamente.")
                self.limpiar_formulario()
                self.cargar_tabla_productos()
            else:
                messagebox.showerror("Error", f"No se pudo {accion} el producto.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def generar_orden_compra_seleccionado(self):
        """Emite una Orden de Compra formal para el producto seleccionado."""
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione un producto de la tabla.")
            return

        prod = self.productos_cache.get(str(self.producto_seleccionado_id))
        if not prod:
            messagebox.showerror("Error", "No se encontró la información del producto seleccionado.")
            return

        cantidad_sugerida = max(75, prod.stock_minimo * 2)
        fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

        texto_oc = (
            "========================================================================\n"
            "                 FRANKIE GESTOR S.R.L. - ORDEN DE COMPRA                \n"
            "                     Reposición por Stock Crítico                       \n"
            "========================================================================\n"
            f" Fecha Emisión : {fecha_emision:<22} Proveedor ID: {prod.id_proveedor}\n"
            f" Producto      : [{prod.codigo}] {prod.descripcion}\n"
            f" Stock Actual  : {prod.stock_actual:<10} Stock Mínimo: {prod.stock_minimo}\n"
            f" Sugerencia    : Reponer {cantidad_sugerida} unidades a la brevedad.\n"
            "------------------------------------------------------------------------\n"
            " Observaciones: Alerta disparada por stock inferior o igual al mínimo (75).\n"
            "========================================================================\n"
            "\n\n"
            "   ___________________________             ___________________________  \n"
            "        Control de Stock                       Firma de Autorización    \n"
        )

        modal = tk.Toplevel(self)
        modal.title(f"Orden de Compra - {prod.codigo}")
        modal.geometry("670x480")
        modal.grab_set()

        frame = ttk.Frame(modal, padding=12)
        frame.pack(fill="both", expand=True)

        txt = tk.Text(frame, font=("Courier New", 10), bg="#FFF", fg="#1E293B", relief="solid", borderwidth=1, padx=10,
                      pady=10, height=18)
        txt.insert("1.0", texto_oc)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, pady=(0, 10))

        def exportar_html():
            carpeta = Path(__file__).resolve().parent.parent.parent / "ordenes_compra"
            carpeta.mkdir(parents=True, exist_ok=True)
            archivo = carpeta / f"OrdenCompra_{prod.codigo}.html"
            html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Orden de Compra</title>
<style>body{{font-family:'Courier New',monospace;padding:30px;background:#f8fafc;}}
.orden{{background:#fff;border:2px solid #0f172a;padding:25px;max-width:720px;margin:auto;white-space:pre;}}
@media print{{.no-print{{display:none;}}}}</style></head>
<body><div class="orden">{texto_oc}</div>
<p class="no-print" style="text-align:center;margin-top:15px;"><button onclick="window.print()" style="padding:10px 20px;font-size:15px;cursor:pointer;">🖨️ Imprimir / Guardar como PDF</button></p>
</body></html>"""
            archivo.write_text(html, encoding="utf-8")
            webbrowser.open(archivo.as_uri())
            messagebox.showinfo("Exportado", f"Orden de compra generada en:\n{archivo}")

        btn_box = ttk.Frame(frame)
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="🖨️ Imprimir / Guardar PDF", command=exportar_html).pack(side="left")
        ttk.Button(btn_box, text="Cerrar", command=modal.destroy).pack(side="right")

    def limpiar_formulario(self):
        self.producto_seleccionado_id = None
        self.producto_estado_activo = True
        self.var_codigo.set("")
        self.var_descripcion.set("")
        self.var_categoria.set("")
        self.var_stock.set("0")
        self.var_stock_minimo.set("75")
        self.var_costo.set("0.00")
        self.var_venta.set("0.00")
        self.var_ubicacion.set("")
        self.btn_guardar.config(text="Guardar Producto")
        self.btn_toggle_estado.config(text="Deshabilitar", state="disabled")
        self.btn_orden_compra.config(state="disabled")
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())

    def _al_seleccionar_fila(self, _event=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        if not valores:
            return

        id_prod_str = str(valores[0])
        prod = self.productos_cache.get(id_prod_str)
        if not prod:
            return

        self.producto_seleccionado_id = prod.id
        self.producto_estado_activo = bool(getattr(prod, "activo", True))

        self.var_codigo.set(prod.codigo or "")
        self.var_descripcion.set(prod.descripcion or "")
        self.var_categoria.set(prod.categoria or "")
        self.var_stock.set(str(prod.stock_actual))
        self.var_stock_minimo.set(str(prod.stock_minimo))
        self.var_costo.set(f"{prod.precio_costo:.2f}")
        self.var_venta.set(f"{prod.precio_venta:.2f}")
        self.var_ubicacion.set(prod.ubicacion or "")

        for nombre_combo, id_p in self.proveedores_map.items():
            if id_p == prod.id_proveedor:
                self.var_proveedor_sel.set(nombre_combo)
                break

        self.btn_guardar.config(text="Actualizar Producto")
        self.btn_toggle_estado.config(
            state="normal",
            text="Deshabilitar" if self.producto_estado_activo else "Reactivar"
        )
        self.btn_orden_compra.config(state="normal")