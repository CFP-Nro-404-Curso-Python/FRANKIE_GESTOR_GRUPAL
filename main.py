import sys
import os
import tkinter as tk



# ===================================
#  CONFIGURACIÓN DEL ENTORNO (PATHS)
# ===================================

# Le indicamos a Python que la carpeta 'src' es el núcleo de nuestros módulos.
# Esto evita el clásico error 'ModuleNotFoundError' al importar archivos entre carpetas.
ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if ruta_src not in sys.path:
    sys.path.insert(0, ruta_src)

# Ahora podemos importar de forma limpia desde nuestros paquetes.
from vistas.estilos import aplicar_estilos_base
from vistas.ui_login import VentanaLogin
from vistas.ui_panel import PanelPrincipal


class FrankieApp:
    """
    El Orquestador Principal (Entry Point).
    Su único trabajo es controlar el ciclo de vida del sistema:
    1. Levantar la ventana de Login.
    2. Esperar la validación.
    3. Si es exitosa, destruir el login y levantar el Panel Principal.
    """
    def __init__(self):
        # Acá guardaremos el objeto Usuario (Entidad) que se logueó con éxito.
        self.usuario_activo = None

    def arrancar_sistema(self):
        """ Punto de partida de la aplicación. """
        self.mostrar_login()

    def mostrar_login(self):
        """ Crea y levanta la ventana de autenticación inicial. """
        self.root_login = tk.Tk()
        aplicar_estilos_base(self.root_login)
        
        # Instanciamos el frame del login pasándole la ventana principal (root).
        self.vista_login = VentanaLogin(self.root_login)
        
        # =====================================================================
        #  NOTA PARA MI:
        # =====================================================================
        #  En ui_login.py armamos que 'self.parent.destroy()' se ejecute si la 
        #  clave es correcta. Al destruirse la ventana, este mainloop se frena 
        #  automáticamente y el código sigue hacia abajo.
        # =====================================================================
        self.root_login.mainloop()
        
        # == MODIFICACIÓN PARA ENCHUFAR EL PANEL ==
        # Si el login fue exitoso, la variable 'usuario_activo' en ui_login ya no estará vacía.
        # Uriel y Alicia deben saber que acá consultamos al REPOSITORIO sin que la VISTA se entere.
        if hasattr(self.vista_login, 'usuario_validado') and self.vista_login.usuario_validado:
            self.usuario_activo = self.vista_login.usuario_validado
            self.mostrar_panel_principal()

    def mostrar_panel_principal(self):
        """ Se ejecutará únicamente si la autenticación fue superada (Paso 2). """
        print(f"[ORQUESTADOR] Iniciando sesión para: {self.usuario_activo.username}")
        
        self.root_panel = tk.Tk()
        aplicar_estilos_base(self.root_panel)
        
        # Le inyectamos el usuario al panel para que sepa qué permisos tiene (Semana 4)
        self.vista_panel = PanelPrincipal(self.root_panel, self.usuario_activo)
        self.root_panel.mainloop()


# ================================================================================
#  ⚠️ ATENCIÓN AL EQUIPO (ALICIA Y URIEL):
# ================================================================================
#  1. EJECUCIÓN OFICIAL DEL SISTEMA:
#     A partir de esta semana, el programa completo se ejecuta SIEMPRE arrancando 
#     este archivo 'main.py' desde la raíz del proyecto.
#
#  2. INTEGRACIÓN DE SUS PANTALLAS:
#     Ustedes sigan desarrollando sus módulos (ui_clientes.py, ui_inventario.py) 
#     de forma aislada. No se preocupen por cómo conectarlas acá; yo (David) me 
#     voy a encargar de importar sus vistas e inyectarlas en el Panel Principal 
#     usando un menú de navegación.
# ================================================================================

if __name__ == "__main__":
    orquestador = FrankieApp()
    orquestador.arrancar_sistema()