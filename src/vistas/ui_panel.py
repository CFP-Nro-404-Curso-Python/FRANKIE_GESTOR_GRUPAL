import tkinter as tk
from tkinter import ttk, messagebox
# Importamos la vista de Alicia para integrarla. Más adelante, Uriel agregará la suya acá.
from vistas.ui_empleados import InterfazRRHH



class VentanaPrincipal:
    """
    Panel Principal (Orquestador Visual).
    Contiene el menú lateral y el área de trabajo central donde se cargarán los módulos.
    """
    def __init__(self, root, usuario_actual):
        self.root = root
        self.root.title(f"Frankie Gestor - Usuario: {usuario_actual.username}")
        # Hacemos que la ventana ocupe gran parte de la pantalla (resolución mínima recomendada).
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        self.usuario_actual = usuario_actual

        self._dibujar_interfaz()

    def _dibujar_interfaz(self):

        #  ESTRUCTURA BASE (Grid)
        # ------------------------
        # Dividimos la ventana en dos columnas: 
        # Columna 0 (Menú Lateral, no se expande) | Columna 1 (Área Central, se expande)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        #  MENÚ LATERAL (Izquierda)
        # --------------------------

        self.frame_menu = ttk.Frame(self.root, width=200, relief="raised", padding=10)
        self.frame_menu.grid(row=0, column=0, sticky="ns")
        # Forzamos a que el menú no se achique si agregamos botones.
        self.frame_menu.grid_propagate(False) 

        lbl_menu = ttk.Label(self.frame_menu, text="MENÚ PRINCIPAL", font=("Arial", 12, "bold"))
        lbl_menu.pack(pady=(10, 20))

        # Botón para cargar el módulo de Alicia. 
        # NOTA PARA URIEL: Cuando termines tu UI de facturación, vas a agregar un botón igual a este.
        btn_rrhh = ttk.Button(self.frame_menu, text="Recursos Humanos", command=self.abrir_modulo_rrhh)
        btn_rrhh.pack(fill="x", pady=5)

        # Separador visual.
        ttk.Separator(self.frame_menu, orient="horizontal").pack(fill="x", pady=20)

        # Botón de salida.
        btn_salir = ttk.Button(self.frame_menu, text="Cerrar Sesión", command=self.cerrar_sesion)
        btn_salir.pack(fill="x", pady=5, side="bottom")

        #  ÁREA CENTRAL (Derecha)
        # ------------------------
        # Acá adentro se van a dibujar las pantallas de cada módulo (RRHH, Ventas, etc.).
        self.frame_contenido = ttk.Frame(self.root, relief="sunken", padding=10)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")

        # Mensaje de bienvenida inicial en el área central.
        self.lbl_bienvenida = ttk.Label(
            self.frame_contenido, 
            text="Bienvenido al Sistema Frankie.\nSeleccioná una opción del menú lateral.",
            justify="center",
            font=("Arial", 14)
        )
        self.lbl_bienvenida.place(relx=0.5, rely=0.5, anchor="center")

    def limpiar_area_central(self):
        """Borra lo que sea que esté en el área central antes de abrir una pantalla nueva."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def abrir_modulo_rrhh(self):
        """Carga la interfaz de empleados en el área central."""
        self.limpiar_area_central()
        # Instanciamos la clase de Alicia y le decimos que su 'padre' es nuestro frame_contenido.
        vista_rrhh = InterfazRRHH(self.frame_contenido)
        # Hacemos que ocupe todo el espacio central.
        vista_rrhh.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        """Pregunta antes de salir."""
        if messagebox.askyesno("Salir", "¿Estás seguro que querés cerrar la sesión?"):
            self.root.destroy()
            # En la Semana 5 llamaremos al main.py para que vuelva a abrir el Login.