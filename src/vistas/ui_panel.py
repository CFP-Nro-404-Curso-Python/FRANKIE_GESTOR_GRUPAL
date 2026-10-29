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
