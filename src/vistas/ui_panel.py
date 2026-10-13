import tkinter as tk
from tkinter import ttk, messagebox
# ===================================================================================
#  IMPORTANTE: Lazy Imports
# ===================================================================================
#  No importamos los archivos de Uriel y Alicia acá arriba. Si lo hiciéramos,
#  el sistema se colgaría cargando todas las pantallas juntas antes de arrancar.
#  Las importaremos recién cuando el usuario haga click en el botón correspondiente.
# ===================================================================================

class PanelPrincipal(ttk.Frame):
    """
    Contenedor principal del sistema (El Esqueleto).
    Acá se inyectarán todas las pantallas de los demás módulos.
    """
    def __init__(self, root, usuario_activo):
        super().__init__(root)
        self.root = root
        self.usuario_activo = usuario_activo

        # Configuración de la ventana principal.
        self.root.title(f"Frankie Gestor - Sesión de {self.usuario_activo.username}")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)

        # Expandimos este frame para que ocupe toda la ventana.
        self.pack(fill="both", expand=True)
        
        # En esta variable guardaremos la pantalla que se está mostrando actualmente.
        self.pantalla_actual = None

        self._dibujar_esqueleto()
        self._construir_menu()

    def _dibujar_esqueleto(self):
        """ Divide la pantalla en un menú lateral y un área de trabajo central. """

        # Columna 0: Menú Lateral (Fijo).
        self.frame_menu = ttk.Frame(self, width=200, relief="solid")
        self.frame_menu.pack(side="left", fill="y", padx=5, pady=5)

        # Evitamos que el frame lateral se encoja.
        self.frame_menu.pack_propagate(False) 

        # Columna 1: Área de Trabajo (Dinámica).
        self.frame_trabajo = ttk.Frame(self)
        self.frame_trabajo.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ttk.Label(self.frame_menu, text="MENÚ PRINCIPAL", font=("Segoe UI", 12, "bold")).pack(pady=20)

    def _construir_menu(self):
        """ 
        Dibuja los botones del menú. 
        Nota: En la Semana 4 agregaremos la lógica RBAC acá para ocultarlos según el rol.
        """

        # Botón para el módulo de RRHH (Alicia).
        self.btn_empleados = ttk.Button(
            self.frame_menu, 
            text="Personal (RRHH)", 
            command=self._cargar_pantalla_empleados
        )
        self.btn_empleados.pack(fill="x", padx=10, pady=5)

        # TODO: Agregar los botones de Clientes, Inventario y Facturación en la Semana 4.

        ttk.Button(
            self.frame_menu, 
            text="Cerrar Sesión", 
            command=self._cerrar_sesion
        ).pack(side="bottom", fill="x", padx=10, pady=20)



    # =============================================
    #  SISTEMA DE NAVEGACIÓN (INYECCIÓN DE VISTAS)
    # =============================================

    def _limpiar_area_trabajo(self):
        """ Destruye la pantalla que esté abierta para dejar el espacio libre. """
        if self.pantalla_actual is not None:
            self.pantalla_actual.destroy()

    def _cargar_pantalla_empleados(self):
        """ Técnica de Lazy Import: Cargamos la vista de Alicia solo al hacer click. """
        self._limpiar_area_trabajo()
        
        try:
            # Importamos sobre la marcha.
            from vistas.ui_empleados import InterfazRRHH
            # Instanciamos la pantalla de Alicia, diciéndole que su "padre" es nuestra área de trabajo.
            self.pantalla_actual = InterfazRRHH(self.frame_trabajo)
            # La empaquetamos para que ocupe todo el espacio central.
            self.pantalla_actual.pack(fill="both", expand=True)
        except ImportError:
            messagebox.showerror("Error", "El módulo de RRHH aún no está disponible.")

    def _cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar la sesión?"):
            self.root.destroy()
            # En main.py este cierre terminará la ejecución del programa.