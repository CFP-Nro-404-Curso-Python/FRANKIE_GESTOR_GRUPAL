"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: LIQUIDACIÓN DE HABERES (iu_haberes.py)
===============================================================================
Incluye:
  - Formulario de cálculo de haberes.
  - Ventana emergente (Toplevel) para visualización e impresión rápida del recibo.
===============================================================================
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Configuración de sys.path para resolución de módulos
DIR_ACTUAL = Path(__file__).resolve().parent
RAIZ_PROYECTO = DIR_ACTUAL.parent

for path in (RAIZ_PROYECTO, DIR_ACTUAL):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Importación de infraestructura
from infraestructura.repo_rrhh import RepositorioRRHH
from infraestructura.repo_haberes import RepositorioHaberes

# Importación de estilos
try:
    from vista.estilos import aplicar_estilos_base, COLOR_TEXTO_MUTED
except ImportError:
    try:
        from estilos import aplicar_estilos_base, COLOR_TEXTO_MUTED
    except ImportError:
        COLOR_TEXTO_MUTED = "#6c757d"

        def aplicar_estilos_base(_root: tk.Misc) -> None:
            pass


# =============================================================================
# VENTANA EMERGENTE DE RECIBO DE SUELDO
# =============================================================================
class VentanaReciboHaberes(tk.Toplevel):
    """ Ventana emergente (Modal) para vista previa e impresión del recibo. """

    def __init__(self, parent: tk.Widget, empleado: object, periodo: str, resultados: dict):
        super().__init__(parent)
        self.title(f"Recibo de Sueldo - Legajo {getattr(empleado, 'id_empleado', '')}")
        self.geometry("620x680")
        self.resizable(False, False)

        self.empleado = empleado
        self.periodo = periodo
        self.res = resultados

        # Configuración modal sin conflictos de tipos de ventana
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._construir_interfaz_recibo()

    def _construir_interfaz_recibo(self) -> None:
        """ Dibuja la vista previa del recibo en pantalla. """
        hoja = ttk.Frame(self, padding=20)
        hoja.pack(fill="both", expand=True)

        # 1. Cabecera Institucional
        lbl_empresa = ttk.Label(hoja, text="EMPRESA S.A.", font=("Segoe UI", 14, "bold"))
        lbl_empresa.pack(anchor="w")
        ttk.Label(hoja, text="CUIT: 30-12345678-9 | Domicilio Legal: Av. Principal 1234").pack(anchor="w")
        ttk.Separator(hoja, orient="horizontal").pack(fill="x", pady=10)

        # 2. Información del Empleado (Uso seguro de atributos con getattr)
        frame_info = ttk.LabelFrame(hoja, text=" Datos del Empleado y Período ", padding=10)
        frame_info.pack(fill="x", pady=5)

        legajo = getattr(self.empleado, 'id_empleado', 'N/A')
        apellidos = getattr(self.empleado, 'apellidos', '')
        nombres = getattr(self.empleado, 'nombres', '')
        cargo = getattr(self.empleado, 'cargo', 'N/A')

        ttk.Label(frame_info, text=f"Legajo: {legajo}").grid(row=0, column=0, sticky="w", padx=10)
        ttk.Label(frame_info, text=f"Empleado: {apellidos}, {nombres}").grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(frame_info, text=f"Cargo: {cargo}").grid(row=1, column=0, sticky="w", padx=10)
        ttk.Label(frame_info, text=f"Período: {self.periodo}").grid(row=1, column=1, sticky="w", padx=10)

        # 3. Tabla Visual de Conceptos
        frame_tabla = ttk.Frame(hoja)
        frame_tabla.pack(fill="both", expand=True, pady=10)

        columnas = ("concepto", "remunerativo", "no_remunerativo", "descuentos")
        tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

        tree.heading("concepto", text="Concepto")
        tree.heading("remunerativo", text="Remunerativo")
        tree.heading("no_remunerativo", text="No Remunerativo")
        tree.heading("descuentos", text="Deducciones")

        tree.column("concepto", width=230)
        tree.column("remunerativo", width=110, anchor="e")
        tree.column("no_remunerativo", width=110, anchor="e")
        tree.column("descuentos", width=110, anchor="e")

        rem = self.res.get("remunerativo", 0.0)
        no_rem = self.res.get("no_remunerativo", 0.0)
        desc = self.res.get("descuentos", 0.0)
        neto = self.res.get("neto", 0.0)

        if rem > 0:
            tree.insert("", "end", values=("Haberes Remunerativos Totales", f"$ {rem:,.2f}", "", ""))
        if no_rem > 0:
            tree.insert("", "end", values=("Conceptos No Remunerativos", "", f"$ {no_rem:,.2f}", ""))
        if desc > 0:
            tree.insert("", "end", values=("Total Deducciones y Retenciones", "", "", f"$ {desc:,.2f}"))

        tree.pack(fill="both", expand=True)

        # 4. Resumen de Totales
        frame_totales = ttk.Frame(hoja)
        frame_totales.pack(fill="x", pady=10)

        ttk.Label(frame_totales, text=f"Total Remunerativo: $ {rem:,.2f}").pack(anchor="e")
        ttk.Label(frame_totales, text=f"Total Deducciones: $ {desc:,.2f}").pack(anchor="e")
        ttk.Label(frame_totales, text=f"NETO A COBRAR: $ {neto:,.2f}", font=("Segoe UI", 11, "bold")).pack(anchor="e")

        # 5. Pie con Firmas y Botón de Imprimir Pantalla
        ttk.Separator(hoja, orient="horizontal").pack(fill="x", pady=10)

        lbl_firmas = ttk.Label(
            hoja,
            text="___________________________________          ___________________________________\n"
                 "        Firma del Empleador                                  Firma del Empleado"
        )
        lbl_firmas.pack(pady=10)

        btn_imprimir = ttk.Button(
            hoja, text="🖨️ Imprimir / Capturar Pantalla", command=self._imprimir_pantalla
        )
        btn_imprimir.pack(pady=5)

    @staticmethod
    def _imprimir_pantalla() -> None:
        """ Notifica al usuario las opciones sencillas de impresión de pantalla. """
        messagebox.showinfo(
            "Imprimir Recibo",
            "Para imprimir o guardar este recibo:\n\n"
            "1. Presione las teclas 'Alt + Impr Pant' (o 'Win + Shift + S') para capturar esta ventana.\n"
            "2. Péguela (Ctrl + V) en Word, WhatsApp o cualquier documento para imprimirlo directamente."
        )


# =============================================================================
# INTERFAZ DE USUARIO PRINCIPAL DE HABERES
# =============================================================================
class InterfazHaberes(ttk.Frame):
    """ Componente de Interfaz Gráfica para la Liquidación de Haberes. """

    def __init__(self, parent: tk.Widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.empleados_lista = []
        self.resultado_ultimo_calculo = None
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
            text="Liquidación de Haberes",
            style="Subtitulo.TLabel"
        )
        lbl_titulo.pack(anchor="w")

        lbl_subtitulo = ttk.Label(
            frame_top,
            text="Cálculo e integración de haberes con la base de datos",
            foreground=COLOR_TEXTO_MUTED
        )
        lbl_subtitulo.pack(anchor="w")

    def _crear_panel_seleccion(self) -> None:
        frame_sel = ttk.LabelFrame(self, text=" Selección de Empleado y Período ")
        frame_sel.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame_sel.columnconfigure(1, weight=1)

        ttk.Label(frame_sel, text="Empleado:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.cmb_empleados = ttk.Combobox(frame_sel, state="readonly")
        self.cmb_empleados.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.cmb_empleados.bind("<<ComboboxSelected>>", self._al_seleccionar_empleado)

        ttk.Label(frame_sel, text="Período:").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.txt_periodo = ttk.Entry(frame_sel)
        self.txt_periodo.insert(0, "2026-09")
        self.txt_periodo.grid(row=0, column=3, padx=10, pady=8, sticky="ew")

        ttk.Label(frame_sel, text="Régimen Aplicable:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.lbl_regimen = ttk.Label(frame_sel, text="Estándar (Relación de dependencia)", font=("Segoe UI", 9, "bold"))
        self.lbl_regimen.grid(row=1, column=1, padx=10, pady=8, sticky="w")

    def _crear_panel_conceptos(self) -> None:
        frame_main = ttk.Frame(self)
        frame_main.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_main.columnconfigure((0, 1), weight=1)
        frame_main.rowconfigure(0, weight=1)

        # Panel Izquierdo: Variables
        frame_izq = ttk.LabelFrame(frame_main, text=" Variables de Entrada ")
        frame_izq.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        frame_izq.columnconfigure(1, weight=1)

        ttk.Label(frame_izq, text="Salario Básico ($):").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.txt_basico = ttk.Entry(frame_izq)
        self.txt_basico.insert(0, "1200000.00")
        self.txt_basico.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Años de Antigüedad:").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.txt_antiguedad_anios = ttk.Entry(frame_izq)
        self.txt_antiguedad_anios.insert(0, "0")
        self.txt_antiguedad_anios.grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        self.var_presentismo = tk.BooleanVar(value=True)
        self.chk_presentismo = ttk.Checkbutton(
            frame_izq, text="Aplicar Presentismo (8,33%)", variable=self.var_presentismo
        )
        self.chk_presentismo.grid(row=2, column=0, columnspan=2, padx=10, pady=6, sticky="w")

        ttk.Label(frame_izq, text="Cant. Horas Extra (50%):").grid(row=3, column=0, padx=10, pady=6, sticky="w")
        self.txt_horas_extra = ttk.Entry(frame_izq)
        self.txt_horas_extra.insert(0, "0")
        self.txt_horas_extra.grid(row=3, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Feriados Trabajados (100%):").grid(row=4, column=0, padx=10, pady=6, sticky="w")
        self.txt_feriados = ttk.Entry(frame_izq)
        self.txt_feriados.insert(0, "0")
        self.txt_feriados.grid(row=4, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Monto Total Ventas ($):").grid(row=5, column=0, padx=10, pady=6, sticky="w")
        self.txt_ventas = ttk.Entry(frame_izq)
        self.txt_ventas.insert(0, "0.00")
        self.txt_ventas.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        ttk.Label(frame_izq, text="Adelanto de Haberes ($):").grid(row=6, column=0, padx=10, pady=6, sticky="w")
        self.txt_adelanto = ttk.Entry(frame_izq)
        self.txt_adelanto.insert(0, "0.00")
        self.txt_adelanto.grid(row=6, column=1, padx=10, pady=6, sticky="ew")

        # Panel Derecho: Deducciones y Acciones
        frame_der = ttk.LabelFrame(frame_main, text=" Deducciones y Resultados ")
        frame_der.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        frame_der.columnconfigure((0, 1), weight=1)

        self.var_jubilacion = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Aportes Jubilatorios (11%)", variable=self.var_jubilacion).grid(row=0, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_pami = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Ley 19032 / PAMI (3%)", variable=self.var_pami).grid(row=1, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_obra_social = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Obra Social (3%)", variable=self.var_obra_social).grid(row=2, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        self.var_sindicato = tk.BooleanVar(value=True)
        self.chk_sindicato = ttk.Checkbutton(
            frame_der, text="Cuota Sindical (2,5%)", variable=self.var_sindicato
        )
        self.chk_sindicato.grid(row=3, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        # Botones de Acción
        btn_calcular = ttk.Button(
            frame_der, text="1. Calcular y Guardar", command=self._procesar_calculo
        )
        btn_calcular.grid(row=4, column=0, padx=5, pady=15, sticky="ew")

        btn_ver_recibo = ttk.Button(
            frame_der, text="2. Ver Recibo", command=self._abrir_ventana_recibo
        )
        btn_ver_recibo.grid(row=4, column=1, padx=5, pady=15, sticky="ew")

        # Etiquetas de Resultados
        self.lbl_res_remunerativo = ttk.Label(frame_der, text="Total Remunerativo: $ 0.00")
        self.lbl_res_remunerativo.grid(row=5, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_no_remunerativo = ttk.Label(frame_der, text="Total No Remunerativo: $ 0.00")
        self.lbl_res_no_remunerativo.grid(row=6, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_descuentos = ttk.Label(frame_der, text="Total Deducciones: $ 0.00")
        self.lbl_res_descuentos.grid(row=7, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_neto = ttk.Label(frame_der, text="NETO A COBRAR: $ 0.00", font=("Segoe UI", 11, "bold"))
        self.lbl_res_neto.grid(row=8, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    def _cargar_empleados(self) -> None:
        try:
            self.empleados_lista = RepositorioRRHH.listar_empleados(incluir_inactivos=False)
            valores_combo = [f"{getattr(e, 'id_empleado', '')} - {getattr(e, 'apellidos', '')}, {getattr(e, 'nombres', '')} ({getattr(e, 'cargo', '')})" for e in self.empleados_lista]
            self.cmb_empleados['values'] = valores_combo
            if valores_combo:
                self.cmb_empleados.current(0)
                self._al_seleccionar_empleado(None)
        except (AttributeError, RuntimeError, ValueError) as err:
            messagebox.showerror("Error", f"Error al cargar lista de empleados: {err}")

    def _al_seleccionar_empleado(self, _event: object) -> None:
        seleccion_idx = self.cmb_empleados.current()
        if seleccion_idx < 0 or not self.empleados_lista:
            return

        emp = self.empleados_lista[seleccion_idx]
        cargo_lower = str(getattr(emp, 'cargo', '') or '').lower()
        vinculo_lower = str(getattr(emp, 'tipo_vinculo', '') or '').lower()

        if "administrador" in cargo_lower or "administrador" in vinculo_lower:
            self.lbl_regimen.config(text="Locación de Servicios - Categoría D")
            self.chk_sindicato.config(state="disabled")
            self.var_sindicato.set(False)
        elif "gerente" in cargo_lower:
            self.lbl_regimen.config(text="Monotributo - Categoría F")
            self.chk_sindicato.config(state="disabled")
            self.var_sindicato.set(False)
        elif "pasante" in vinculo_lower:
            self.lbl_regimen.config(text="Pasante (Sin cuota sindical)")
            self.chk_sindicato.config(state="disabled")
            self.var_sindicato.set(False)
        else:
            self.lbl_regimen.config(text="Relación de Dependencia Estándar")
            self.chk_sindicato.config(state="normal")
            self.var_sindicato.set(True)

        sueldo = getattr(emp, 'sueldo', 0)
        if sueldo and sueldo > 0:
            self.txt_basico.delete(0, "end")
            self.txt_basico.insert(0, f"{sueldo:.2f}")

    def _procesar_calculo(self) -> None:
        try:
            seleccion_idx = self.cmb_empleados.current()
            if seleccion_idx < 0:
                messagebox.showwarning("Atención", "Seleccione un empleado.")
                return

            emp = self.empleados_lista[seleccion_idx]

            datos_calculo = [
                getattr(emp, 'id_empleado', None),
                self.txt_periodo.get().strip(),
                float(self.txt_basico.get() or 0),
                int(self.txt_antiguedad_anios.get() or 0),
                self.var_presentismo.get(),
                float(self.txt_horas_extra.get() or 0),
                float(self.txt_feriados.get() or 0),
                float(self.txt_ventas.get() or 0),
                float(self.txt_adelanto.get() or 0),
                self.var_jubilacion.get(),
                self.var_pami.get(),
                self.var_obra_social.get(),
                self.var_sindicato.get()
            ]

            res = RepositorioHaberes.calcular_liquidacion(*datos_calculo)
            self.resultado_ultimo_calculo = res

            if isinstance(res, dict):
                self.lbl_res_remunerativo.config(text=f"Total Remunerativo: $ {res.get('remunerativo', 0):,.2f}")
                self.lbl_res_no_remunerativo.config(text=f"Total No Remunerativo: $ {res.get('no_remunerativo', 0):,.2f}")
                self.lbl_res_descuentos.config(text=f"Total Deducciones: $ {res.get('descuentos', 0):,.2f}")
                self.lbl_res_neto.config(text=f"NETO A COBRAR: $ {res.get('neto', 0):,.2f}")

            messagebox.showinfo("Éxito", "Liquidación calculada y registrada correctamente.")

        except ValueError:
            messagebox.showerror("Error", "Revise los campos numéricos ingresados.")
        except Exception as err:
            messagebox.showerror("Error en proceso", f"No se pudo guardar la liquidación: {err}")

    def _abrir_ventana_recibo(self) -> None:
        """ Abre el recibo emergente si existe una liquidación calculada. """
        seleccion_idx = self.cmb_empleados.current()
        if seleccion_idx < 0:
            messagebox.showwarning("Atención", "Seleccione un empleado.")
            return

        if not self.resultado_ultimo_calculo:
            messagebox.showwarning(
                "Cálculo Pendiente",
                "Primero presione '1. Calcular y Guardar' para generar los datos del recibo."
            )
            return

        emp = self.empleados_lista[seleccion_idx]
        periodo = self.txt_periodo.get().strip()

        VentanaReciboHaberes(
            parent=self,
            empleado=emp,
            periodo=periodo,
            resultados=self.resultado_ultimo_calculo
        )