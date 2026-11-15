"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: LIQUIDACIÓN DE HABERES (vistas/ui_haberes.py)
===============================================================================
Permite calcular los haberes remunerativos, deducciones y neto a cobrar
de un empleado, conectando la vista con el RepositorioHaberes y RepositorioRRHH.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from infraestructura.repo_rrhh import RepositorioRRHH
from infraestructura.repo_haberes import RepositorioHaberes


class InterfazHaberes(ttk.Frame):
    """
    Componente visual modular basado en ttk.Frame para la liquidación de haberes.
    """

    def __init__(self, parent: tk.Widget, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)

        self.empleados_lista = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._crear_encabezado()
        self._crear_panel_seleccion()
        self._crear_panel_conceptos()
        self._cargar_empleados()

    def _crear_encabezado(self) -> None:
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        lbl_titulo = ttk.Label(
            frame_top,
            text="Liquidación de Haberes y Nómina",
            font=("Segoe UI", 12, "bold")
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ttk.Label(
            frame_top,
            text="Cálculo automático de haberes, aportes de ley y persistencia en base de datos"
        )
        lbl_subtitulo.pack(anchor="w")

    def _crear_panel_seleccion(self) -> None:
        frame_sel = ttk.LabelFrame(self, text=" Selección de Empleado y Período ")
        frame_sel.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame_sel.columnconfigure(1, weight=1)

        ttk.Label(frame_sel, text="Empleado *:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.cmb_empleados = ttk.Combobox(frame_sel, state="readonly")
        self.cmb_empleados.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.cmb_empleados.bind("<<ComboboxSelected>>", self._al_seleccionar_empleado)

        ttk.Label(frame_sel, text="Período (AAAA-MM) *:").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.txt_periodo = ttk.Entry(frame_sel)
        self.txt_periodo.insert(0, "2026-10")
        self.txt_periodo.grid(row=0, column=3, padx=10, pady=8, sticky="ew")

    def _crear_panel_conceptos(self) -> None:
        frame_main = ttk.Frame(self)
        frame_main.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_main.columnconfigure((0, 1), weight=1)
        frame_main.rowconfigure(0, weight=1)

        # Panel Izquierdo: Variables de Entrada
        frame_izq = ttk.LabelFrame(frame_main, text=" Variables de Entrada Laboral ")
        frame_izq.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        frame_izq.columnconfigure(1, weight=1)

        ttk.Label(frame_izq, text="Salario Básico ($):").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.txt_basico = ttk.Entry(frame_izq)
        self.txt_basico.insert(0, "0.00")
        self.txt_basico.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Años de Antigüedad:").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.txt_antiguedad = ttk.Entry(frame_izq)
        self.txt_antiguedad.insert(0, "0")
        self.txt_antiguedad.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        self.var_presentismo = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_izq, text="Aplicar Presentismo (8,33%)", variable=self.var_presentismo).grid(
            row=2, column=0, columnspan=2, padx=10, pady=6, sticky="w"
        )

        ttk.Label(frame_izq, text="Horas Extra (Cant.):").grid(row=3, column=0, padx=10, pady=6, sticky="w")
        self.txt_horas = ttk.Entry(frame_izq)
        self.txt_horas.insert(0, "0")
        self.txt_horas.grid(row=3, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Feriados Trabajados (Cant.):").grid(row=4, column=0, padx=10, pady=6, sticky="w")
        self.txt_feriados = ttk.Entry(frame_izq)
        self.txt_feriados.insert(0, "0")
        self.txt_feriados.grid(row=4, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Ventas Realizadas ($):").grid(row=5, column=0, padx=10, pady=6, sticky="w")
        self.txt_ventas = ttk.Entry(frame_izq)
        self.txt_ventas.insert(0, "0.00")
        self.txt_ventas.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Adelanto de Haberes ($):").grid(row=6, column=0, padx=10, pady=6, sticky="w")
        self.txt_adelanto = ttk.Entry(frame_izq)
        self.txt_adelanto.insert(0, "0.00")
        self.txt_adelanto.grid(row=6, column=1, padx=10, pady=6, sticky="ew")

        # Panel Derecho: Deducciones y Resultados
        frame_der = ttk.LabelFrame(frame_main, text=" Deducciones de Ley y Totales ")
        frame_der.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        frame_der.columnconfigure(1, weight=1)

        self.var_jub = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Jubilación (11%)", variable=self.var_jub).grid(row=0, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_pami = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="PAMI (3%)", variable=self.var_pami).grid(row=1, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_obrasocial = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Obra Social (3%)", variable=self.var_obrasocial).grid(row=2, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_sindicato = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Cuota Sindical (2,5%)", variable=self.var_sindicato).grid(row=3, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        btn_calcular = ttk.Button(frame_der, text="Calcular y Guardar Liquidación", command=self._procesar_calculo)
        btn_calcular.grid(row=4, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        self.lbl_res_rem = ttk.Label(frame_der, text="Total Remunerativo: $ 0.00")
        self.lbl_res_rem.grid(row=5, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_desc = ttk.Label(frame_der, text="Total Deducciones: $ 0.00")
        self.lbl_res_desc.grid(row=6, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_neto = ttk.Label(frame_der, text="NETO A COBRAR: $ 0.00", font=("Segoe UI", 11, "bold"))
        self.lbl_res_neto.grid(row=7, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="w")

    def _cargar_empleados(self) -> None:
        try:
            self.empleados_lista = RepositorioRRHH.listar_empleados(incluir_inactivos=False)
            valores = [
                f"{int(getattr(e, 'id_empleado', 0) or 0)} - {getattr(e, 'apellidos', '')}, {getattr(e, 'nombres', '')} ({getattr(e, 'cargo', '')})"
                for e in self.empleados_lista
            ]
            self.cmb_empleados['values'] = valores
            if valores:
                self.cmb_empleados.current(0)
                self._al_seleccionar_empleado(None)
        except Exception as err:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados: {err}")

    def _al_seleccionar_empleado(self, _event: Any) -> None:
        idx = self.cmb_empleados.current()
        if idx < 0 or not self.empleados_lista:
            return
        emp = self.empleados_lista[idx]
        sueldo_val = getattr(emp, "sueldo", 0.0)
        if sueldo_val is not None:
            self.txt_basico.delete(0, "end")
            self.txt_basico.insert(0, f"{float(sueldo_val):.2f}")

    def _procesar_calculo(self) -> None:
        try:
            idx = self.cmb_empleados.current()
            if idx < 0:
                messagebox.showwarning("Atención", "Debe seleccionar un empleado.")
                return

            emp = self.empleados_lista[idx]
            id_emp_raw = getattr(emp, "id_empleado", 0)
            if not id_emp_raw:
                messagebox.showerror("Error", "El empleado seleccionado no posee un ID válido.")
                return

            # Casteo estricto tipado para satisfacer plenamente al IDE
            id_emp_seguro: int = int(str(id_emp_raw))

            res = RepositorioHaberes.calcular_liquidacion(
                id_empleado=id_emp_seguro,
                periodo=self.txt_periodo.get().strip(),
                basico=float(self.txt_basico.get() or 0),
                antiguedad_anios=int(self.txt_antiguedad.get() or 0),
                aplica_presentismo=self.var_presentismo.get(),
                horas_extra=float(self.txt_horas.get() or 0),
                feriados=float(self.txt_feriados.get() or 0),
                ventas=float(self.txt_ventas.get() or 0),
                adelanto=float(self.txt_adelanto.get() or 0),
                aplica_jubilacion=self.var_jub.get(),
                aplica_pami=self.var_pami.get(),
                aplica_obra_social=self.var_obrasocial.get(),
                aplica_sindicato=self.var_sindicato.get()
            )

            self.lbl_res_rem.config(text=f"Total Remunerativo: $ {res['remunerativo']:,.2f}")
            self.lbl_res_desc.config(text=f"Total Deducciones: $ {res['descuentos']:,.2f}")
            self.lbl_res_neto.config(text=f"NETO A COBRAR: $ {res['neto']:,.2f}")

            messagebox.showinfo("Éxito", "Liquidación calculada y persistida correctamente en la base de datos.")

        except ValueError:
            messagebox.showerror("Error de Formato", "Verifique que los valores numéricos ingresados sean correctos.")
        except Exception as err:
            messagebox.showerror("Error", f"Ocurrió un error al procesar el cálculo: {err}")