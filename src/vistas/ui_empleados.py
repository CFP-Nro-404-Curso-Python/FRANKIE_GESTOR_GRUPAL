"""
Módulo de Interfaz Gráfica: Gestión de Empleados (Recursos Humanos)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dominio.entidades_rrhh import Empleado
from infraestructura.repo_rrhh import RepositorioRRHH
from vistas.estilos import aplicar_estilos_base


def es_cuit_cuil_valido(doc_raw: str) -> bool:
    """ Verifica que contenga exactamente 11 dígitos numéricos (rechaza DNI de 8 dígitos). """
    num_limpio = "".join(
        caracter for caracter in str(doc_raw or "") if caracter.isdigit())
    return len(num_limpio) == 11


def formatear_cuit(doc_raw: str) -> str:
    """ Formatea una cadena de 11 dígitos al formato XX-XXXXXXXX-X. """
    num_limpio = "".join(
        caracter for caracter in str(doc_raw or "") if caracter.isdigit())
    if len(num_limpio) == 11:
        return f"{num_limpio[:2]}-{num_limpio[2:10]}-{num_limpio[10]}"
    return num_limpio


class ModuloEmpleadosUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill="both", expand=True, padx=15, pady=15)

        self.empleado_seleccionado_id = None
        self.persona_seleccionada_id = None
        self.empleado_estado_activo = True

        self.var_documento = tk.StringVar()
        self.var_nombres = tk.StringVar()
        self.var_apellidos = tk.StringVar()
        self.var_legajo = tk.StringVar()
        self.var_cargo = tk.StringVar()
        self.var_sector = tk.StringVar()
        self.var_sueldo = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telefono = tk.StringVar()

        self.var_busqueda = tk.StringVar()
        self.var_mostrar_inactivos = tk.BooleanVar(value=False)

        self._crear_interfaz()
        self.cargar_tabla_empleados()
        self.sugerir_siguiente_legajo()

    def _crear_interfaz(self):
        # --- Formulario ---
        self.frame_form = ttk.LabelFrame(self,
                                         text=" Registrar / Editar Empleado ",
                                         padding=12)
        self.frame_form.pack(fill="x", pady=(0, 10))

        ttk.Label(self.frame_form, text="CUIL / CUIT (11 dígitos) *:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        entry_doc = ttk.Entry(self.frame_form, textvariable=self.var_documento)
        entry_doc.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        entry_doc.bind("<FocusOut>", self._al_perder_foco_documento)

        ttk.Label(self.frame_form, text="Legajo (Auto):").grid(row=0, column=2,
                                                               sticky="w",
                                                               padx=5, pady=5)
        entry_legajo = ttk.Entry(self.frame_form, textvariable=self.var_legajo,
                                 state="readonly")
        entry_legajo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(self.frame_form, text="Nombres *:").grid(row=1, column=0,
                                                           sticky="w", padx=5,
                                                           pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_nombres).grid(row=1,
                                                                       column=1,
                                                                       sticky="ew",
                                                                       padx=5,
                                                                       pady=5)

        ttk.Label(self.frame_form, text="Apellidos *:").grid(row=1, column=2,
                                                             sticky="w", padx=5,
                                                             pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_apellidos).grid(row=1,
                                                                         column=3,
                                                                         sticky="ew",
                                                                         padx=5,
                                                                         pady=5)

        ttk.Label(self.frame_form, text="Cargo *:").grid(row=2, column=0,
                                                         sticky="w", padx=5,
                                                         pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_cargo).grid(row=2,
                                                                     column=1,
                                                                     sticky="ew",
                                                                     padx=5,
                                                                     pady=5)

        ttk.Label(self.frame_form, text="Sector *:").grid(row=2, column=2,
                                                          sticky="w", padx=5,
                                                          pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_sector).grid(row=2,
                                                                      column=3,
                                                                      sticky="ew",
                                                                      padx=5,
                                                                      pady=5)

        ttk.Label(self.frame_form, text="Sueldo Base ($) *:").grid(row=3,
                                                                   column=0,
                                                                   sticky="w",
                                                                   padx=5,
                                                                   pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_sueldo).grid(row=3,
                                                                      column=1,
                                                                      sticky="ew",
                                                                      padx=5,
                                                                      pady=5)

        ttk.Label(self.frame_form, text="Email *:").grid(row=3, column=2,
                                                         sticky="w", padx=5,
                                                         pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_email).grid(row=3,
                                                                     column=3,
                                                                     sticky="ew",
                                                                     padx=5,
                                                                     pady=5)

        ttk.Label(self.frame_form, text="Teléfono *:").grid(row=4, column=0,
                                                            sticky="w", padx=5,
                                                            pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_telefono).grid(row=4,
                                                                        column=1,
                                                                        sticky="ew",
                                                                        padx=5,
                                                                        pady=5)

        frame_acciones_form = ttk.Frame(self.frame_form)
        frame_acciones_form.grid(row=4, column=2, columnspan=2, sticky="e",
                                 padx=5, pady=5)

        self.btn_limpiar = ttk.Button(frame_acciones_form,
                                      text="Nuevo / Limpiar",
                                      command=self.limpiar_formulario)
        self.btn_limpiar.pack(side="left", padx=3)

        self.btn_toggle_estado = ttk.Button(frame_acciones_form,
                                            text="Deshabilitar",
                                            command=self.toggle_estado_empleado,
                                            state="disabled")
        self.btn_toggle_estado.pack(side="left", padx=3)

        self.btn_guardar = ttk.Button(frame_acciones_form,
                                      text="Guardar Empleado",
                                      command=self.guardar_empleado)
        self.btn_guardar.pack(side="left", padx=3)

        for col in range(4):
            self.frame_form.columnconfigure(col, weight=1)

        entry_doc.focus_set()

        # --- Tabla de Listado ---
        frame_tabla = ttk.LabelFrame(self, text=" Listado de Empleados ",
                                     padding=12)
        frame_tabla.pack(fill="both", expand=True)

        frame_buscar = ttk.Frame(frame_tabla)
        frame_buscar.pack(fill="x", pady=(0, 8))

        ttk.Label(frame_buscar, text="Buscar:").pack(side="left", padx=(0, 5))
        entry_buscar = ttk.Entry(frame_buscar, textvariable=self.var_busqueda)
        entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        entry_buscar.bind("<KeyRelease>",
                          lambda e: self.cargar_tabla_empleados())

        chk_inactivos = ttk.Checkbutton(
            frame_buscar,
            text="Mostrar inactivos",
            variable=self.var_mostrar_inactivos,
            command=self.cargar_tabla_empleados
        )
        chk_inactivos.pack(side="right", padx=(5, 0))

        # Incluimos Email y Teléfono directamente en la vista
        columnas = ("id", "legajo", "nombre", "documento", "cargo", "sector",
                    "sueldo", "email", "telefono", "estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas,
                                  show="headings", height=7)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("legajo", text="Legajo")
        self.tabla.heading("nombre", text="Nombre Completo")
        self.tabla.heading("documento", text="CUIL / CUIT")
        self.tabla.heading("cargo", text="Cargo")
        self.tabla.heading("sector", text="Sector")
        self.tabla.heading("sueldo", text="Sueldo")
        self.tabla.heading("email", text="Email")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=35, anchor="center")
        self.tabla.column("legajo", width=75, anchor="center")
        self.tabla.column("nombre", width=150, anchor="w")
        self.tabla.column("documento", width=110, anchor="center")
        self.tabla.column("cargo", width=90, anchor="w")
        self.tabla.column("sector", width=90, anchor="w")
        self.tabla.column("sueldo", width=80, anchor="e")
        self.tabla.column("email", width=140, anchor="w")
        self.tabla.column("telefono", width=100, anchor="w")
        self.tabla.column("estado", width=65, anchor="center")

        scrollbar_v = ttk.Scrollbar(frame_tabla, orient="vertical",
                                    command=self.tabla.yview)
        scrollbar_h = ttk.Scrollbar(frame_tabla, orient="horizontal",
                                    command=self.tabla.xview)

        self.tabla.configure(yscrollcommand=scrollbar_v.set,
                             xscrollcommand=scrollbar_h.set)

        self.tabla.pack(side="top", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")

        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def _al_perder_foco_documento(self, event=None):
        doc_actual = self.var_documento.get().strip()
        if doc_actual and es_cuit_cuil_valido(doc_actual):
            self.var_documento.set(formatear_cuit(doc_actual))

    def sugerir_siguiente_legajo(self):
        siguiente = RepositorioRRHH.generar_siguiente_legajo()
        self.var_legajo.set(siguiente)

    def _al_seleccionar_fila(self, event=None):
        item_sel = self.tabla.selection()
        if not item_sel:
            return

        valores = self.tabla.item(item_sel[0], "values")
        if not valores:
            return

        id_emp = str(valores[0])
        empleados = RepositorioRRHH.listar_empleados(
            criterio_busqueda=self.var_busqueda.get().strip(),
            incluir_inactivos=True
        )
        emp_encontrado = next(
            (e for e in empleados if str(e.id_empleado) == id_emp), None)

        if emp_encontrado:
            self.empleado_seleccionado_id = emp_encontrado.id_empleado
            self.persona_seleccionada_id = emp_encontrado.id
            self.empleado_estado_activo = getattr(emp_encontrado, "activo",
                                                  True)

            self.var_documento.set(formatear_cuit(emp_encontrado.nro_documento))
            self.var_nombres.set(emp_encontrado.nombres or "")
            self.var_apellidos.set(emp_encontrado.apellidos or "")
            self.var_legajo.set(emp_encontrado.legajo or "")
            self.var_cargo.set(emp_encontrado.cargo or "")
            self.var_sector.set(emp_encontrado.sector or "")
            self.var_sueldo.set(str(emp_encontrado.sueldo or ""))
            self.var_email.set(emp_encontrado.email or "")
            self.var_telefono.set(emp_encontrado.telefono or "")

            self.btn_guardar.config(text="Actualizar Empleado")
            self.btn_toggle_estado.config(
                state="normal",
                text="Deshabilitar" if self.empleado_estado_activo else "Reactivar"
            )

    def guardar_empleado(self):
        doc_ingresado = self.var_documento.get().strip()
        nom_ingresado = self.var_nombres.get().strip()
        ape_ingresado = self.var_apellidos.get().strip()
        cargo_ingresado = self.var_cargo.get().strip()
        sector_ingresado = self.var_sector.get().strip()
        sueldo_ingresado = self.var_sueldo.get().strip()
        email_ingresado = self.var_email.get().strip()
        tel_ingresado = self.var_telefono.get().strip()

        # --- VALIDACIÓN DE CAMPOS OBLIGATORIOS ---
        if not all(
                [doc_ingresado, nom_ingresado, ape_ingresado, cargo_ingresado,
                 sector_ingresado, sueldo_ingresado, email_ingresado,
                 tel_ingresado]):
            messagebox.showwarning("Campos Incompletos",
                                   "Todos los campos con (*) son obligatorios. Por favor, complete la información.")
            return

        # --- VALIDACIÓN ESTRICTA DE CUIL / CUIT ---
        if not es_cuit_cuil_valido(doc_ingresado):
            messagebox.showerror(
                "CUIL / CUIT Inválido",
                "El módulo requiere obligatoriamente un CUIL o CUIT de 11 dígitos (ejemplo: 20-12345678-9).\n\n"
                "No se permite el ingreso de DNI simple (8 dígitos)."
            )
            return

        # Formatemos a XX-XXXXXXXX-X
        doc_formateado = formatear_cuit(doc_ingresado)

        # Validar duplicados de CUIL/CUIT
        if RepositorioRRHH.existe_documento(doc_formateado,
                                            id_persona_actual=self.persona_seleccionada_id):
            messagebox.showerror("CUIL/CUIT Duplicado",
                                 f"El CUIL/CUIT {doc_formateado} ya está registrado a nombre de otro empleado.")
            return

        try:
            sueldo_val = float(sueldo_ingresado)
        except ValueError:
            messagebox.showerror("Error de Formato",
                                 "El sueldo debe ser un valor numérico válido.")
            return

        legajo_final = self.var_legajo.get().strip() or RepositorioRRHH.generar_siguiente_legajo()

        nuevo_emp = Empleado(
            id_empleado=self.empleado_seleccionado_id,
            id_persona=self.persona_seleccionada_id,
            nro_documento=doc_formateado,
            nombres=nom_ingresado,
            apellidos=ape_ingresado,
            legajo=legajo_final,
            cargo=cargo_ingresado,
            sector=sector_ingresado,
            sueldo=sueldo_val,
            email=email_ingresado,
            telefono=tel_ingresado
        )

        if self.empleado_seleccionado_id:
            exito = RepositorioRRHH.actualizar_empleado(nuevo_emp)
            msj_exito = "Empleado actualizado correctamente."
        else:
            exito = RepositorioRRHH.crear_empleado(nuevo_emp)
            msj_exito = "Empleado registrado correctamente."

        if exito:
            messagebox.showinfo("Éxito", msj_exito)
            self.limpiar_formulario()
            self.cargar_tabla_empleados()
        else:
            messagebox.showerror("Error",
                                 "No se pudo completar la operación en la base de datos.")

    def toggle_estado_empleado(self):
        if not self.empleado_seleccionado_id:
            return

        nuevo_estado = 0 if self.empleado_estado_activo else 1
        accion_texto = "deshabilitar" if self.empleado_estado_activo else "reactivar"

        confirmar = messagebox.askyesno(
            "Confirmación",
            f"¿Está seguro de que desea {accion_texto} a este empleado?"
        )

        if confirmar:
            exito = RepositorioRRHH.cambiar_estado_empleado(
                self.empleado_seleccionado_id, nuevo_estado)
            if exito:
                messagebox.showinfo("Éxito",
                                    f"El empleado ha sido {accion_texto}do.")
                self.limpiar_formulario()
                self.cargar_tabla_empleados()
            else:
                messagebox.showerror("Error",
                                     f"No se pudo {accion_texto} al empleado.")

    def limpiar_formulario(self):
        self.empleado_seleccionado_id = None
        self.persona_seleccionada_id = None
        self.empleado_estado_activo = True
        self.var_documento.set("")
        self.var_nombres.set("")
        self.var_apellidos.set("")
        self.var_cargo.set("")
        self.var_sector.set("")
        self.var_sueldo.set("")
        self.var_email.set("")
        self.var_telefono.set("")
        self.btn_guardar.config(text="Guardar Empleado")
        self.btn_toggle_estado.config(text="Deshabilitar", state="disabled")
        self.sugerir_siguiente_legajo()

    def cargar_tabla_empleados(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        criterio = self.var_busqueda.get().strip()
        mostrar_inactivos = self.var_mostrar_inactivos.get()

        empleados = RepositorioRRHH.listar_empleados(
            criterio_busqueda=criterio,
            incluir_inactivos=mostrar_inactivos
        )

        for emp in empleados:
            estado_txt = "Activo" if getattr(emp, "activo",
                                             True) else "Inactivo"
            self.tabla.insert("", "end", values=(
                emp.id_empleado,
                emp.legajo,
                emp.obtener_nombre_completo(),
                formatear_cuit(emp.nro_documento),
                emp.cargo,
                emp.sector,
                f"$ {emp.sueldo:,.2f}",
                emp.email or "-",
                emp.telefono or "-",
                estado_txt
            ))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Frankie Gestor - Módulo de RRHH")
    root.geometry("1000x650")

    aplicar_estilos_base(root)

    app = ModuloEmpleadosUI(root)
    root.mainloop()