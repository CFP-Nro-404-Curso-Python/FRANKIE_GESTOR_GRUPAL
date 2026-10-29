"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: GESTIÓN DE PROVEEDORES (vistas/ui_proveedores.py)
===============================================================================
Permite registrar y consultar los proveedores asociados al control de stock.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from infraestructura.repo_stock import RepositorioStock
from dominio.entidades_proveedores import Proveedor
from vistas.ui_estilos import COLOR_TEXTO_MUTED


class InterfazProveedores(ttk.Frame):
    """
    Componente visual modular basado en ttk.Frame para la gestión de proveedores.
    """

    def __init__(self, parent: tk.Widget, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._crear_encabezado()
        self._crear_formulario()
        self._crear_tabla_proveedores()
        self._cargar_datos_tabla()

    def _crear_encabezado(self) -> None:
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        lbl_titulo = ttk.Label(
            frame_top,
            text="Padrón de Proveedores",
            style="Subtitulo.TLabel"
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ttk.Label(
            frame_top,
            text="Administración de proveedores y fuentes de abastecimiento para inventario",
            foreground=COLOR_TEXTO_MUTED
        )
        lbl_subtitulo.pack(anchor="w")

    def _crear_formulario(self) -> None:
        frame_form = ttk.LabelFrame(self, text=" Datos del Proveedor ")
        frame_form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame_form.columnconfigure((1, 3), weight=1)

        ttk.Label(frame_form, text="Razón Social / Nombre *:").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.txt_razon_social = ttk.Entry(frame_form)
        self.txt_razon_social.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_form, text="CUIT / Doc *:").grid(row=0, column=2, padx=10, pady=6, sticky="w")
        self.txt_cuit = ttk.Entry(frame_form)
        self.txt_cuit.grid(row=0, column=3, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_form, text="Teléfono:").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.txt_telefono = ttk.Entry(frame_form)
        self.txt_telefono.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_form, text="Correo Electrónico:").grid(row=1, column=2, padx=10, pady=6, sticky="w")
        self.txt_email = ttk.Entry(frame_form)
        self.txt_email.grid(row=1, column=3, padx=10, pady=6, sticky="ew")

        frame_btns = ttk.Frame(frame_form)
        frame_btns.grid(row=2, column=0, columnspan=4, padx=10, pady=12)

        btn_guardar = ttk.Button(frame_btns, text="Guardar Proveedor", command=self._guardar_proveedor)
        btn_guardar.pack(side="left", padx=5)

        btn_limpiar = ttk.Button(frame_btns, text="Limpiar Campos", command=self._limpiar_formulario)
        btn_limpiar.pack(side="left", padx=5)

    def _crear_tabla_proveedores(self) -> None:
        frame_tabla = ttk.LabelFrame(self, text=" Listado de Proveedores Registrados ")
        frame_tabla.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        columnas = ("id", "razon_social", "cuit", "telefono", "email")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("razon_social", text="Razón Social")
        self.tree.heading("cuit", text="CUIT")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("email", text="Correo Electrónico")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("razon_social", width=250, anchor="w")
        self.tree.column("cuit", width=130, anchor="center")
        self.tree.column("telefono", width=120, anchor="center")
        self.tree.column("email", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _cargar_datos_tabla(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            proveedores = RepositorioStock.listar_proveedores()
            for item_proveedor in proveedores:
                id_prov = getattr(item_proveedor, "id_proveedor", getattr(item_proveedor, "id", ""))
                razon = getattr(item_proveedor, "nombre_comercial", getattr(item_proveedor, "razon_social", ""))
                cuit = getattr(item_proveedor, "nro_documento", "")
                tel = getattr(item_proveedor, "telefono", "")
                email = getattr(item_proveedor, "email", "")

                self.tree.insert(
                    "",
                    "end",
                    values=(id_prov, razon, cuit, tel, email)
                )
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo cargar el listado de proveedores: {err}")

    def _guardar_proveedor(self) -> None:
        try:
            razon_social = self.txt_razon_social.get().strip()
            cuit = self.txt_cuit.get().strip()
            telefono = self.txt_telefono.get().strip()
            email = self.txt_email.get().strip()

            if not razon_social or not cuit:
                messagebox.showwarning("Atención", "La Razón Social y el CUIT son obligatorios.")
                return

            # Instanciamos el objeto Proveedor tal como lo exige el repositorio
            nuevo_proveedor = Proveedor(
                razon_social=razon_social,
                nro_documento=cuit,
                telefono=telefono,
                email=email,
                rubro="General"
            )

            RepositorioStock.guardar_proveedor(nuevo_proveedor)

            messagebox.showinfo("Éxito", "Proveedor registrado correctamente.")
            self._limpiar_formulario()
            self._cargar_datos_tabla()

        except Exception as err:
            messagebox.showerror("Error", f"No se pudo guardar el proveedor: {err}")

    def _limpiar_formulario(self) -> None:
        self.txt_razon_social.delete(0, "end")
        self.txt_cuit.delete(0, "end")
        self.txt_telefono.delete(0, "end")
        self.txt_email.delete(0, "end")