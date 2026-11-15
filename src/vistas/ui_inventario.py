"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: INVENTARIO Y PROVEEDORES (vistas/ui_inventario.py)
===============================================================================
Gestión completa de productos, stock, alertas y padrón de proveedores
(altas, modificaciones, ajustes y bajas).
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_stock import Producto
from dominio.entidades_proveedores import Proveedor
from vistas.ui_estilos import COLOR_TEXTO_MUTED


class InterfazInventario(ttk.Frame):
    """
    Componente visual modular basado en ttk.Frame para la gestión completa de stock y proveedores.
    """

    def __init__(self, parent: tk.Widget, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.repo = RepositorioStock()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_productos = ttk.Frame(notebook)
        self.tab_proveedores = ttk.Frame(notebook)

        notebook.add(self.tab_productos, text="📦 Control de Inventario y Stock")
        notebook.add(self.tab_proveedores, text="🤝 Padrón de Proveedores")

        self._construir_pestana_productos(self.tab_productos)
        self._construir_pestana_proveedores(self.tab_proveedores)

        self.cargar_datos()

    def _construir_pestana_productos(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        frame_acciones = ttk.Frame(parent, padding=5)
        frame_acciones.grid(row=0, column=0, sticky="ew")

        btn_nuevo_prod = ttk.Button(frame_acciones, text="+ Registrar / Editar Producto",
                                    command=self._manejar_click_producto)
        btn_nuevo_prod.pack(side=tk.LEFT, padx=5)

        btn_ajustar = ttk.Button(frame_acciones, text="Ajustar Stock", command=self._dialogo_ajustar_stock)
        btn_ajustar.pack(side=tk.LEFT, padx=5)

        btn_eliminar_prod = ttk.Button(frame_acciones, text="🗑️ Eliminar Producto", command=self._eliminar_producto)
        btn_eliminar_prod.pack(side=tk.LEFT, padx=5)

        self.var_solo_alertas = tk.BooleanVar(value=False)
        chk_alertas = ttk.Checkbutton(
            frame_acciones, text="Ver solo Alertas de Stock Mínimo",
            variable=self.var_solo_alertas, command=self.cargar_datos
        )
        chk_alertas.pack(side=tk.RIGHT, padx=5)

        frame_tabla = ttk.Frame(parent)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        columnas = ("id", "codigo", "descripcion", "categoria", "stock", "minimo", "precio", "ubicacion", "proveedor")
        self.tabla_prod = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

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
        self.tabla_prod.column("descripcion", width=180, anchor=tk.W)
        self.tabla_prod.column("categoria", width=100, anchor=tk.W)
        self.tabla_prod.column("stock", width=80, anchor=tk.CENTER)
        self.tabla_prod.column("minimo", width=80, anchor=tk.CENTER)
        self.tabla_prod.column("precio", width=90, anchor=tk.E)
        self.tabla_prod.column("ubicacion", width=90, anchor=tk.CENTER)
        self.tabla_prod.column("proveedor", width=130, anchor=tk.W)

        scrollbar_p = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_prod.yview)
        self.tabla_prod.configure(yscrollcommand=scrollbar_p.set)

        self.tabla_prod.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_p.pack(side=tk.RIGHT, fill=tk.Y)

    def _construir_pestana_proveedores(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        frame_acciones = ttk.Frame(parent, padding=5)
        frame_acciones.grid(row=0, column=0, sticky="ew")

        btn_nuevo_prov = ttk.Button(frame_acciones, text="+ Registrar Proveedor", command=self._abrir_modal_proveedor)
        btn_nuevo_prov.pack(side=tk.LEFT, padx=5)

        btn_editar_prov = ttk.Button(frame_acciones, text="✏️ Modificar Proveedor", command=self._modificar_proveedor)
        btn_editar_prov.pack(side=tk.LEFT, padx=5)

        btn_eliminar_prov = ttk.Button(frame_acciones, text="🗑️ Dar de Baja / Borrar", command=self._eliminar_proveedor)
        btn_eliminar_prov.pack(side=tk.LEFT, padx=5)

        frame_tabla = ttk.Frame(parent)
        frame_tabla.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        columnas_prov = ("id_prov", "razon_social", "cuit", "rubro", "telefono", "email")
        self.tabla_prov = ttk.Treeview(frame_tabla, columns=columnas_prov, show="headings", height=12)

        self.tabla_prov.heading("id_prov", text="ID")
        self.tabla_prov.heading("razon_social", text="Razón Social / Nombre")
        self.tabla_prov.heading("cuit", text="CUIT / Documento")
        self.tabla_prov.heading("rubro", text="Rubro")
        self.tabla_prov.heading("telefono", text="Teléfono")
        self.tabla_prov.heading("email", text="Email")

        self.tabla_prov.column("id_prov", width=40, anchor=tk.CENTER)
        self.tabla_prov.column("razon_social", width=220, anchor=tk.W)
        self.tabla_prov.column("cuit", width=120, anchor=tk.CENTER)
        self.tabla_prov.column("rubro", width=140, anchor=tk.W)
        self.tabla_prov.column("telefono", width=110, anchor=tk.CENTER)
        self.tabla_prov.column("email", width=160, anchor=tk.W)

        scrollbar_prov = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_prov.yview)
        self.tabla_prov.configure(yscrollcommand=scrollbar_prov.set)

        self.tabla_prov.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_prov.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_datos(self) -> None:
        for item in self.tabla_prod.get_children():
            self.tabla_prod.delete(item)

        try:
            solo_alertas = self.var_solo_alertas.get()
            productos = self.repo.listar_productos(solo_alertas=solo_alertas)
            for prod in productos:
                self.tabla_prod.insert(
                    "", tk.END, iid=str(prod.id),
                    values=(
                        prod.id,
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

        for item in self.tabla_prov.get_children():
            self.tabla_prov.delete(item)

        try:
            proveedores = self.repo.listar_proveedores()
            for prov in proveedores:
                self.tabla_prov.insert(
                    "", tk.END, iid=str(prov.id),
                    values=(
                        prov.id,
                        prov.razon_social,
                        prov.nro_documento,
                        prov.rubro,
                        prov.telefono,
                        prov.email
                    )
                )
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo cargar el padrón de proveedores: {err}")

    def _abrir_modal_proveedor(self, proveedor_editar: Proveedor | None = None) -> None:
        modal = tk.Toplevel(self)
        es_edicion = proveedor_editar is not None
        modal.title("Modificar Proveedor" if es_edicion else "Registrar Proveedor")
        modal.geometry("450x520")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ttk.Label(modal, text="Razón Social / Nombre *:").pack(anchor="w", padx=15, pady=(15, 2))
        txt_razon = ttk.Entry(modal, width=45)
        txt_razon.pack(padx=15, pady=2)
        if es_edicion:
            txt_razon.insert(0, proveedor_editar.razon_social or "")

        ttk.Label(modal, text="CUIT / Documento *:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_cuit = ttk.Entry(modal, width=45)
        txt_cuit.pack(padx=15, pady=2)
        if es_edicion:
            txt_cuit.insert(0, proveedor_editar.nro_documento or "")

        ttk.Label(modal, text="Rubro:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_rubro = ttk.Entry(modal, width=45)
        txt_rubro.pack(padx=15, pady=2)
        if es_edicion:
            txt_rubro.insert(0, proveedor_editar.rubro or "")

        ttk.Label(modal, text="Domicilio:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_dom = ttk.Entry(modal, width=45)
        txt_dom.pack(padx=15, pady=2)
        if es_edicion:
            txt_dom.insert(0, proveedor_editar.domicilio or "")

        ttk.Label(modal, text="Teléfono:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_tel = ttk.Entry(modal, width=45)
        txt_tel.pack(padx=15, pady=2)
        if es_edicion:
            txt_tel.insert(0, proveedor_editar.telefono or "")

        ttk.Label(modal, text="Email:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_email = ttk.Entry(modal, width=45)
        txt_email.pack(padx=15, pady=2)
        if es_edicion:
            txt_email.insert(0, proveedor_editar.email or "")

        def guardar() -> None:
            try:
                razon = txt_razon.get().strip()
                cuit = txt_cuit.get().strip()
                if not razon or not cuit:
                    messagebox.showwarning("Atención", "Razón Social y CUIT son obligatorios.", parent=modal)
                    return

                if es_edicion:
                    prov = Proveedor(
                        id=proveedor_editar.id,
                        id_persona=proveedor_editar.id_persona,
                        tipo_persona=proveedor_editar.tipo_persona or "Juridica",
                        razon_social=razon,
                        nro_documento=cuit,
                        rubro=txt_rubro.get().strip(),
                        domicilio=txt_dom.get().strip(),
                        telefono=txt_tel.get().strip(),
                        email=txt_email.get().strip()
                    )
                else:
                    prov = Proveedor(
                        tipo_persona="Juridica",
                        razon_social=razon,
                        nro_documento=cuit,
                        rubro=txt_rubro.get().strip(),
                        domicilio=txt_dom.get().strip(),
                        telefono=txt_tel.get().strip(),
                        email=txt_email.get().strip()
                    )

                self.repo.guardar_proveedor(prov)
                messagebox.showinfo("Éxito", "Proveedor guardado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo guardar: {err}", parent=modal)

        ttk.Button(modal, text="Guardar Cambios" if es_edicion else "Registrar Proveedor", command=guardar).pack(
            pady=20)

    def _modificar_proveedor(self) -> None:
        selected = self.tabla_prov.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un proveedor de la tabla para modificar.")
            return

        id_prov = int(selected[0])
        proveedores = self.repo.listar_proveedores()
        prov_obj = next((p for p in proveedores if p.id == id_prov), None)

        if prov_obj:
            self._abrir_modal_proveedor(prov_obj)
        else:
            messagebox.showerror("Error", "No se encontró el proveedor seleccionado.")

    def _eliminar_proveedor(self) -> None:
        selected = self.tabla_prov.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un proveedor para dar de baja o eliminar.")
            return

        id_prov = int(selected[0])
        if messagebox.askyesno("Confirmar Baja",
                               "¿Confirma que desea eliminar/dar de baja este proveedor? (Asegúrese de que no tenga productos activos vinculados)."):
            try:
                from infraestructura.conexion import ConexionDB
                with ConexionDB() as db:
                    cursor = db.conexion.cursor()
                    cursor.execute("DELETE FROM proveedores WHERE id = ?;", (id_prov,))
                    db.conexion.commit()

                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente.")
                self.cargar_datos()
            except Exception as err:
                messagebox.showerror("Error",
                                     f"No se pudo eliminar el proveedor (puede tener productos asociados): {err}")

    def _eliminar_producto(self) -> None:
        selected = self.tabla_prod.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un producto de la tabla para eliminar (descontinuado).")
            return

        id_prod = int(selected[0])
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Confirma la eliminación definitiva de este producto discontinuado del stock?"):
            try:
                self.repo.eliminar_producto(id_prod)
                messagebox.showinfo("Éxito", "Producto eliminado del inventario.")
                self.cargar_datos()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {err}")

    def _manejar_click_producto(self) -> None:
        selected = self.tabla_prod.selection()
        if selected:
            id_prod = int(selected[0])
            productos = self.repo.listar_productos()
            prod_obj = next((p for p in productos if p.id == id_prod), None)
            if prod_obj:
                self._abrir_modal_producto(prod_obj)
                return

        self._abrir_modal_producto(None)

    def _abrir_modal_producto(self, producto_editar: Producto | None = None) -> None:
        proveedores = self.repo.listar_proveedores()
        if not proveedores:
            messagebox.showwarning("Atención",
                                   "Debe registrar al menos un proveedor en la solapa 'Padrón Proveedores' antes de dar de alta productos.")
            return

        modal = tk.Toplevel(self)
        es_edicion = producto_editar is not None
        modal.title("Modificar Producto / Stock" if es_edicion else "Registrar Producto / Stock")
        modal.geometry("450x550")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ttk.Label(modal, text="Proveedor Asociado *:").pack(anchor="w", padx=15, pady=(15, 2))
        prov_map = {f"{p.id} - {p.razon_social}": p.id for p in proveedores}
        cmb_prov = ttk.Combobox(modal, values=list(prov_map.keys()), state="readonly", width=42)
        cmb_prov.pack(padx=15, pady=2)

        if es_edicion and producto_editar.id_proveedor:
            matching_key = next((k for k, v in prov_map.items() if v == producto_editar.id_proveedor), None)
            if matching_key:
                cmb_prov.set(matching_key)
            elif prov_map:
                cmb_prov.current(0)
        elif prov_map:
            cmb_prov.current(0)

        ttk.Label(modal, text="Código del Producto *:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_codigo = ttk.Entry(modal, width=45)
        txt_codigo.pack(padx=15, pady=2)
        if es_edicion:
            txt_codigo.insert(0, producto_editar.codigo or "")

        ttk.Label(modal, text="Descripción / Nombre *:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_desc = ttk.Entry(modal, width=45)
        txt_desc.pack(padx=15, pady=2)
        if es_edicion:
            txt_desc.insert(0, producto_editar.descripcion or "")

        ttk.Label(modal, text="Categoría:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_cat = ttk.Entry(modal, width=45)
        txt_cat.pack(padx=15, pady=2)
        if es_edicion:
            txt_cat.insert(0, producto_editar.categoria or "")

        ttk.Label(modal, text="Stock Inicial / Actual:").pack(anchor="w", padx=15, pady=(10, 2))
        txt_stock = ttk.Entry(modal, width=45)
        txt_stock.insert(0, str(producto_editar.stock_actual) if es_edicion else "10")
        txt_stock.pack(padx=15, pady=2)

        ttk.Label(modal, text="Precio de Venta ($):").pack(anchor="w", padx=15, pady=(10, 2))
        txt_precio = ttk.Entry(modal, width=45)
        txt_precio.insert(0, f"{producto_editar.precio_venta:.2f}" if es_edicion else "0.00")
        txt_precio.pack(padx=15, pady=2)

        def guardar_prod() -> None:
            try:
                seleccion_prov = cmb_prov.get()
                if not seleccion_prov:
                    messagebox.showwarning("Atención", "Seleccione un proveedor.", parent=modal)
                    return
                id_prov = prov_map[seleccion_prov]

                if es_edicion:
                    prod = Producto(
                        id=producto_editar.id,
                        codigo=txt_codigo.get().strip(),
                        descripcion=txt_desc.get().strip(),
                        categoria=txt_cat.get().strip(),
                        id_proveedor=id_prov,
                        stock_actual=int(txt_stock.get() or 0),
                        precio_venta=float(txt_precio.get() or 0)
                    )
                else:
                    prod = Producto(
                        codigo=txt_codigo.get().strip(),
                        descripcion=txt_desc.get().strip(),
                        categoria=txt_cat.get().strip(),
                        id_proveedor=id_prov,
                        stock_actual=int(txt_stock.get() or 0),
                        precio_venta=float(txt_precio.get() or 0)
                    )

                self.repo.guardar_producto(prod)
                messagebox.showinfo("Éxito", "Producto guardado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos()
            except ValueError:
                messagebox.showerror("Error", "Revise los campos numéricos.", parent=modal)
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo guardar el producto: {err}", parent=modal)

        ttk.Button(modal, text="Guardar Cambios" if es_edicion else "Guardar Producto", command=guardar_prod).pack(
            pady=20)

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