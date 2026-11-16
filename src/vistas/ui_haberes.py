"""
===============================================================================
MÓDULO DE INTERFAZ DE USUARIO: LIQUIDACIÓN DE HABERES (src/vistas/ui_haberes.py)
===============================================================================
Calcula haberes remunerativos, deducciones de ley, persiste la liquidación
en SQLite y permite previsualizar y emitir el recibo oficial de sueldo.
===============================================================================
"""

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from infraestructura.repo_rrhh import RepositorioRRHH
from infraestructura.repo_haberes import RepositorioHaberes

try:
    from vistas.estilos import COLOR_TEXTO_MUTED
except ImportError:
    COLOR_TEXTO_MUTED = "#6c757d"


class InterfazHaberes(ttk.Frame):
    """
    Componente visual modular basado en ttk.Frame para la Liquidación de Haberes.
    """

    def __init__(self, parent: tk.Widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.empleados_lista = []
        self.ultima_liquidacion = None
        self.ultimo_empleado_liquidado = None
        self.ultimo_periodo_liquidado = ""

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._crear_encabezado()
        self._crear_panel_seleccion()
        self._crear_panel_conceptos()
        self._cargar_empleados()

    def _crear_encabezado(self) -> None:
        """Construye el título y subtítulo del panel."""
        frame_top = ttk.Frame(self)
        frame_top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

        ttk.Label(
            frame_top,
            text="Liquidación de Haberes",
            style="Subtitulo.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            frame_top,
            text="Cálculo remunerativo, deducciones de ley y emisión de recibos oficiales",
            foreground=COLOR_TEXTO_MUTED
        ).pack(anchor="w")

    def _crear_panel_seleccion(self) -> None:
        """Construye el selector de empleado y período."""
        frame_sel = ttk.LabelFrame(self, text=" Selección de Empleado y Período ")
        frame_sel.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame_sel.columnconfigure(1, weight=1)

        ttk.Label(frame_sel, text="Empleado:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.cmb_empleados = ttk.Combobox(frame_sel, state="readonly")
        self.cmb_empleados.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.cmb_empleados.bind("<<ComboboxSelected>>", self._al_seleccionar_empleado)

        ttk.Label(frame_sel, text="Período:").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.txt_periodo = ttk.Entry(frame_sel, width=15)
        self.txt_periodo.insert(0, datetime.now().strftime("%Y-%m"))
        self.txt_periodo.grid(row=0, column=3, padx=10, pady=8, sticky="ew")

        ttk.Label(frame_sel, text="Régimen Aplicable:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.lbl_regimen = ttk.Label(
            frame_sel,
            text="Estándar (Relación de dependencia)",
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_regimen.grid(row=1, column=1, padx=10, pady=8, sticky="w")

    def _crear_panel_conceptos(self) -> None:
        """Construye los paneles de variables de entrada, deducciones y resultados."""
        frame_main = ttk.Frame(self)
        frame_main.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")
        frame_main.columnconfigure((0, 1), weight=1)
        frame_main.rowconfigure(0, weight=1)

        # Panel Izquierdo: Variables de Entrada
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

        # Panel Derecho: Deducciones y Resultados
        frame_der = ttk.LabelFrame(frame_main, text=" Deducciones y Resultados ")
        frame_der.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        frame_der.columnconfigure(1, weight=1)

        self.var_jubilacion = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Aportes Jubilatorios (11%)", variable=self.var_jubilacion).grid(
            row=0, column=0, columnspan=2, padx=10, pady=4, sticky="w"
        )

        self.var_pami = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Ley 19032 / PAMI (3%)", variable=self.var_pami).grid(
            row=1, column=0, columnspan=2, padx=10, pady=4, sticky="w"
        )

        self.var_obra_social = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_der, text="Obra Social (3%)", variable=self.var_obra_social).grid(
            row=2, column=0, columnspan=2, padx=10, pady=4, sticky="w"
        )

        self.var_sindicato = tk.BooleanVar(value=True)
        self.chk_sindicato = ttk.Checkbutton(
            frame_der, text="Cuota Sindical (2,5%)", variable=self.var_sindicato
        )
        self.chk_sindicato.grid(row=3, column=0, columnspan=2, padx=10, pady=4, sticky="w")

        # Botones de Cálculo y Emisión de Recibo
        frame_btns_der = ttk.Frame(frame_der)
        frame_btns_der.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="ew")
        frame_btns_der.columnconfigure((0, 1), weight=1)

        self.btn_calcular = ttk.Button(
            frame_btns_der,
            text="Calcular y Guardar",
            command=self._procesar_calculo
        )
        self.btn_calcular.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_emitir_recibo = ttk.Button(
            frame_btns_der,
            text="📄 Emitir / Ver Recibo",
            command=self._abrir_vista_previa_recibo,
            state="disabled"
        )
        self.btn_emitir_recibo.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Etiquetas dinámicas de resultados
        self.lbl_res_remunerativo = ttk.Label(frame_der, text="Total Remunerativo: $ 0.00")
        self.lbl_res_remunerativo.grid(row=5, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_no_remunerativo = ttk.Label(frame_der, text="Total No Remunerativo: $ 0.00")
        self.lbl_res_no_remunerativo.grid(row=6, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_descuentos = ttk.Label(frame_der, text="Total Deducciones: $ 0.00")
        self.lbl_res_descuentos.grid(row=7, column=0, columnspan=2, padx=10, pady=3, sticky="w")

        self.lbl_res_neto = ttk.Label(frame_der, text="NETO A COBRAR: $ 0.00", font=("Segoe UI", 11, "bold"))
        self.lbl_res_neto.grid(row=8, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    def _cargar_empleados(self) -> None:
        """Consulta la BD mediante el Repositorio de RRHH y llena el Combobox."""
        try:
            self.empleados_lista = RepositorioRRHH.listar_empleados(incluir_inactivos=False)
            valores_combo = [
                f"{e.legajo} - {e.apellidos}, {e.nombres} ({e.cargo})"
                for e in self.empleados_lista
            ]
            self.cmb_empleados["values"] = valores_combo

            if valores_combo:
                self.cmb_empleados.current(0)
                self._al_seleccionar_empleado(None)

        except Exception as err:
            messagebox.showerror("Error", f"Error al cargar lista de empleados: {err}")

    def _al_seleccionar_empleado(self, _event: object) -> None:
        """Adapta el régimen laboral y carga el sueldo base del empleado seleccionado."""
        seleccion_idx = self.cmb_empleados.current()
        if seleccion_idx < 0 or not self.empleados_lista:
            return

        emp = self.empleados_lista[seleccion_idx]
        cargo_lower = (emp.cargo or "").lower()
        vinculo_lower = (getattr(emp, "tipo_vinculo", "") or "").lower()

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

        if emp.sueldo and emp.sueldo > 0:
            self.txt_basico.delete(0, "end")
            self.txt_basico.insert(0, f"{emp.sueldo:.2f}")

    def _procesar_calculo(self) -> None:
        """Calcula los haberes, persiste la liquidación y habilita la emisión del recibo."""
        try:
            seleccion_idx = self.cmb_empleados.current()
            if seleccion_idx < 0 or not self.empleados_lista:
                messagebox.showwarning("Atención", "Seleccione un empleado activo de la nómina.")
                return

            emp = self.empleados_lista[seleccion_idx]
            periodo = self.txt_periodo.get().strip()
            if not periodo:
                messagebox.showwarning("Atención", "Ingrese un período válido (ej. 2026-11).")
                return

            basico_val = float(self.txt_basico.get() or 0)
            adelanto_val = float(self.txt_adelanto.get() or 0)

            datos_calculo = [
                emp.id_empleado,
                periodo,
                basico_val,
                int(self.txt_antiguedad_anios.get() or 0),
                self.var_presentismo.get(),
                float(self.txt_horas_extra.get() or 0),
                float(self.txt_feriados.get() or 0),
                float(self.txt_ventas.get() or 0),
                adelanto_val,
                self.var_jubilacion.get(),
                self.var_pami.get(),
                self.var_obra_social.get(),
                self.var_sindicato.get()
            ]

            res = RepositorioHaberes.calcular_liquidacion(*datos_calculo)

            if isinstance(res, dict):
                remunerativo = res.get("remunerativo", 0.0)
                no_remunerativo = res.get("no_remunerativo", 0.0)
                descuentos = res.get("descuentos", 0.0)
                neto = res.get("neto", 0.0)

                self.lbl_res_remunerativo.config(text=f"Total Remunerativo: $ {remunerativo:,.2f}")
                self.lbl_res_no_remunerativo.config(text=f"Total No Remunerativo: $ {no_remunerativo:,.2f}")
                self.lbl_res_descuentos.config(text=f"Total Deducciones: $ {descuentos:,.2f}")
                self.lbl_res_neto.config(text=f"NETO A COBRAR: $ {neto:,.2f}")

                # Guardar estado para la emisión del recibo
                res_completo = dict(res)
                res_completo["basico"] = basico_val
                res_completo["adicionales"] = max(0.0, remunerativo - basico_val)
                if "desglose_deducciones" not in res_completo:
                    res_completo["desglose_deducciones"] = {
                        "jubilacion": remunerativo * 0.11 if self.var_jubilacion.get() else 0.0,
                        "pami": remunerativo * 0.03 if self.var_pami.get() else 0.0,
                        "obra_social": remunerativo * 0.03 if self.var_obra_social.get() else 0.0,
                        "sindicato": remunerativo * 0.025 if self.var_sindicato.get() else 0.0,
                        "adelanto": adelanto_val,
                    }

                self.ultima_liquidacion = res_completo
                self.ultimo_empleado_liquidado = emp
                self.ultimo_periodo_liquidado = periodo
                self.btn_emitir_recibo.config(state="normal")

            messagebox.showinfo("Éxito", "Liquidación calculada y registrada correctamente.")

        except ValueError:
            messagebox.showerror("Error", "Revise los campos numéricos ingresados (deben ser válidos).")
        except Exception as err:
            messagebox.showerror("Error en proceso", f"No se pudo procesar la liquidación: {err}")

    def _abrir_vista_previa_recibo(self) -> None:
        """Despliega una ventana modal con el recibo oficial y permite exportarlo a HTML/PDF."""
        if not self.ultima_liquidacion or not self.ultimo_empleado_liquidado:
            messagebox.showwarning("Atención", "Primero debe calcular y guardar una liquidación.")
            return

        emp = self.ultimo_empleado_liquidado
        liq = self.ultima_liquidacion
        periodo = self.ultimo_periodo_liquidado
        ded = liq.get("desglose_deducciones", {})
        fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

        nombre_completo = f"{emp.apellidos}, {emp.nombres}"
        otros_desc = ded.get("sindicato", 0.0) + ded.get("adelanto", 0.0)

        texto_recibo = (
            "========================================================================\n"
            "                 FRANKIE GESTOR S.R.L. - RECIBO DE HABERES              \n"
            "                      Ley 20.744 - Comprobante de Pago                  \n"
            "========================================================================\n"
            f" Fecha Emisión : {fecha_emision:<22} Período : {periodo}\n"
            f" Empleado      : {nombre_completo[:22]:<22} Legajo  : {emp.legajo}\n"
            f" CUIL / DNI    : {emp.nro_documento:<22} Cargo   : {emp.cargo}\n"
            "------------------------------------------------------------------------\n"
            " CONCEPTO                                  HABERES         DEDUCCIONES  \n"
            "------------------------------------------------------------------------\n"
            f" Sueldo Básico                           $ {liq.get('basico', 0.0):>10,.2f}\n"
            f" Adicionales Remunerativos               $ {liq.get('adicionales', 0.0):>10,.2f}\n"
            f" Haberes No Remunerativos                $ {liq.get('no_remunerativo', 0.0):>10,.2f}\n"
            f" Aporte Jubilatorio (11%)                                $ {ded.get('jubilacion', 0.0):>10,.2f}\n"
            f" Ley 19.032 - PAMI (3%)                                  $ {ded.get('pami', 0.0):>10,.2f}\n"
            f" Obra Social (3%)                                        $ {ded.get('obra_social', 0.0):>10,.2f}\n"
            f" Cuota Sindical / Adelantos                              $ {otros_desc:>10,.2f}\n"
            "------------------------------------------------------------------------\n"
            f" TOTALES                                 $ {liq.get('remunerativo', 0.0):>10,.2f}   $ {liq.get('descuentos', 0.0):>10,.2f}\n"
            "========================================================================\n"
            f" NETO A COBRAR:                          $ {liq.get('neto', 0.0):>10,.2f}\n"
            "========================================================================\n"
            "\n\n"
            "   ___________________________             ___________________________  \n"
            "       Firma del Empleador                     Firma del Empleado       \n"
        )

        modal = tk.Toplevel(self)
        modal.title(f"Recibo de Haberes - {emp.legajo} ({periodo})")
        modal.geometry("670x540")
        modal.resizable(False, False)
        modal.grab_set()

        frame_contenedor = ttk.Frame(modal, padding=15)
        frame_contenedor.pack(fill="both", expand=True)

        txt_vista = tk.Text(
            frame_contenedor,
            font=("Courier New", 10),
            bg="#FFFFFF",
            fg="#1E293B",
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=12,
            height=22
        )
        txt_vista.insert("1.0", texto_recibo)
        txt_vista.config(state="disabled")
        txt_vista.pack(fill="both", expand=True, pady=(0, 12))

        def exportar_e_imprimir() -> None:
            carpeta_recibos = Path(__file__).resolve().parent.parent.parent / "recibos"
            carpeta_recibos.mkdir(parents=True, exist_ok=True)
            legajo_limpio = str(emp.legajo).replace(" ", "_")
            periodo_limpio = periodo.replace("/", "-").replace(" ", "_")
            archivo_html = carpeta_recibos / f"Recibo_{legajo_limpio}_{periodo_limpio}.html"

            html_contenido = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Recibo {legajo_limpio} - {periodo}</title>
<style>
  body {{ font-family: 'Courier New', monospace; padding: 30px; background: #f8fafc; }}
  .recibo {{ background: #fff; border: 2px solid #0f172a; padding: 25px; max-width: 720px; margin: auto; white-space: pre; }}
  @media print {{ body {{ background: #fff; padding: 0; }} .no-print {{ display: none; }} }}
</style>
</head>
<body>
  <div class="recibo">{texto_recibo}</div>
  <p class="no-print" style="text-align:center; margin-top:15px;">
    <button onclick="window.print()" style="padding:10px 20px; font-size:15px; cursor:pointer;">🖨️ Imprimir / Guardar como PDF</button>
  </p>
</body>
</html>"""
            archivo_html.write_text(html_contenido, encoding="utf-8")
            webbrowser.open(archivo_html.as_uri())
            messagebox.showinfo("Recibo Exportado", f"Comprobante guardado en:\n{archivo_html}")

        frame_acciones = ttk.Frame(frame_contenedor)
        frame_acciones.pack(fill="x")

        ttk.Button(frame_acciones, text="🖨️ Exportar / Imprimir PDF", command=exportar_e_imprimir).pack(side="left")
        ttk.Button(frame_acciones, text="Cerrar", command=modal.destroy).pack(side="right")