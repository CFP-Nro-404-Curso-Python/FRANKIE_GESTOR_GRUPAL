"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: CONTROL DE INVENTARIO Y STOCK (vistas/ui_inventario.py)
===============================================================================
Permite administrar el inventario de productos, controlar existencias y
visualizar alertas de reposición (stock mínimo) de forma directa y limpia.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_stock import Producto
from vistas.ui_estilos import COLOR_TEXTO_MUTED


class InterfazInventario(ttk.Frame):
    """
    Componente visual modular basado en ttk.Frame para la gestión exclusiva de inventario y stock.
    """

    def __init__(self, parent: tk.Widget, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.repo = RepositorioStock()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._crear_encabezado()
        self._crear_panel_acciones()
        self._crear_tabla_productos()
        self.cargar_datos()

    def _crear_encabezado(self) -> None:
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        lbl_titulo = ttk.Label(
            frame_top,
            text="Control de Inventario y Stock",
            style="Subtitulo.TLabel"
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ttk.Label(
            frame_top,
            text="Administración de productos, existencias físicas y alertas de reposición",
            foreground=COLOR_TEXTO_MUTED
        )
        lbl_subtitulo.pack(anchor="w")

    def _crear_panel_acciones(self) -> None:
        frame_acciones = ttk.Frame(self, padding=10)
        frame_acciones.grid(row=1, column=0, sticky="ew", padx=10)

        btn_nuevo_prod = ttk.Button(frame_acciones, text="+ Registrar / Editar Producto", command=self._abrir_modal_producto)
        btn_nuevo_prod.pack(side=tk.LEFT, padx=5)

        btn_ajustar = ttk.Button(frame_acciones, text="Ajustar Stock (Entrada/Salida)", command=self._dialogo_ajustar_stock)
        btn_ajustar.pack(side=tk.LEFT, padx=5)

        self.var_solo_alertas = tk.BooleanVar(value=False)
        chk_alertas = ttk.Checkbutton(
            frame_acciones, text="Ver solo Alertas de Stock Mínimo",
            variable=self.var_solo_alertas, command=self.cargar_datos
        )
        chk_alertas.pack(side=tk.RIGHT, padx=5)

    def _crear_tabla_productos(self) -> None:
        frame_tabla = ttk.LabelFrame(self, text=" Catálogo de Productos ")
        frame_tabla.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 15))
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        columnas = ("id", "codigo", "descripcion", "categoria", "stock", "minimo", "precio", "ubicacion", "proveedor")
        self.tabla_prod = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

        self.tabla_prod.heading("id", text="ID")
        self.tabla_prod.heading("codigo", text="Código")
        self.tabla_prod.heading("descripcion", text="Descripción del Producto")
        self.tabla_prod.heading("categoria", text="Categoría")
        self.tabla_prod.heading("stock", text="Stock Actual")
        self.tabla_prod.heading("minimo", text="Stock Mín.")
        self.tabla_prod.heading("precio", text="Precio Venta")
        self.tabla_prod.heading("ubicacion", text="Ubicación")
        self.tabla_prod.heading("proveedor", text="Proveedor")

        self.tabla_prod.column("id", width=40, anchor=tk.CENTER)
        self.tabla_prod.column("codigo", width=90, anchor=tk.CENTER)
        self.tabla_prod.column("descripcion", width=200, anchor=tk.W)
        self.tabla_prod.column("categoria", width=100, anchor=tk.W)
        self.tabla_prod.column("stock", width=80, anchor=tk.CENTER)
        self.tabla_prod.column("minimo", width=80, anchor=tk.CENTER)
        self.tabla_prod.column("precio", width=90, anchor=tk.E)
        self.tabla_prod.column("ubicacion", width=90, anchor=tk.CENTER)
        self.tabla_prod.column("proveedor", width=150, anchor=tk.W)

        scrollbar_p = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_prod.yview)
        self.tabla_prod.configure(yscrollcommand=scrollbar_p.set)

        self.tabla_prod.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_p.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_datos(self) -> None:
        for item in self.tabla_prod.get_children():
            self.tabla_prod.delete(item)

        try:
            solo_alertas = self.var_solo_alertas.get()
            productos = self.repo.listar_productos(solo_alertas=solo_alertas)
            for prod in productos:
                self.tabla_prod.insert(
                    "", tk.END, iid=str(prod.id_producto),
                    values=(
                        prod.id_producto,
                        prod.codigo,
                        prod.descripcion,
                        prod.categoria,
                        prod.stock_actual,
                        prod.stock_minimo,
                        f"$ {prod.precio_venta:,.2f}",
                        prod.ubicacion or "",
                        prod.nombre_proveedor or "N/A"
                    )
                )
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo cargar el inventario: {err}")

    def _abrir_modal_producto(self) -> None:
        proveedores = self.repo.listar_proveedores()
        if not proveedores:
            messagebox.showwarning("Atención", "Debe registrar al menos un proveedor en la solapa 'Padrón Proveedores' antes de dar de alta productos.")
            return

        modal = tk.Toplevel(self)
        modal.title("Gestión de Producto / Stock")
        modal.geometry("450x550")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ttk.Label(modal, text="Proveedor Asociado *:").pack(anchor="w", padx=15, pady=(15, 2))
        prov_map = {f"{p.id} - {p.nombre_comercial}": p.id for p in proveedores}
        cmb_prov = ttk.Combobox(modal, values=list(prov_map.keys()), state="readonly", width=42)
        cmb_prov.pack(padx=15, pady=2)
        if prov_map:
            cmb_prov.current(0)

        ttk.Label(modal, text="Código del Producto *:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_codigo = ttk.Entry(modal, width=45)
        txt_codigo.pack(padx=15, pady=2)

        ttk.Label(modal, text="Descripción / Nombre *:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_desc = ttk.Entry(modal, width=45)
        txt_desc.pack(padx=15, pady=2)

        ttk.Label(modal, text="Categoría:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_cat = ttk.Entry(modal, width=45)
        txt_cat.pack(padx=15, pady=2)

        ttk.Label(modal, text="Stock Inicial / Actual:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_stock = ttk.Entry(modal, width=45)
        txt_stock.insert(0, "10")
        txt_stock.pack(padx=15, pady=2)

        ttk.Label(modal, text="Precio de Venta ($):").pack(anchor="w", padx=15, pady=(10, 2))
        txt_precio = ttk.Entry(modal, width=45)
        txt_precio.insert(0, "0.00")
        txt_precio.pack(padx=15, pady=2)

        def guardar_prod() -> None:
            try:
                seleccion_prov = cmb_prov.get()
                if not seleccion_prov:
                    messagebox.showwarning("Atención", "Seleccione un proveedor.", parent=modal)
                    return
                id_prov = prov_map[seleccion_prov]

                prod = Producto(
                    codigo=txt_codigo.get().strip(),
                    descripcion=txt_desc.get().strip(),
                    categoria=txt_cat.get().strip(),
                    id_proveedor=id_prov,
                    stock_actual=int(txt_stock.get() or 0),
                    precio_venta=float(txt_precio.get() or 0)
                )
                self.repo.guardar_producto(prod)
                messagebox.showinfo("Éxito", "Producto registrado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError:
                messagebox.showerror("Error", "Revise los campos numéricos.", parent=modal)
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo guardar el producto: {err}", parent=modal)

        ttk.Button(modal, text="Guardar Producto", command=guardar_prod).pack(pady=20)

    def _dialogo_ajustar_stock(self) -> None:
        selected = self.tabla_prod.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla para ajustar su stock.")
            return

        raw_id = selected[0]
        assert raw_id is not None
        id_prod: int = int(raw_id)

        modal = tk.Toplevel(self)
        modal.title("Ajuste Manual de Stock")
        modal.geometry("350x250")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ttk.Label(modal, text="Cantidad a sumar (+) o restar (-):").pack(anchor="w", padx=20, pady=(20, 5))
        txt_cant = ttk.Entry(modal, width=25)
        txt_cant.insert(0, "1")
        txt_cant.pack(padx=20, pady=5)

        def ejecutar_ajuste() -> None:
            try:
                cambio = int(txt_cant.get().strip())
                self.repo.ajustar_stock(id_prod, cambio)
                messagebox.showinfo("Éxito", "Stock ajustado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError as err:
                messagebox.showerror("Error de Validación", f"{err}", parent=modal)

        ttk.Button(modal, text="Aplicar Ajuste", command=ejecutar_ajuste).pack(pady=20)