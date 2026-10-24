"""
===============================================================================
MÓDULO DE PRUEBAS UNITARIAS Y DE INTEGRACIÓN: RRHH Y HABERES (test_rrhh.py)
===============================================================================
Batería de pruebas automatizadas para validar:
1. Creación, listado y filtrado de Empleados (repo_rrhh.py).
2. Cálculo exacto de conceptos remunerativos y descuentos de ley (repo_haberes.py).
3. Comportamiento transaccional en base de datos temporal (:memory:).
===============================================================================
"""

import sqlite3
import unittest
from unittest.mock import patch

from dominio.entidades_rrhh import Empleado
from infraestructura.repo_rrhh import RepositorioRRHH
from infraestructura.repo_haberes import RepositorioHaberes


class TestRRHHYHaberes(unittest.TestCase):
    """
    Suite de pruebas para validar las reglas de negocio de Recursos Humanos
    y la liquidación de sueldos.
    """

    def setUp(self) -> None:
        """
        Prepara una conexión SQLite en memoria aislada antes de cada test.
        """
        self.conexion_test = sqlite3.connect(":memory:")
        self.conexion_test.row_factory = sqlite3.Row
        self._crear_tablas_en_memoria()

    def tearDown(self) -> None:
        """
        Cierra la conexión al finalizar cada test para garantizar aislamiento.
        """
        self.conexion_test.close()

    def _crear_tablas_en_memoria(self) -> None:
        """ Recrea el esquema relacional de personas, empleados y liquidaciones. """
        cursor = self.conexion_test.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_persona TEXT NOT NULL,
                nombres TEXT,
                apellidos TEXT,
                razon_social TEXT,
                tipo_documento TEXT,
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

    # -------------------------------------------------------------------------
    # 1. PRUEBAS DE GESTIÓN DE EMPLEADOS
    # -------------------------------------------------------------------------
    @patch("infraestructura.repo_rrhh._obtener_conexion_segura")
    def test_crear_y_listar_empleado(self, mock_conexion) -> None:
        """ Verifica el alta multitabla y la recuperación de empleados. """
        mock_conexion.return_value = self.conexion_test

        emp = Empleado(
            nombres="María",
            apellidos="González",
            nro_documento="32111222",
            telefono="1199887766",
            email="maria.gonzalez@empresa.com",
            legajo="EMP-001",
            cargo="Empleado_Admin",
            sector="Administración",
            tipo_vinculo="Planta",
            sueldo=450000.0
        )

        resultado = RepositorioRRHH.crear_empleado(emp)
        self.assertTrue(resultado, "El empleado debió crearse exitosamente.")

        empleados = RepositorioRRHH.listar_empleados()
        self.assertEqual(len(empleados), 1, "Debe haber 1 empleado registrado.")
        self.assertEqual(empleados[0].nombres, "María")
        self.assertEqual(empleados[0].apellidos, "González")
        self.assertEqual(empleados[0].sueldo, 450000.0)

    @patch("infraestructura.repo_rrhh._obtener_conexion_segura")
    def test_baja_logica_empleado(self, mock_conexion) -> None:
        """ Valida que el Soft Delete oculte al empleado del listado por defecto. """
        mock_conexion.return_value = self.conexion_test

        emp = Empleado(
            nombres="Juan", apellidos="Pérez", nro_documento="28333444",
            cargo="Vendedor", sector="Ventas", sueldo=300000.0
        )
        RepositorioRRHH.crear_empleado(emp)

        # Desactivar empleado (id_empleado = 1)
        RepositorioRRHH.cambiar_estado_empleado(id_empleado=1, nuevo_estado=0)

        # Listado estándar no debe incluir inactivos
        activos = RepositorioRRHH.listar_empleados(incluir_inactivos=False)
        self.assertEqual(len(activos), 0, "No debe retornar empleados inactivos por defecto.")

        # Listado con inactivos debe incluirlo
        todos = RepositorioRRHH.listar_empleados(incluir_inactivos=True)
        self.assertEqual(len(todos), 1, "Debe retornar el empleado inactivo al solicitarlo.")

    # -------------------------------------------------------------------------
    # 2. PRUEBAS DE LIQUIDACIÓN DE HABERES
    # -------------------------------------------------------------------------
    def test_calculo_liquidacion_basica_con_descuentos(self) -> None:
        """
        Simulacro de Liquidación:
        - Básico: $100.000
        - Antigüedad: 5 años (5% = $5.000) -> Subtotal Base = $105.000
        - Presentismo: Sí (8.33% de $105.000 = $8.746,50)
        - Total Remunerativo = $113.746,50
        - Deducciones Ley (11% + 3% + 3% + 2.5% = 19.5% de Remunerativo)
          Deducciones = $113.746,50 * 0.195 = $22.180,57
        - Neto = $113.746,50 - $22.180,57 = $91.565,93
        """
        res = RepositorioHaberes.calcular_liquidacion(
            id_empleado=1,
            periodo="2026-03",
            basico=100000.0,
            antiguedad_anios=5,
            aplica_presentismo=True,
            aplica_jubilacion=True,
            aplica_pami=True,
            aplica_obra_social=True,
            aplica_sindicato=True,
            conexion_alt=self.conexion_test
        )

        self.assertEqual(res["remunerativo"], 113746.50)
        self.assertEqual(res["descuentos"], 22180.57)
        self.assertEqual(res["neto"], 91565.93)

        # Verificar persistencia directa en la base de datos de test
        cursor = self.conexion_test.cursor()
        cursor.execute("SELECT neto_a_cobrar FROM liquidaciones WHERE id_empleado = 1 AND periodo = '2026-03'")
        fila = cursor.fetchone()
        self.assertIsNotNone(fila, "Debe haber grabado la liquidación en la base de datos.")
        self.assertEqual(fila["neto_a_cobrar"], 91565.93)

    def test_calculo_horas_extra_y_adelanto(self) -> None:
        """ Valida el recargo del 150% en horas extras y la deducción de adelantos. """
        # Básico: $200.000 -> Valor Hora: 200.000 / 200 = $1.000
        # 10 Horas Extra al 150%: 10 * 1000 * 1.5 = $15.000
        # Remunerativo = $215.000
        # Deducciones Ley (19.5% de 215.000 = $41.925) + Adelanto ($10.000) = $51.925
        # Neto = 215.000 - 51.925 = $163.075

        res = RepositorioHaberes.calcular_liquidacion(
            id_empleado=2,
            periodo="2026-03",
            basico=200000.0,
            horas_extra=10.0,
            adelanto=10000.0,
            conexion_alt=self.conexion_test
        )

        self.assertEqual(res["remunerativo"], 215000.0)
        self.assertEqual(res["descuentos"], 51925.0)
        self.assertEqual(res["neto"], 163075.0)


if __name__ == "__main__":
    unittest.main()