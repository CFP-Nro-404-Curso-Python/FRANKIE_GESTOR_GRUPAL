"""
Módulo de Interfaz Gráfica: Gestión de Empleados (Recursos Humanos)
Estructura semántica conectada al repositorio y a la hoja de estilos compartida.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from dominio.entidades_rrhh import Empleado
from infraestructura.repo_rrhh import RepositorioRRHH
from vistas.estilos import aplicar_estilos_base


def formatear_cuit(doc_raw: str) -> str:
    """
    Toma un número de documento o CUIT/CUIL en formato numérico y devuelve
    la representación con guiones XX-XXXXXXXX-X.
    """
    num_limpio = "".join(
        caracter for caracter in str(doc_raw or "") if caracter.isdigit())
    if len(num_limpio) == 11:
        return f"{num_limpio[:2]}-{num_limpio[2:10]}-{num_limpio[10]}"
    return num_limpio


class ModuloEmpleadosUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.pack(fill="both", expand=True, padx=15, pady=15)

        # Estado interno para edición
        self.empleado_seleccionado_id = None
        self.persona_seleccionada_id = None

        # Variables asociadas al formulario
        self.var_documento = tk.StringVar()
        self.var_nombres = tk.StringVar()
        self.var_apellidos = tk.StringVar()
        self.var_legajo = tk.StringVar()
        self.var_cargo = tk.StringVar()
        self.var_sector = tk.StringVar()
        self.var_sueldo = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_telefono = tk.StringVar()

        # Variable de búsqueda
        self.var_busqueda = tk.StringVar()

        self._crear_interfaz()
        self.cargar_tabla_empleados()
        self.sugerir_siguiente_legajo()

    def _crear_interfaz(self):
        # --- SECCIÓN 1: Formulario de Registro / Edición ---
        self.frame_form = ttk.LabelFrame(self,
                                         text=" Registrar / Editar Empleado ",
                                         padding=12)
        self.frame_form.pack(fill="x", pady=(0, 10))

        # Fila 0
        ttk.Label(self.frame_form, text="Nro. Documento/CUIT *:").grid(row=0,
                                                                       column=0,
                                                                       sticky="w",
                                                                       padx=5,
                                                                       pady=5)
        entry_doc = ttk.Entry(self.frame_form, textvariable=self.var_documento)
        entry_doc.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        entry_doc.bind("<FocusOut>", self._al_perder_foco_documento)

        ttk.Label(self.frame_form, text="Legajo:").grid(row=0, column=2,
                                                        sticky="w", padx=5,
                                                        pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_legajo).grid(row=0,
                                                                      column=3,
                                                                      sticky="ew",
                                                                      padx=5,
                                                                      pady=5)

        # Fila 1
        ttk.Label(self.frame_form, text="Nombres *:").grid(row=1, column=0,
                                                           sticky="w", padx=5,
                                                           pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_nombres).grid(row=1,
                                                                       column=1,
                                                                       sticky="ew",
                                                                       padx=5,
                                                                       pady=5)

        ttk.Label(self.frame_form, text="Apellidos:").grid(row=1, column=2,
                                                           sticky="w", padx=5,
                                                           pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_apellidos).grid(row=1,
                                                                         column=3,
                                                                         sticky="ew",
                                                                         padx=5,
                                                                         pady=5)

        # Fila 2
        ttk.Label(self.frame_form, text="Cargo:").grid(row=2, column=0,
                                                       sticky="w", padx=5,
                                                       pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_cargo).grid(row=2,
                                                                     column=1,
                                                                     sticky="ew",
                                                                     padx=5,
                                                                     pady=5)

        ttk.Label(self.frame_form, text="Sector:").grid(row=2, column=2,
                                                        sticky="w", padx=5,
                                                        pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_sector).grid(row=2,
                                                                      column=3,
                                                                      sticky="ew",
                                                                      padx=5,
                                                                      pady=5)

        # Fila 3
        ttk.Label(self.frame_form, text="Sueldo Base ($):").grid(row=3,
                                                                 column=0,
                                                                 sticky="w",
                                                                 padx=5, pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_sueldo).grid(row=3,
                                                                      column=1,
                                                                      sticky="ew",
                                                                      padx=5,
                                                                      pady=5)

        ttk.Label(self.frame_form, text="Email:").grid(row=3, column=2,
                                                       sticky="w", padx=5,
                                                       pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_email).grid(row=3,
                                                                     column=3,
                                                                     sticky="ew",
                                                                     padx=5,
                                                                     pady=5)

        # Fila 4
        ttk.Label(self.frame_form, text="Teléfono:").grid(row=4, column=0,
                                                          sticky="w", padx=5,
                                                          pady=5)
        ttk.Entry(self.frame_form, textvariable=self.var_telefono).grid(row=4,
                                                                        column=1,
                                                                        sticky="ew",
                                                                        padx=5,
                                                                        pady=5)

        # Botones del formulario
        frame_acciones_form = ttk.Frame(self.frame_form)
        frame_acciones_form.grid(row=4, column=2, columnspan=2, sticky="e",
                                 padx=5, pady=5)

        self.btn_limpiar = ttk.Button(frame_acciones_form,
                                      text="Nuevo / Limpiar",
                                      command=self.limpiar_formulario)
        self.btn_limpiar.pack(side="left", padx=3)

        self.btn_deshabilitar = ttk.Button(frame_acciones_form,
                                           text="Deshabilitar",
                                           command=self.deshabilitar_empleado,
                                           state="disabled")
        self.btn_deshabilitar.pack(side="left", padx=3)

        self.btn_guardar = ttk.Button(frame_acciones_form,
                                      text="Guardar Empleado",
                                      command=self.guardar_empleado)
        self.btn_guardar.pack(side="left", padx=3)

        for col in range(4):
            self.frame_form.columnconfigure(col, weight=1)

        entry_doc.focus_set()

        # --- SECCIÓN 2: Buscador y Tabla de Empleados ---
        frame_tabla = ttk.LabelFrame(self, text=" Listado de Empleados ",
                                     padding=12)
        frame_tabla.pack(fill="both", expand=True)

        # Barra de búsqueda
        frame_buscar = ttk.Frame(frame_tabla)
        frame_buscar.pack(fill="x", pady=(0, 8))

        ttk.Label(frame_buscar, text="Buscar:").pack(side="left", padx=(0, 5))
        entry_buscar = ttk.Entry(frame_buscar, textvariable=self.var_busqueda)
        entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        entry_buscar.bind("<KeyRelease>",
                          lambda e: self.cargar_tabla_empleados())

        # Tabla
        columnas = ("id", "legajo", "nombre", "documento", "cargo", "sector",
                    "sueldo")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas,
                                  show="headings", height=7)

        self.tabla.heading("id", text="ID")
        self.tabla.heading("legajo", text="Legajo")
        self.tabla.heading("nombre", text="Nombre Completo")
        self.tabla.heading("documento", text="Documento / CUIT")
        self.tabla.heading("cargo", text="Cargo")
        self.tabla.heading("sector", text="Sector")
        self.tabla.heading("sueldo", text="Sueldo")

        self.tabla.column("id", width=40, anchor="center")
        self.tabla.column("legajo", width=90, anchor="center")
        self.tabla.column("nombre", width=180, anchor="w")
        self.tabla.column("documento", width=130, anchor="center")
        self.tabla.column("cargo", width=110, anchor="w")
        self.tabla.column("sector", width=110, anchor="w")
        self.tabla.column("sueldo", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical",
                                  command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Doble clic en fila para cargar en formulario
        self.tabla.bind("<Double-1>", self._al_seleccionar_fila)

    def _al_perder_foco_documento(self, event=None):
        doc_actual = self.var_documento.get().strip()
        if doc_actual:
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

        id_emp = valores[0]
        empleados = RepositorioRRHH.listar_empleados()
        emp_encontrado = next(
            (e for e in empleados if str(e.id_empleado) == str(id_emp)), None)

        if emp_encontrado:
            self.empleado_seleccionado_id = emp_encontrado.id_empleado
            self.persona_seleccionada_id = emp_encontrado.id
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
            self.btn_deshabilitar.config(state="normal")

    def guardar_empleado(self):
        if not self.var_documento.get().strip() or not self.var_nombres.get().strip():
            messagebox.showwarning("Campos Requeridos",
                                   "Por favor complete los campos obligatorios (*).")
            return

        try:
            sueldo_val = float(
                self.var_sueldo.get().strip()) if self.var_sueldo.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Error de Formato",
                                 "El sueldo debe ser un número válido.")
            return

        legajo_final = self.var_legajo.get().strip() or RepositorioRRHH.generar_siguiente_legajo()

        nuevo_emp = Empleado(
            id_empleado=self.empleado_seleccionado_id,
            id_persona=self.persona_seleccionada_id,
            nro_documento=self.var_documento.get().strip(),
            nombres=self.var_nombres.get().strip(),
            apellidos=self.var_apellidos.get().strip(),
            legajo=legajo_final,
            cargo=self.var_cargo.get().strip() or "General",
            sector=self.var_sector.get().strip() or "Administración",
            sueldo=sueldo_val,
            email=self.var_email.get().strip(),
            telefono=self.var_telefono.get().strip()
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
                                 "No se pudo completar la operación en la BD.")

    def deshabilitar_empleado(self):
        if not self.empleado_seleccionado_id:
            return

        confirmar = messagebox.askyesno(
            "Confirmar Baja Lógica",
            "¿Está seguro de que desea deshabilitar este empleado?\nEl registro permanecerá en la base de datos pero no se mostrará en los listados activos."
        )

        if confirmar:
            exito = RepositorioRRHH.deshabilitar_empleado(
                self.empleado_seleccionado_id)
            if exito:
                messagebox.showinfo("Baja Lógica Exitosa",
                                    "El empleado ha sido deshabilitado.")
                self.limpiar_formulario()
                self.cargar_tabla_empleados()
            else:
                messagebox.showerror("Error",
                                     "No se pudo deshabilitar el empleado.")

    def limpiar_formulario(self):
        self.empleado_seleccionado_id = None
        self.persona_seleccionada_id = None
        self.var_documento.set("")
        self.var_nombres.set("")
        self.var_apellidos.set("")
        self.var_cargo.set("")
        self.var_sector.set("")
        self.var_sueldo.set("")
        self.var_email.set("")
        self.var_telefono.set("")
        self.btn_guardar.config(text="Guardar Empleado")
        self.btn_deshabilitar.config(state="disabled")
        self.sugerir_siguiente_legajo()

    def cargar_tabla_empleados(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        criterio = self.var_busqueda.get().strip()
        empleados = RepositorioRRHH.listar_empleados(criterio_busqueda=criterio)
        for emp in empleados:
            self.tabla.insert("", "end", values=(
                emp.id_empleado,
                emp.legajo,
                emp.obtener_nombre_completo(),
                formatear_cuit(emp.nro_documento),
                emp.cargo,
                emp.sector,
                f"$ {emp.sueldo:,.2f}"
            ))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Frankie Gestor - Módulo de RRHH")
    root.geometry("850x650")

    aplicar_estilos_base(root)

    app = ModuloEmpleadosUI(root)
    root.mainloop()