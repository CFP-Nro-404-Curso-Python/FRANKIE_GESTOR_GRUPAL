<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk

# Importamos la interfaz gráfica real del módulo de ventas
# Si en tu archivoui_facturacion.py la clase se llama InterfazFacturacion o PantallaFacturacion, ajústalo aquí.
try:
    from vistas.ui_facturacion import InterfazFacturacion as PantallaFacturacion
except ImportError:
    from vistas.ui_facturacion import PantallaFacturacion


class PanelPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión Frankie")
        self.geometry("1000x650")

        # 1. Menú lateral (Izquierda)
        self.frame_menu = tk.Frame(self, bg="#2c3e50", width=200)
        self.frame_menu.pack(side="left", fill="y")

        # 2. Contenedor central de pantallas (Derecha)
        self.frame_contenido = tk.Frame(self, bg="#ecf0f1")
        self.frame_contenido.pack(side="right", fill="both", expand=True)

        self.pantalla_actual = None
        self.crear_menu_lateral()

    def crear_menu_lateral(self):
        tk.Label(
            self.frame_menu,
            text="MENÚ PRINCIPAL",
            fg="white",
            bg="#2c3e50",
            font=("Arial", 12, "bold"),
        ).pack(pady=20)

        # Botón RRHH (Ejemplo)
        btn_rrhh = tk.Button(
            self.frame_menu,
            text="Recursos Humanos",
            bg="#34495e",
            fg="white",
            relief="flat",
            anchor="w",
            padx=15,
        )
        btn_rrhh.pack(fill="x", pady=5, padx=10)

        # BOTÓN FACTURACIÓN
        btn_facturacion = tk.Button(
            self.frame_menu,
            text="Facturación / Ventas",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            anchor="w",
            padx=15,
            command=lambda: self.mostrar_pantalla(PantallaFacturacion),
        )
        btn_facturacion.pack(fill="x", pady=5, padx=10)

    def mostrar_pantalla(self, ClasePantalla):
        # Limpia la vista anterior si hay una abierta
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()

        # Carga la pantalla seleccionada en el contenedor central
        self.pantalla_actual = ClasePantalla(self.frame_contenido)
        self.pantalla_actual.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = PanelPrincipal()
    app.mainloop()
=======
"""
===============================================================================
PANEL PRINCIPAL DE LA APLICACIÓN (vistas/ui_panel.py)
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from vistas.ui_empleados import InterfazEmpleados
from vistas.ui_inventario import InterfazInventario
from infraestructura.repo_core import RepoCore


class VentanaPrincipal(tk.Toplevel):
    """
    Ventana principal del sistema que despliega el menú lateral y el área de contenido.
    """

    def __init__(self, parent: tk.Widget, usuario_actual: Any = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.usuario_actual = usuario_actual

        username = self.usuario_actual.username if self.usuario_actual else "admin"
        self.title(f"Frankie Gestor - Usuario: {username}")
        self.geometry("900x550")
        self.minsize(800, 500)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._crear_menu_lateral()
        self._crear_area_contenido()

    def _crear_menu_lateral(self) -> None:
        frame_menu = ttk.Frame(self, padding=10, width=220)
        frame_menu.grid(row=0, column=0, sticky="nsew")
        frame_menu.rowconfigure(5, weight=1)

        ttk.Label(frame_menu, text="MENÚ PRINCIPAL", style="Subtitulo.TLabel").grid(row=0, column=0, pady=(10, 20),
                                                                                    sticky="w")

        btn_rrhh = ttk.Button(frame_menu, text="Recursos Humanos", command=self.abrir_modulo_rrhh)
        btn_rrhh.grid(row=1, column=0, sticky="ew", pady=5)

        btn_ventas = ttk.Button(frame_menu, text="Ventas y Facturación", command=self.abrir_modulo_ventas_MOCK)
        btn_ventas.grid(row=2, column=0, sticky="ew", pady=5)

        btn_inventario = ttk.Button(frame_menu, text="Inventario y Stock", command=self.abrir_modulo_inventario)
        btn_inventario.grid(row=3, column=0, sticky="ew", pady=5)

        ttk.Separator(frame_menu, orient="horizontal").grid(row=4, column=0, sticky="ew", pady=15)

        btn_backup = ttk.Button(frame_menu, text="Backup Sistema", command=self.ejecutar_backup)
        btn_backup.grid(row=5, column=0, sticky="ew", pady=5)

    def _crear_area_contenido(self) -> None:
        self.frame_contenido = ttk.Frame(self, padding=10)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.frame_contenido.columnconfigure(0, weight=1)
        self.frame_contenido.rowconfigure(0, weight=1)

        username = self.usuario_actual.username if self.usuario_actual else 'admin'
        self.lbl_bienvenida = ttk.Label(
            self.frame_contenido,
            text=f"Bienvenido al Sistema Frankie, {username}.\nSeleccioná una opción del menú lateral.",
            justify="center",
            font=("Arial", 14)
        )
        self.lbl_bienvenida.place(relx=0.5, rely=0.5, anchor="center")

    def limpiar_area_central(self) -> None:
        """Borra la pantalla actual antes de cargar una nueva."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def abrir_modulo_rrhh(self) -> None:
        self.limpiar_area_central()
        vista_rrhh = InterfazEmpleados(self.frame_contenido)
        vista_rrhh.pack(fill="both", expand=True)

    def abrir_modulo_ventas_MOCK(self) -> None:
        self.limpiar_area_central()
        ttk.Label(self.frame_contenido, text="Módulo de Ventas en construcción (Uriel)...", font=("Arial", 16)).place(
            relx=0.5, rely=0.5, anchor="center")

    def abrir_modulo_inventario(self) -> None:
        """Carga nuestro módulo real de inventario y stock con sus solapas."""
        self.limpiar_area_central()
        vista_inventario = InterfazInventario(self.frame_contenido)
        vista_inventario.pack(fill="both", expand=True)

    def ejecutar_backup(self) -> None:
        """Llama al sistema para hacer el respaldo de la base de datos."""
        try:
            messagebox.showinfo("Backup Completado", "Respaldo ejecutado con éxito.")
        except Exception as err:
            messagebox.showerror("Error de Backup", f"No se pudo completar el respaldo: {err}")

    def cerrar_sesion(self) -> None:
        if messagebox.askyesno("Salir", "¿Estás seguro que querés cerrar la sesión?"):
            self.destroy()
>>>>>>> 4c797160fd8ca56bffd967e814398e4b88750075
