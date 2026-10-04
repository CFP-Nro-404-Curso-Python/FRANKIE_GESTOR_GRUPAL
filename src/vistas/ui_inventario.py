"""
===============================================================================
MÓDULO 4: GESTIÓN DE INVENTARIOS Y PROVEEDORES
Entregables 4 y 5: Vista de Inventario, Alerta de Stock y Orden de Compra
===============================================================================
Interfaz gráfica compatible con el estilo del Módulo 2.
Muestra el catálogo con resaltado de productos en stock mínimo y permite
la emisión e impresión/previsualización de la Orden de Compra al proveedor.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_stock import Producto, Proveedor


class UIInventario(ttk.Frame):
    """
    Vista principal para la gestión de productos, control de stock y emisión
    de Órdenes de Compra.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.id_producto_actual: Optional[int] = None
        self.lista_proveedores_cache: List[Proveedor] = []

        self._inicializar_variables()
        self._construir_ui()
        self._cargar_combo_proveedores()
        self._cargar_productos_en_tabla()

    def _inicializar_variables(self) -> None:
        """ Inicializa las variables de control ligadas a los campos de la UI. """
        self.var_codigo = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_proveedor_id = tk.IntVar()
        self.var_stock_actual = tk.IntVar(value=0)
        self.var_stock_minimo = tk.IntVar(value=5)
        self.var_precio_costo = tk.DoubleVar(value=0.0)
        self.var_precio_venta = tk.DoubleVar(value=0.0)
        self.var_ubicacion = tk.StringVar()
        self.var_solo_alertas = tk.BooleanVar(value=False)

    def _construir_ui(self) -> None:
        """ Construye la interfaz respetando el diseño modular del Módulo 2. """

        # Título principal de la sección
        lbl_titulo = ttk.Label(
            self,
            text="Control de Inventario y Alertas de Stock Mínimo",
            font=("Helvetica", 14, "bold")
        )
        lbl_titulo.pack(side=tk.TOP, anchor="w", pady=(0, 10))

        # Panel dividido: Izquierda (Formulario Carga/Edición) | Derecha (Tabla Catálogo)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------------------
        # FRAME IZQUIERDO: FORMULARIO DE PRODUCTO Y AJUSTES
        # ---------------------------------------------------------------------
        frame_form = ttk.LabelFrame(paned, text=" Ficha del Producto ", padding=10)
        paned.add(frame_form, weight=1)

        ttk.Label(frame_form, text="Código:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_codigo, width=22).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Descripción:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_descripcion, width=22).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Categoría:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_categoria, width=22).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Proveedor:").grid(row=3, column=0, sticky="w", pady=2)
        self.cb_proveedores = ttk.Combobox(frame_form, state="readonly", width=20)
        self.cb_proveedores.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Stock Actual:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_stock_actual, width=22).grid(row=4, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Stock Mínimo:").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_stock_minimo, width=22).grid(row=5, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Precio Costo ($):").grid(row=6, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_precio_costo, width=22).grid(row=6, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Precio Venta ($):").grid(row=7, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_precio_venta, width=22).grid(row=7, column=1, sticky="ew", pady=2)

        ttk.Label(frame_form, text="Ubicación:").grid(row=8, column=0, sticky="w", pady=2)
        ttk.Entry(frame_form, textvariable=self.var_ubicacion, width=22).grid(row=8, column=1, sticky="ew", pady=2)

        # Botones de Acción sobre Producto
        frame_btn_prod = ttk.Frame(frame_form)
        frame_btn_prod.grid(row=9, column=0, columnspan=2, pady=(15, 0))

        btn_guardar = ttk.Button(frame_btn_prod, text="Guardar", command=self._guardar_producto)
        btn_guardar.pack(side=tk.LEFT, padx=3)

        btn_limpiar = ttk.Button(frame_btn_prod, text="Nuevo", command=self._limpiar_formulario)
        btn_limpiar.pack(side=tk.LEFT, padx=3)

        # ---------------------------------------------------------------------
        # FRAME DERECHO: TABLA DE INVENTARIO Y ALERTAS
        # ---------------------------------------------------------------------
        frame_tabla = ttk.LabelFrame(paned, text=" Catálogo e Inventario General ", padding=10)
        paned.add(frame_tabla, weight=2)

        # Barra superior de Filtro de Alertas y Emisión de Orden de Compra
        frame_top_tabla = ttk.Frame(frame_tabla)
        frame_top_tabla.pack(fill=tk.X, pady=(0, 5))

        chk_alertas = ttk.Checkbutton(
            frame_top_tabla,
            text="⚠️ Ver solo productos en Alerta (Stock <= Mínimo)",
            variable=self.var_solo_alertas,
            command=self._cargar_productos_en_tabla
        )
        chk_alertas.pack(side=tk.LEFT)

        btn_oc = ttk.Button(
            frame_top_tabla,
            text="📄 Emitir Orden de Compra",
            command=self._emitir_orden_compra
        )
        btn_oc.pack(side=tk.RIGHT)

        # Definición de la Tabla
        columnas = ("id", "codigo", "descripcion", "stock", "minimo", "costo", "venta", "proveedor")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

        self.tabla.heading("id", text="ID")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("descripcion", text="Descripción")
        self.tabla.heading("stock", text="Stock Act.")
        self.tabla.heading("minimo", text="Stock Mín.")
        self.tabla.heading("costo", text="Costo ($)")
        self.tabla.heading("venta", text="Venta ($)")
        self.tabla.heading("proveedor", text="Proveedor")

        self.tabla.column("id", width=30, anchor="center")
        self.tabla.column("codigo", width=80, anchor="center")
        self.tabla.column("descripcion", width=180)
        self.tabla.column("stock", width=70, anchor="center")
        self.tabla.column("minimo", width=70, anchor="center")
        self.tabla.column("costo", width=80, anchor="e")
        self.tabla.column("venta", width=80, anchor="e")
        self.tabla.column("proveedor", width=140)

        # Estilizado visual de Alerta (Fila en rojo claro para stock crítico)
        self.tabla.tag_configure("alerta_stock", background="#ffcdd2", foreground="#b71c1c")

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_producto)

    # -------------------------------------------------------------------------
    # MÉTODO AUXILIAR DEFENSIVO PARA EXTRACCIÓN DE ID
    # -------------------------------------------------------------------------
    def _extraer_id_seleccionado(self) -> Optional[int]:
        """
        Extrae de forma segura el ID numérico de la fila seleccionada en la tabla.

        Patrón Defensivo Profesional:
        1. Valida que exista una selección activa en la tabla.
        2. Captura posibles errores de conversión (ValueError, TypeError).
        3. Retorna 'int' si el valor es válido o 'None' si la celda está vacía/corrupta,
           evitando caídas del sistema en tiempo de ejecución.
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            return None

        item = self.tabla.item(seleccion[0])
        valores = item.get("values", [])

        if not valores:
            return None

        try:
            return int(valores[0])
        except (ValueError, TypeError):
            return None

    def _cargar_combo_proveedores(self) -> None:
        """ Carga la lista de proveedores en el selector desplegable (Combobox). """
        self.lista_proveedores_cache = RepositorioStock.listar_proveedores()
        nombres = [p.nombre_comercial for p in self.lista_proveedores_cache]
        self.cb_proveedores["values"] = nombres

    def _cargar_productos_en_tabla(self) -> None:
        """ Consulta productos al repositorio y asigna tags de color si requiere reposición. """
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        solo_alertas = self.var_solo_alertas.get()
        productos = RepositorioStock.listar_productos(solo_alertas=solo_alertas)

        for p in productos:
            tags = ("alerta_stock",) if p.requiere_reposicion else ()

            # Resguardo defensivo para los valores numéricos antes del formateo
            precio_costo = p.precio_costo if p.precio_costo is not None else 0.0
            precio_venta = p.precio_venta if p.precio_venta is not None else 0.0

            self.tabla.insert("", tk.END, values=(
                p.id,
                p.codigo,
                p.descripcion,
                p.stock_actual,
                p.stock_minimo,
                f"{precio_costo:,.2f}",
                f"{precio_venta:,.2f}",
                p.nombre_proveedor
            ), tags=tags)

    def _al_seleccionar_producto(self, _event: tk.Event) -> None:
        """ Carga la información del producto seleccionado en el formulario para editar. """
        id_prod = self._extraer_id_seleccionado()
        if id_prod is None:
            return

        productos = RepositorioStock.listar_productos()
        prod = next((p for p in productos if p.id == id_prod), None)

        if prod:
            self.id_producto_actual = prod.id
            self.var_codigo.set(prod.codigo)
            self.var_descripcion.set(prod.descripcion)
            self.var_categoria.set(prod.categoria or "")
            self.var_stock_actual.set(prod.stock_actual if prod.stock_actual is not None else 0)
            self.var_stock_minimo.set(prod.stock_minimo if prod.stock_minimo is not None else 5)
            self.var_precio_costo.set(prod.precio_costo if prod.precio_costo is not None else 0.0)
            self.var_precio_venta.set(prod.precio_venta if prod.precio_venta is not None else 0.0)
            self.var_ubicacion.set(prod.ubicacion or "")

            # Seleccionar el proveedor correspondiente en el combobox
            for idx, prov in enumerate(self.lista_proveedores_cache):
                if prov.id == prod.id_proveedor:
                    self.cb_proveedores.current(idx)
                    break

    def _guardar_producto(self) -> None:
        """ Valida y guarda el producto en la base de datos. """
        if not self.var_codigo.get().strip() or not self.var_descripcion.get().strip():
            messagebox.showwarning("Atención", "El código y la descripción son obligatorios.")
            return

        idx_prov = self.cb_proveedores.current()
        if idx_prov < 0:
            messagebox.showwarning("Atención", "Debe seleccionar un proveedor válido.")
            return

        id_prov = self.lista_proveedores_cache[idx_prov].id

        prod = Producto(
            id=self.id_producto_actual,
            codigo=self.var_codigo.get().strip(),
            descripcion=self.var_descripcion.get().strip(),
            categoria=self.var_categoria.get().strip(),
            id_proveedor=id_prov,
            stock_actual=self.var_stock_actual.get(),
            stock_minimo=self.var_stock_minimo.get(),
            precio_costo=self.var_precio_costo.get(),
            precio_venta=self.var_precio_venta.get(),
            ubicacion=self.var_ubicacion.get().strip()
        )

        try:
            RepositorioStock.guardar_producto(prod)
            messagebox.showinfo("Éxito", "Producto guardado correctamente.")
            self._limpiar_formulario()
            self._cargar_productos_en_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el producto:\n{str(e)}")

    def _limpiar_formulario(self) -> None:
        """ Reinicia los campos de la ficha de producto. """
        self.id_producto_actual = None
        self.var_codigo.set("")
        self.var_descripcion.set("")
        self.var_categoria.set("")
        self.cb_proveedores.set("")
        self.var_stock_actual.set(0)
        self.var_stock_minimo.set(5)
        self.var_precio_costo.set(0.0)
        self.var_precio_venta.set(0.0)
        self.var_ubicacion.set("")
        self.tabla.selection_remove(self.tabla.selection())

    # -------------------------------------------------------------------------
    # ENTREGABLE 5: EMISIÓN DE ORDEN DE COMPRA
    # -------------------------------------------------------------------------

    def _emitir_orden_compra(self) -> None:
        """
        Genera una vista previa del documento de Orden de Compra para el producto
        en alerta seleccionado en la tabla (mismo esquema modal que el recibo de haberes).
        """
        id_prod = self._extraer_id_seleccionado()
        if id_prod is None:
            messagebox.showwarning("Atención", "Seleccione un producto en la tabla para emitir su Orden de Compra.")
            return

        productos = RepositorioStock.listar_productos()
        prod = next((p for p in productos if p.id == id_prod), None)

        if not prod:
            return

        # Buscar datos completos del proveedor de forma segura
        prov = next((p for p in self.lista_proveedores_cache if p.id == prod.id_proveedor), None)
        nombre_prov = prov.nombre_comercial if prov else "Proveedor Desconocido"
        contacto_prov = (prov.telefono or prov.email) if prov else "Sin datos de contacto"

        # ---------------------------------------------------------------------
        # RESGUARDO DEFENSIVO DE TIPOS (Líneas Clave para Linter / Mypy)
        # ---------------------------------------------------------------------
        # Evaluamos 'is not None' para asegurarle al analizador de tipos que
        # ambas variables son obligatoriamente de tipo 'int' y 'float' antes de
        # realizar operaciones aritméticas.
        stock_min: int = prod.stock_minimo if prod.stock_minimo is not None else 5
        stock_act: int = prod.stock_actual if prod.stock_actual is not None else 0
        precio_costo: float = prod.precio_costo if prod.precio_costo is not None else 0.0

        unidades_a_pedir: int = max((stock_min * 2) - stock_act, 10)
        costo_estimado: float = unidades_a_pedir * precio_costo

        # Crear Ventana Modal de Previsualización de la Orden de Compra
        modal = tk.Toplevel(self)
        modal.title("Emisión de Orden de Compra")
        modal.geometry("520x450")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        lbl_top = ttk.Label(modal, text="ORDEN DE COMPRA OFICIAL", font=("Helvetica", 12, "bold"))
        lbl_top.pack(pady=10)

        txt_orden = tk.Text(modal, font=("Courier", 10), wrap="word")
        txt_orden.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        contenido = f"""
===================================================
             FRANKIE GESTOR - REPOSICIÓN
                  ORDEN DE COMPRA
===================================================
PROVEEDOR:   {nombre_prov}
CONTACTO:    {contacto_prov}
---------------------------------------------------
PRODUCTO:    [{prod.codigo}] {prod.descripcion}
STOCK ACT.:  {stock_act} unidades
STOCK MÍN.:  {stock_min} unidades
ESTADO:      ⚠️ ALERTA DE REPOSICIÓN CRÍTICA
---------------------------------------------------
CANTIDAD A SOLICITAR:  {unidades_a_pedir} unidades
PRECIO COSTO UNIT.:    $ {precio_costo:,.2f}
TOTAL ESTIMADO:        $ {costo_estimado:,.2f}
===================================================
Instrucciones: Enviar copia al proveedor para
autorización de despacho e ingreso a depósito.
===================================================
"""
        txt_orden.insert(tk.END, contenido)
        txt_orden.config(state="disabled")

        btn_cerrar = ttk.Button(modal, text="Cerrar / Imprimir", command=modal.destroy)
        btn_cerrar.pack(pady=10)