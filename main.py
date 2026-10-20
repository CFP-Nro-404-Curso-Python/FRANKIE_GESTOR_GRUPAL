import sys
from pathlib import Path
import tkinter as tk

# Agregamos la carpeta 'src' al path del sistema para que Python encuentre los módulos.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from vistas.ui_login import VentanaLogin
from vistas.ui_panel import VentanaPrincipal
from vistas.estilos import aplicar_estilos_base
from infraestructura.repo_core import RepoCore



class GestorFrankie:
    """
    Controlador central de la aplicación.
    Se encarga de manejar el ciclo de vida, abriendo primero el Login
    y, si hay éxito, cargando el Panel Principal.
    """
    def __init__(self):
        # 1. Iniciamos el motor gráfico y aplicamos estilos base.
        self.root = tk.Tk()
        aplicar_estilos_base(self.root)
        self.root.withdraw() # Ocultamos la ventana principal temporalmente.
        
        self.usuario_logueado = None
        self.iniciar_login()

    def iniciar_login(self):
        # 2. Creamos una ventana secundaria (Toplevel) para el Login.
        self.ventana_login = tk.Toplevel(self.root)
        self.app_login = VentanaLogin(self.ventana_login)
        
        # Guardamos el comportamiento original de destrucción de la ventana.
        metodo_original_destroy = self.ventana_login.destroy
        
        def validar_y_destruir():
            # Interceptamos el cierre: Si el login fue exitoso (llama a destroy),
            # recuperamos los datos tipeados antes de que la ventana desaparezca.
            repo = RepoCore()
            self.usuario_logueado = repo.autenticar_usuario(
                self.app_login.entry_usuario.get(), 
                self.app_login.entry_password.get()
            )
            
            # Ahora sí, destruimos el login.
            metodo_original_destroy() 
            
            # Si logramos capturar al usuario, arrancamos el panel. Si no, matamos la app.
            if self.usuario_logueado:
                self.iniciar_panel()
            else:
                self.root.destroy()

        # Sobreescribimos el método destroy para ejecutar nuestro puente.
        self.ventana_login.destroy = validar_y_destruir
        
        # Si aprietan la "X" roja para salir del login, apagamos todo.
        self.ventana_login.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def iniciar_panel(self):
        # 3. Login exitoso: Mostramos la ventana raíz y cargamos el Panel
        self.root.deiconify() 
        VentanaPrincipal(self.root, self.usuario_logueado)
        
        # Si aprietan la "X" roja en el panel principal, apagamos todo
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

if __name__ == "__main__":
    app = GestorFrankie()
    app.root.mainloop()