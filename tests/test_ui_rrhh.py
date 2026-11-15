"""
===============================================================================
MÓDULO DE PRUEBAS DE INTERFAZ GRÁFICA (UI): RRHH Y HABERES
test/test_ui_rrhh.py
===============================================================================
Ejecuta la interfaz de Tkinter sobre una base de datos SQLite en RAM (:memory:)
para evaluar:
1. Formulario y CRUD de Empleados (alta, edición, baja, listado).
2. Cálculo de liquidación y emisión/previsualización de Recibos de Sueldo.
3. Distribución estética de la pantalla (Layout, Treeview, Botones).
===============================================================================
"""

import sqlite3
import unittest
from unittest.mock import patch
import tkinter as tk
from tkinter import ttk, messagebox

from dominio.entidades_rrhh import Empleado
from infraestructura.repo_rrhh import RepositorioRRHH
from infraestructura.repo_haberes import RepositorioHaberes


class TestUIRRHHYHaberes(unittest.TestCase):
    """ Batería de pruebas de la interfaz de usuario para Nómina y Haberes. """

    def setUp(self) -> None:
        """ Prepara una base de datos temporal en memoria y la ventana de Tkinter. """
        # Base de datos en memoria para no tocar frankie_gestor.db
        self.conexion_test = sqlite3.connect(":memory:")
        self.conexion_test.row_factory = sqlite3.Row
        self._crear_tablas_en_memoria()

        # Instancia la ventana raíz de Tkinter
        self.root = tk.Tk()
        self.root.title("TEST UI - Gestión de Nómina y Liquidación de Haberes")
        self.root.geometry("1000x650")

    def tearDown(self) -> None:
        """ Cierra la ventana y la conexión al finalizar. """
        try:
            self.root.destroy()
        except Exception:
            pass
        self.conexion_test.close()

    def _crear_tablas_en_memoria(self) -> None:
        """ Recrea la estructura relacional necesaria en RAM. """
        cursor = self.conexion_test.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_persona TEXT NOT NULL DEFAULT 'Fisica',
                nombres TEXT,
                apellidos TEXT,
                razon_social TEXT,
                tipo_documento TEXT DEFAULT 'DNI',
                nro_documento TEXT,
                telefono TEXT,
                email TEXT,
                domicilio TEXT,
                ciudad TEXT,
                provincia TEXT,
                codigo_postal TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_persona INTEGER NOT NULL,
                id_usuario INTEGER,
                legajo TEXT UNIQUE,
                cargo TEXT,
                sector TEXT,
                tipo_vinculo TEXT DEFAULT 'Planta',
                sueldo REAL DEFAULT 0.0,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (id_persona) REFERENCES personas(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS liquidaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                periodo TEXT NOT NULL,
                total_remunerativo REAL NOT NULL,
                total_no_remunerativo REAL NOT NULL,
                total_descuentos REAL NOT NULL,
                neto_a_cobrar REAL NOT NULL,
                UNIQUE(id_empleado, periodo),
                FOREIGN KEY (id_empleado) REFERENCES empleados(id)
            );
        """)
        self.conexion_test.commit()

    @patch("infraestructura.repo_rrhh._obtener_conexion_segura")
    def test_simulacion_ui_completa(self, mock_conexion_rrhh) -> None:
        """
        Simula la interacción con la UI:
        1. Carga un empleado en la base temporal.
        2. Muestra la tabla (Treeview) con los datos cargados.
        3. Realiza la simulación del cálculo de recibo de sueldo y su vista previa.
        4. Despliega la ventana para inspección estética.
        """
        mock_conexion_rrhh.return_value = self.conexion_test

        # ---------------------------------------------------------------------
        # 1. PRECARGA DE DATOS DE PRUEBA (CRUD - Alta)
        # ---------------------------------------------------------------------
        emp_prueba = Empleado(
            nombres="Laura",
            apellidos="Fernández",
            nro_documento="35123456",
            telefono="1144556677",
            email="laura.fernandez@empresa.com",
            legajo="EMP-001",
            cargo="Empleado_Admin",
            sector="Administración",
            tipo_vinculo="Planta",
            sueldo=500000.0
        )
        RepositorioRRHH.crear_empleado(emp_prueba)

        # ---------------------------------------------------------------------
        # 2. CONSTRUCCIÓN DE LA INTERFAZ DE SIMULACIÓN (Simulación Estética)
        # ---------------------------------------------------------------------
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TAB 1: CRUD / Nómina de Empleados
        frame_nomina = ttk.Frame(notebook)
        notebook.add(frame_nomina, text="Nómina de Empleados (CRUD)")

        # Formulario de entrada
        frame_form = ttk.LabelFrame(frame_nomina, text=" Formulario de Empleado ", padding=10)
        frame_form.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_form, text="Legajo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        entry_legajo = ttk.Entry(frame_form)
        entry_legajo.insert(0, "EMP-002")
        entry_legajo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(frame_form, text="Nombre Completo:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        entry_nombre = ttk.Entry(frame_form)
        entry_nombre.insert(0, "Carlos Gómez")
        entry_nombre.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(frame_form, text="Sueldo Básico:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        entry_sueldo = ttk.Entry(frame_form)
        entry_sueldo.insert(0, "480000")
        entry_sueldo.grid(row=1, column=1, padx=5, pady=2)

        # Botones CRUD
        frame_btn = ttk.Frame(frame_form)
        frame_btn.grid(row=1, column=2, columnspan=2, pady=5)
        btn_guardar = ttk.Button(frame_btn, text="Guardar")
        btn_guardar.pack(side=tk.LEFT, padx=5)
        btn_eliminar = ttk.Button(frame_btn, text="Dar de Baja (Soft Delete)")
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        # Tabla Treeview para listar empleados
        tree_empleados = ttk.Treeview(
            frame_nomina,
            columns=("ID", "Legajo", "Nombre", "DNI", "Sector", "Sueldo"),
            show="headings"
        )
        tree_empleados.heading("ID", text="ID")
        tree_empleados.heading("Legajo", text="Legajo")
        tree_empleados.heading("Nombre", text="Nombre y Apellido")
        tree_empleados.heading("DNI", text="DNI")
        tree_empleados.heading("Sector", text="Sector")
        tree_empleados.heading("Sueldo", text="Sueldo Básico")

        tree_empleados.column("ID", width=40, anchor=tk.CENTER)
        tree_empleados.column("Legajo", width=80, anchor=tk.CENTER)
        tree_empleados.column("Nombre", width=200)
        tree_empleados.column("DNI", width=100)
        tree_empleados.column("Sector", width=120)
        tree_empleados.column("Sueldo", width=100, anchor=tk.E)

        tree_empleados.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Cargar datos en la tabla
        for emp in RepositorioRRHH.listar_empleados():
            tree_empleados.insert("", tk.END, values=(
                emp.id_empleado, emp.legajo, f"{emp.apellidos}, {emp.nombres}",
                emp.nro_documento, emp.sector, f"${emp.sueldo:,.2f}"
            ))

        # TAB 2: Liquidación de Haberes y Recibo
        frame_haberes = ttk.Frame(notebook)
        notebook.add(frame_haberes, text="Liquidación de Haberes y Recibo")

        # Cálculo de liquidación simulada
        liq = RepositorioHaberes.calcular_liquidacion(
            id_empleado=1,
            periodo="2026-03",
            basico=500000.0,
            antiguedad_anios=3,
            aplica_presentismo=True,
            conexion_alt=self.conexion_test
        )

        lbl_frame_recibo = ttk.LabelFrame(frame_haberes, text=" Vista Previa de Recibo de Sueldo ", padding=15)
        lbl_frame_recibo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        txt_recibo = tk.Text(lbl_frame_recibo, font=("Courier", 10), bg="#f8f9fa")
        txt_recibo.pack(fill=tk.BOTH, expand=True)

        plantilla_recibo = f"""
        ======================================================================
                                RECIBO DE SUELDO
        ======================================================================
        Periodo: 2026-03                     Legajo: EMP-001
        Empleado: Fernández, Laura           DNI: 35.123.456
        Sector: Administración               Cargo: Empleado_Admin
        ======================================================================
        CONCEPTO                             HABERES              DESCUENTOS
        ----------------------------------------------------------------------
        Sueldo Básico                        $500,000.00
        Antigüedad (3 años - 3%)              $ 15,000.00
        Presentismo (8.33%)                   $ 42,900.00
        Jubilación (11%)                                           $ 61,369.00
        PAMI Ley 19032 (3%)                                        $ 16,737.00
        Obra Social (3%)                                           $ 16,737.00
        Aporte Sindicato (2.5%)                                    $ 13,947.50
        ----------------------------------------------------------------------
        TOTAL REMUNERATIVO:                  ${liq['remunerativo']:,.2f}
        TOTAL DESCUENTOS:                                         ${liq['descuentos']:,.2f}
        ----------------------------------------------------------------------
        NETO A COBRAR:                       ${liq['neto']:,.2f}
        ======================================================================
        """
        txt_recibo.insert(tk.END, plantilla_recibo)
        txt_recibo.config(state=tk.DISABLED)

        # ---------------------------------------------------------------------
        # 3. VERIFICACIONES AUTOMÁTICAS Y MUESTRA VISUAL
        # ---------------------------------------------------------------------
        # Verificar que la tabla tenga filas
        filas_tree = tree_empleados.get_children()
        self.assertEqual(len(filas_tree), 1, "La tabla de la UI debe mostrar 1 empleado.")

        # Verificar los valores del cálculo de liquidación
        self.assertGreater(liq["neto"], 0, "El neto a cobrar debe ser mayor a 0.")

        # Descomentar 'self.root.mainloop()' para pausar el test y revisar la ventana en pantalla
        self.root.mainloop()


if __name__ == "__main__":
    unittest.main()