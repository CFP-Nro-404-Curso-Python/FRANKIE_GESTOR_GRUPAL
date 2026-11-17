"""
===============================================================================
PUNTO DE ENTRADA PRINCIPAL: SISTEMA FRANKIE (main.py)
===============================================================================
Inicializa la base de datos, aplica los estilos accesibles y lanza
la ventana de autenticación (Login) para el control de acceso.
===============================================================================
"""

import sys
from pathlib import Path
import tkinter as tk

# Garantizar resolución de rutas: Agrega la carpeta 'src' al path de Python
DIR_ACTUAL = Path(__file__).resolve().parent
SRC_DIR = DIR_ACTUAL / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from infraestructura.conexion import ConexionDB
from vistas.estilos import aplicar_estilos_base
from vistas.ui_login import VentanaLogin


def main() -> None:
    """ Función de lanzamiento oficial del Sistema Frankie. """
    root = tk.Tk()

    # 1. Aplicar estilos corporativos accesibles globales
    aplicar_estilos_base(root)

    # 2. Verificar conexión a la base de datos al arrancar
    try:
        with ConexionDB():
            pass
        print("[INFO] Base de datos conectada y verificada correctamente.")
    except Exception as err:
        print(f"[ERROR CRÍTICO] No se pudo conectar a la base de datos: {err}")

    # 3. Lanzar la ventana de Autenticación (Login)
    VentanaLogin(root)

    root.mainloop()


if __name__ == "__main__":
    main()