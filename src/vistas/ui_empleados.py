"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: CAPA DE PRESENTACIÓN DE EMPLEADOS (iu_empleados.py)
===============================================================================
Estrategia y Buenas Prácticas Aplicadas:
1. Módulo Integrado de Vista (Tkinter / TTK):
   Diseñado para ser instanciado como un componente (Frame) dentro de la
   ventana principal gestionada por 'main.py'.

2. Formato e Identificación Fiscal (CUIT/CUIL):
   Visualización limpia y formateada (XX-XXXXXXXX-X) en la grilla sin alterar
   la representación de 11 dígitos numéricos en la persistencia.

3. Valores Sugeridos por Defecto:
   Cargo inicial: 'empleado_ventas' | Sector inicial: 'Ventas'.

4. Desacoplamiento de Inicialización:
   Delegación total de arranque, temas y verificación de BD a 'main.py'.
===============================================================================
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

# Garantizar que el directorio actual esté en sys.path
DIR_ACTUAL = Path(__file__).resolve().parent
RAIZ_PROYECTO = DIR_ACTUAL.parent

for path in (DIR_ACTUAL, RAIZ_PROYECTO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Importación de Entidades y Repositorios
from dominio.entidades_rrhh import (
    Empleado,
    limpiar_documento,
    CARGOS,
    SECTORES,
    TIPOS_VINCULO
)
from infraestructura.repo_rrhh import RepositorioRRHH
from estilos import COLOR_TEXTO_MUTED


def formatear_cuit(cuit_limpio: str) -> str:
    """ Convierte una cadena de 11 dígitos al formato de presentación XX-XXXXXXXX-X. """
    cuit_digits = "".join(filter(str.isdigit, cuit_limpio or ""))
    if len(cuit_digits) == 11:
        return f"{cuit_digits[:2]}-{cuit_digits[2:10]}-{cuit_digits[10]}"
    return cuit_limpio


class InterfazRRHH(ttk.Frame):
    """ Componente principal de Interfaz Gráfica para el Módulo de Recursos Humanos. """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.empleado_edicion_id: Optional[int] = None

        # Configurar distribución responsiva
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)  # Panel Formulario
        self.rowconfigure(2, weight=1)  # Panel Grilla/Tabla

        self._crear_encabezado()
        self._crear_panel_formulario()
        self._crear_panel_tabla()
        self._cargar_tabla()
        self._actualizar_legajo_sugerido()

    def _crear_encabezado(self):
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        lbl_titulo = ttk.Label(
            frame_top,
            text="Gestión de Recursos Humanos",
            style="Subtitulo.TLabel"
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ttk.Label(
            frame_top,
            text="Administración de legajos, datos fiscales, cargos y contratos",
            foreground=COLOR_TEXTO_MUTED
        )
        lbl_subtitulo.pack(anchor="w")

    def _crear_panel_formulario(self):
        self.frame_form = ttk.LabelFrame(self, text=" Datos del Empleado ")
        self.frame_form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_form.columnconfigure((1, 3), weight=1)

        # Row 0: Nombres y Apellidos
        ttk.Label(self.frame_form, text="Nombres:").grid(row=0, column=0, padx=10, pady=4, sticky="w")
        self.txt_nombres = ttk.Entry(self.frame_form)
        self.txt_nombres.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Apellidos:").grid(row=0, column=2, padx=10, pady=4, sticky="w")
        self.txt_apellidos = ttk.Entry(self.frame_form)
        self.txt_apellidos.grid(row=0, column=3, padx=10, pady=4, sticky="ew")

        # Row 1: CUIT/CUIL y Legajo
        ttk.Label(self.frame_form, text="CUIT / CUIL (11 dígitos):").grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.txt_documento = ttk.Entry(self.frame_form)
        self.txt_documento.grid(row=1, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Legajo:").grid(row=1, column=2, padx=10, pady=4, sticky="w")
        self.txt_legajo = ttk.Entry(self.frame_form)
        self.txt_legajo.grid(row=1, column=3, padx=10, pady=4, sticky="ew")

        # Row 2: Cargo y Sector
        ttk.Label(self.frame_form, text="Cargo:").grid(row=2, column=0, padx=10, pady=4, sticky="w")
        self.cmb_cargo = ttk.Combobox(self.frame_form, values=CARGOS, state="readonly")
        default_cargo = "empleado_ventas" if "empleado_ventas" in CARGOS else CARGOS[0]
        self.cmb_cargo.set(default_cargo)
        self.cmb_cargo.grid(row=2, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Sector:").grid(row=2, column=2, padx=10, pady=4, sticky="w")
        self.cmb_sector = ttk.Combobox(self.frame_form, values=SECTORES, state="readonly")
        default_sector = "Ventas" if "Ventas" in SECTORES else SECTORES[0]
        self.cmb_sector.set(default_sector)
        self.cmb_sector.grid(row=2, column=3, padx=10, pady=4, sticky="ew")

        # Row 3: Tipo de Vínculo y Sueldo Base
        ttk.Label(self.frame_form, text="Vínculo Laboral:").grid(row=3, column=0, padx=10, pady=4, sticky="w")
        self.cmb_vinculo = ttk.Combobox(self.frame_form, values=TIPOS_VINCULO, state="readonly")
        self.cmb_vinculo.set("Planta")
        self.cmb_vinculo.grid(row=3, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Sueldo Base ($):").grid(row=3, column=2, padx=10, pady=4, sticky="w")
        self.txt_sueldo = ttk.Entry(self.frame_form)
        self.txt_sueldo.grid(row=3, column=3, padx=10, pady=4, sticky="ew")

        # Row 4: Teléfono y Email
        ttk.Label(self.frame_form, text="Teléfono:").grid(row=4, column=0, padx=10, pady=4, sticky="w")
        self.txt_telefono = ttk.Entry(self.frame_form)
        self.txt_telefono.grid(row=4, column=1, padx=10, pady=4, sticky="ew")

        ttk.Label(self.frame_form, text="Email:").grid(row=4, column=2, padx=10, pady=4, sticky="w")
        self.txt_email = ttk.Entry(self.frame_form)
        self.txt_email.grid(row=4, column=3, padx=10, pady=4, sticky="ew")

        # Row 5: Botonera
        frame_botones = ttk.Frame(self.frame_form)
        frame_botones.grid(row=5, column=0, columnspan=4, pady=10, sticky="w")

        self.btn_guardar = ttk.Button(
            frame_botones,
            text="Guardar datos",
            command=self._guardar_empleado
        )
        self.btn_guardar.pack(side="left", padx=(10, 5))

        self.btn_limpiar = ttk.Button(
            frame_botones,
            text="Limpiar Formulario",
            command=self._limpiar_formulario
        )
        self.btn_limpiar.pack(side="left", padx=5)

    def _crear_panel_tabla(self):
        frame_tabla = ttk.LabelFrame(self, text=" Nómina de Personal ")
        frame_tabla.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(1, weight=1)

        frame_filtro = ttk.Frame(frame_tabla)
        frame_filtro.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(frame_filtro, text="Buscar:").pack(side="left", padx=(0, 5))
        self.txt_buscar = ttk.Entry(frame_filtro)
        self.txt_buscar.pack(side="left", fill="x", expand=True, padx=5)
        self.txt_buscar.bind("<KeyRelease>", self._al_buscar_tecla)

        self.var_inactivos = tk.BooleanVar(value=False)
        self.chk_inactivos = ttk.Checkbutton(
            frame_filtro,
            text="Mostrar Inactivos",
            variable=self.var_inactivos,
            command=self._cargar_tabla
        )
        self.chk_inactivos.pack(side="right", padx=10)

        columnas = ("id", "legajo", "cuit", "nombre", "cargo", "sector", "vinculo", "sueldo", "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=6)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("legajo", text="Legajo")
        self.tabla.heading("cuit", text="CUIT / CUIL")
        self.tabla.heading("nombre", text="Nombre Completo")
        self.tabla.heading("cargo", text="Cargo")
        self.tabla.heading("sector", text="Sector")
        self.tabla.heading("vinculo", text="Vínculo")
        self.tabla.heading("sueldo", text="Sueldo Base")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=30, anchor="center")
        self.tabla.column("legajo", width=80, anchor="center")
        self.tabla.column("cuit", width=120, anchor="center")
        self.tabla.column("nombre", width=180, anchor="w")
        self.tabla.column("cargo", width=120, anchor="w")
        self.tabla.column("sector", width=100, anchor="w")
        self.tabla.column("vinculo", width=90, anchor="center")
        self.tabla.column("sueldo", width=90, anchor="e")
        self.tabla.column("estado", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="nsew")
        scrollbar.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="ns")

        self.tabla.bind("<Double-1>", self._al_doble_click_tabla)

        frame_acciones_tabla = ttk.Frame(frame_tabla)
        frame_acciones_tabla.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

        btn_editar = ttk.Button(
            frame_acciones_tabla,
            text="Editar Seleccionado",
            command=self._cargar_seleccion_formulario
        )
        btn_editar.pack(side="left", padx=5)

        btn_estado = ttk.Button(
            frame_acciones_tabla,
            text="Activar/Desactivar",
            command=self._alternar_estado_empleado
        )
        btn_estado.pack(side="left", padx=5)

    def _actualizar_legajo_sugerido(self):
        self.txt_legajo.config(state="normal")
        self.txt_legajo.delete(0, "end")
        if self.empleado_edicion_id is None:
            siguiente = RepositorioRRHH.generar_siguiente_legajo()
            self.txt_legajo.insert(0, siguiente)
        self.txt_legajo.config(state="disabled")

    def _al_buscar_tecla(self, _event):
        self._cargar_tabla()

    def _cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        criterio = self.txt_buscar.get().strip() if hasattr(self, 'txt_buscar') else ""
        incluir_inactivos = self.var_inactivos.get() if hasattr(self, 'var_inactivos') else False

        empleados: List[Empleado] = RepositorioRRHH.listar_empleados(
            criterio_busqueda=criterio,
            incluir_inactivos=incluir_inactivos
        )

        for emp in empleados:
            estado_txt = "Activo" if emp.activo else "Inactivo"
            nombre_completo = f"{emp.apellidos}, {emp.nombres}" if emp.apellidos and emp.nombres else (
                        emp.nombres or "")
            cuit_formateado = formatear_cuit(emp.nro_documento)

            self.tabla.insert("", "end", values=(
                emp.id_empleado,
                emp.legajo,
                cuit_formateado,
                nombre_completo,
                emp.cargo,
                emp.sector,
                emp.tipo_vinculo,
                f"$ {emp.sueldo:,.2f}",
                estado_txt
            ))

    def _limpiar_formulario(self):
        self.empleado_edicion_id = None
        self.txt_nombres.delete(0, "end")
        self.txt_apellidos.delete(0, "end")
        self.txt_documento.delete(0, "end")
        self.txt_sueldo.delete(0, "end")
        self.txt_telefono.delete(0, "end")
        self.txt_email.delete(0, "end")

        default_cargo = "empleado_ventas" if "empleado_ventas" in CARGOS else CARGOS[0]
        default_sector = "Ventas" if "Ventas" in SECTORES else SECTORES[0]

        self.cmb_cargo.set(default_cargo)
        self.cmb_sector.set(default_sector)
        self.cmb_vinculo.set("Planta")
        self.btn_guardar.configure(text="Guardar datos")

        self._actualizar_legajo_sugerido()

    def _guardar_empleado(self):
        nombres = self.txt_nombres.get().strip()
        apellidos = self.txt_apellidos.get().strip()
        cuit_raw = self.txt_documento.get().strip()
        cuit_limpio = limpiar_documento(cuit_raw)

        self.txt_legajo.config(state="normal")
        legajo = self.txt_legajo.get().strip()
        self.txt_legajo.config(state="disabled")

        sueldo_str = self.txt_sueldo.get().strip()

        if not nombres or not apellidos:
            messagebox.showwarning("Atención", "Nombres y Apellidos son obligatorios.")
            return

        if not cuit_limpio or len(cuit_limpio) != 11 or not cuit_limpio.isdigit():
            messagebox.showwarning("Atención",
                                   "Ingrese un número de CUIT / CUIL válido de 11 dígitos numéricos sin puntos ni guiones.")
            return

        id_persona_ref = None
        if self.empleado_edicion_id:
            for emp in RepositorioRRHH.listar_empleados(incluir_inactivos=True):
                if emp.id_empleado == self.empleado_edicion_id:
                    id_persona_ref = emp.id
                    break

        if RepositorioRRHH.existe_documento(cuit_limpio, id_persona_actual=id_persona_ref):
            messagebox.showerror("Error",
                                 f"El CUIT/CUIL '{formatear_cuit(cuit_limpio)}' ya está registrado en la base de datos.")
            return

        try:
            sueldo = float(sueldo_str) if sueldo_str else 0.0
        except ValueError:
            messagebox.showerror("Error", "El sueldo debe ser un valor numérico decimal válido.")
            return

        emp = Empleado(
            id_empleado=self.empleado_edicion_id,
            id_persona=id_persona_ref,
            nro_documento=cuit_limpio,
            nombres=nombres,
            apellidos=apellidos,
            legajo=legajo,
            cargo=self.cmb_cargo.get(),
            sector=self.cmb_sector.get(),
            tipo_vinculo=self.cmb_vinculo.get(),
            sueldo=sueldo,
            telefono=self.txt_telefono.get().strip(),
            email=self.txt_email.get().strip()
        )

        if self.empleado_edicion_id:
            exito = RepositorioRRHH.actualizar_empleado(emp)
            msg = "Empleado actualizado correctamente."
        else:
            exito = RepositorioRRHH.crear_empleado(emp)
            msg = "Empleado registrado con éxito."

        if exito:
            messagebox.showinfo("Éxito", msg)
            self._limpiar_formulario()
            self._cargar_tabla()
        else:
            messagebox.showerror("Error", "Ocurrió un fallo en la operación de base de datos.")

    def _cargar_seleccion_formulario(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un empleado de la lista para editar.")
            return

        valores = self.tabla.item(seleccion[0], "values")
        id_empleado = int(valores[0])

        empleados = RepositorioRRHH.listar_empleados(incluir_inactivos=True)
        emp_sel = next((e for e in empleados if e.id_empleado == id_empleado), None)

        if emp_sel:
            self._limpiar_formulario()
            self.empleado_edicion_id = emp_sel.id_empleado
            self.txt_nombres.insert(0, emp_sel.nombres or "")
            self.txt_apellidos.insert(0, emp_sel.apellidos or "")
            self.txt_documento.insert(0, emp_sel.nro_documento or "")

            self.txt_legajo.config(state="normal")
            self.txt_legajo.delete(0, "end")
            self.txt_legajo.insert(0, emp_sel.legajo or "")
            self.txt_legajo.config(state="disabled")

            self.txt_sueldo.insert(0, str(emp_sel.sueldo or 0.0))
            self.txt_telefono.insert(0, emp_sel.telefono or "")
            self.txt_email.insert(0, emp_sel.email or "")

            if emp_sel.cargo in CARGOS:
                self.cmb_cargo.set(emp_sel.cargo)
            if emp_sel.sector in SECTORES:
                self.cmb_sector.set(emp_sel.sector)
            if emp_sel.tipo_vinculo in TIPOS_VINCULO:
                self.cmb_vinculo.set(emp_sel.tipo_vinculo)

            self.btn_guardar.configure(text="Guardar datos")

    def _al_doble_click_tabla(self, _event):
        self._cargar_seleccion_formulario()

    def _alternar_estado_empleado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un empleado para cambiar su estado.")
            return

        valores = self.tabla.item(seleccion[0], "values")
        id_empleado = int(valores[0])
        estado_actual = valores[8]

        nuevo_estado = 0 if estado_actual == "Activo" else 1
        accion_str = "desactivar" if nuevo_estado == 0 else "activar"

        if messagebox.askyesno("Confirmar", f"¿Desea {accion_str} al empleado seleccionado?"):
            if RepositorioRRHH.cambiar_estado_empleado(id_empleado, nuevo_estado):
                messagebox.showinfo("Éxito", f"Empleado {accion_str}do correctamente.")
                self._cargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo cambiar el estado en la base de datos.")