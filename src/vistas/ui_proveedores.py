"""
===============================================================================
MÓDULO DE VISTAS: INTERFAZ DE PROVEEDORES (src/vistas/ui_proveedores.py)
===============================================================================
Gestión completa del padrón de proveedores: Alta, Listado, Edición y Baja Lógica.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox

from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_proveedores import Proveedor


class InterfazProveedores(ttk.Frame):
    """
    Panel de control y gestión del padrón de proveedores.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Estado de selección y caché local
        self.proveedor_seleccionado_id = None
        self.persona_seleccionada_id = None
        self.proveedor_estado_activo = True
        self.proveedores_cache = {}

        # Variables de control del formulario
        self.var_razon_social = tk.StringVar()
        self.var_rubro = tk.StringVar()
        self.var_tipo_doc = tk.StringVar(value="CUIT")
        self.var_nro_doc = tk.StringVar()
        self.var_contacto_sec = tk.StringVar()
        self.var_telefono = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_domicilio = tk.StringVar()
        self.var_ciudad = tk.StringVar()
        self.var_provincia = tk.StringVar()
        self.var_cp = tk.StringVar()

        self.var_busqueda = tk.StringVar()
        self.var_mostrar_inactivos = tk.BooleanVar(value=False)

        self._construir_interfaz()
        self.cargar_tabla_proveedores()

    def _construir_interfaz(self):
        # 1. Formulario de Datos
        frame_form = ttk.LabelFrame(self, text=" Datos del Proveedor ", padding=15)
        frame_form.pack(fill="x", padx=5, pady=5)

        # Fila 0: Razón Social y Rubro
        ttk.Label(frame_form, text="Razón Social / Nombre *:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_razon_social, width=30).grid(row=0, column=1, sticky="ew", padx=5,
                                                                                 pady=5)

        ttk.Label(frame_form, text="Rubro *:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_rubro, width=25).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        # Fila 1: Documento y Contacto Secundario
        ttk.Label(frame_form, text="CUIT / Doc *:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_nro_doc, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame_form, text="Contacto Sec.:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_contacto_sec, width=25).grid(row=1, column=3, sticky="ew", padx=5,
                                                                                 pady=5)

        # Fila 2: Teléfono y Email
        ttk.Label(frame_form, text="Teléfono:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_telefono, width=20).grid(row=2, column=1, sticky="w", padx=5,
                                                                             pady=5)

        ttk.Label(frame_form, text="Email:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_email, width=25).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        # Fila 3: Domicilio y Ciudad
        ttk.Label(frame_form, text="Domicilio:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_domicilio, width=30).grid(row=3, column=1, sticky="ew", padx=5,
                                                                              pady=5)

        ttk.Label(frame_form, text="Ciudad:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_form, textvariable=self.var_ciudad, width=20).grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Botonera del Formulario
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=4, column=0, columnspan=4, sticky="e", pady=10)

        ttk.Button(frame_botones, text="Limpiar / Nuevo", command=self.limpiar_formulario).pack(side="left", padx=5)

        self.btn_toggle_estado = ttk.Button(
            frame_botones,
            text="Deshabilitar",
            command=self.toggle_estado_proveedor,
            state="disabled"
        )
        self.btn_toggle_estado.pack(side="left", padx=5)

        self.btn_guardar = ttk.Button(frame_botones, text="Guardar Proveedor", command=self.guardar_proveedor)
        self.btn_guardar.pack(side="left", padx=5)

        # 2. Sección de Listado (Tabla Treeview)
        frame_tabla = ttk.LabelFrame(self,
                                     text=" Padrón de Proveedores (Haga clic en una fila para editar o deshabilitar) ",
                                     padding=15)
        frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        # Filtro de Búsqueda
        frame_busqueda = ttk.Frame(frame_tabla)
        frame_busqueda.pack(fill="x", pady=(0, 8))

        ttk.Label(frame_busqueda, text="Buscar proveedor:").pack(side="left", padx=(0, 5))
        entry_buscar = ttk.Entry(frame_busqueda, textvariable=self.var_busqueda)
        entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry_buscar.bind("<KeyRelease>", lambda _e: self.cargar_tabla_proveedores())

        chk_inactivos = ttk.Checkbutton(
            frame_busqueda,
            text="Mostrar inactivos",
            variable=self.var_mostrar_inactivos,
            command=self.cargar_tabla_proveedores
        )
        chk_inactivos.pack(side="right")

        # Tabla Treeview
        columnas = ("id", "nombre", "rubro", "cuit", "telefono", "email", "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=7)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Razón Social / Nombre")
        self.tabla.heading("rubro", text="Rubro")
        self.tabla.heading("cuit", text="CUIT / Doc")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("email", text="Email")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=35, anchor="center")
        self.tabla.column("nombre", width=170, anchor="w")
        self.tabla.column("rubro", width=120, anchor="w")
        self.tabla.column("cuit", width=110, anchor="center")
        self.tabla.column("telefono", width=95, anchor="center")
        self.tabla.column("email", width=140, anchor="w")
        self.tabla.column("estado", width=70, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tabla.pack(side="top", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def cargar_tabla_proveedores(self):
        """Carga y filtra los registros de proveedores en la tabla."""
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        self.proveedores_cache.clear()
        incluir_inactivos = self.var_mostrar_inactivos.get()

        try:
            proveedores = RepositorioStock.listar_proveedores(incluir_inactivos=incluir_inactivos)
            criterio = self.var_busqueda.get().strip().lower()

            for prov in proveedores:
                # Filtrado local por criterio de búsqueda
                nombre_mostrable = prov.nombre_comercial
                if criterio and criterio not in nombre_mostrable.lower() and criterio not in prov.rubro.lower():
                    continue

                self.proveedores_cache[str(prov.id)] = prov
                estado_str = "Activo" if getattr(prov, "activo", True) else "Inactivo"

                self.tabla.insert("", "end", values=(
                    prov.id,
                    nombre_mostrable,
                    prov.rubro,
                    prov.nro_documento or "-",
                    prov.telefono or "-",
                    prov.email or "-",
                    estado_str
                ))
        except Exception as e:
            print(f"[AVISO] No se pudo cargar la tabla de proveedores: {e}")

    def guardar_proveedor(self):
        """Valida y persiste el proveedor (Alta o Modificación)."""
        razon = self.var_razon_social.get().strip()
        rubro = self.var_rubro.get().strip()
        doc = "".join(c for c in self.var_nro_doc.get() if c.isdigit())

        if not razon or not rubro or not doc:
            messagebox.showwarning("Campos Incompletos", "Por favor, complete Razón Social, Rubro y CUIT/Documento.")
            return

        proveedor = Proveedor(
            id=self.proveedor_seleccionado_id,
            id_persona=self.persona_seleccionada_id,
            razon_social=razon,
            rubro=rubro,
            tipo_documento="CUIT",
            nro_documento=doc,
            contacto_secundario=self.var_contacto_sec.get().strip(),
            telefono=self.var_telefono.get().strip(),
            email=self.var_email.get().strip(),
            domicilio=self.var_domicilio.get().strip(),
            ciudad=self.var_ciudad.get().strip(),
            provincia=self.var_provincia.get().strip(),
            codigo_postal=self.var_cp.get().strip(),
            activo=self.proveedor_estado_activo
        )

        try:
            es_edicion = self.proveedor_seleccionado_id is not None
            exito_id = RepositorioStock.guardar_proveedor(proveedor)

            if exito_id:
                mensaje = "¡Datos del proveedor actualizados correctamente!" if es_edicion else "¡Proveedor registrado correctamente!"
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_formulario()
                self.cargar_tabla_proveedores()
            else:
                messagebox.showerror("Error", "No se pudo guardar el registro del proveedor.")
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Ocurrió un error al persistir los datos: {e}")

    def toggle_estado_proveedor(self):
        """Ejecuta la baja o reactivación lógica del proveedor seleccionado."""
        if not self.proveedor_seleccionado_id:
            return

        nuevo_estado = not self.proveedor_estado_activo
        accion = "reactivar" if nuevo_estado else "deshabilitar"

        confirmado = messagebox.askyesno(
            "Confirmar Acción",
            f"¿Está seguro de que desea {accion} al proveedor seleccionado?"
        )
        if not confirmado:
            return

        try:
            exito = RepositorioStock.cambiar_estado_proveedor(self.proveedor_seleccionado_id, nuevo_estado)
            if exito:
                messagebox.showinfo("Estado Actualizado", f"El proveedor ha sido {accion[:-1]}do correctamente.")
                self.limpiar_formulario()
                self.cargar_tabla_proveedores()
            else:
                messagebox.showerror("Error", f"No se pudo {accion} al proveedor.")
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Error al cambiar el estado del proveedor: {e}")

    def limpiar_formulario(self):
        """Restablece el formulario a su estado inicial."""
        self.proveedor_seleccionado_id = None
        self.persona_seleccionada_id = None
        self.proveedor_estado_activo = True
        self.var_razon_social.set("")
        self.var_rubro.set("")
        self.var_nro_doc.set("")
        self.var_contacto_sec.set("")
        self.var_telefono.set("")
        self.var_email.set("")
        self.var_domicilio.set("")
        self.var_ciudad.set("")
        self.var_provincia.set("")
        self.var_cp.set("")
        self.btn_guardar.config(text="Guardar Proveedor")
        self.btn_toggle_estado.config(text="Deshabilitar", state="disabled")
        if self.tabla.selection():
            self.tabla.selection_remove(self.tabla.selection())

    def _al_seleccionar_fila(self, _event=None):
        """Carga los datos del proveedor seleccionado en el formulario para su edición."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        if not valores:
            return

        id_prov_str = str(valores[0])
        prov = self.proveedores_cache.get(id_prov_str)
        if not prov:
            return

        self.proveedor_seleccionado_id = prov.id
        self.persona_seleccionada_id = prov.id_persona
        self.proveedor_estado_activo = bool(getattr(prov, "activo", True))

        self.var_razon_social.set(prov.razon_social or "")
        self.var_rubro.set(prov.rubro or "")
        self.var_nro_doc.set(prov.nro_documento or "")
        self.var_contacto_sec.set(prov.contacto_secundario or "")
        self.var_telefono.set(prov.telefono or "")
        self.var_email.set(prov.email or "")
        self.var_domicilio.set(prov.domicilio or "")
        self.var_ciudad.set(prov.ciudad or "")
        self.var_provincia.set(prov.provincia or "")
        self.var_cp.set(prov.codigo_postal or "")

        self.btn_guardar.config(text="Actualizar Proveedor")
        self.btn_toggle_estado.config(
            state="normal",
            text="Deshabilitar" if self.proveedor_estado_activo else "Reactivar"
        )