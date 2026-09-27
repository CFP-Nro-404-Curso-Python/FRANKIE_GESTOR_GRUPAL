import tkinter as tk
from tkinter import messagebox
from infraestructura.repo_core import RepoCore



class VentanaLogin:
    """
    Capa Visual (Vista) para el ingreso al sistema.
    Solamente dibuja la pantalla y captura los clicks del usuario.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Frankie Gestor - Acceso")
        self.root.geometry("300x250")
        self.root.resizable(False, False)

        # Contador de seguridad (regla de negocio simple que podemos manejar acá).
        self.intentos_fallidos = 0

        self._dibujar_interfaz()

    def _dibujar_interfaz(self):
        # Etiquetas y Cajas de texto
        tk.Label(self.root, text="Usuario:").pack(pady=(20, 5))
        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack()

        tk.Label(self.root, text="Contraseña:").pack(pady=(10, 5))
        # show="*" oculta los caracteres tipeados por seguridad.
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack()

        # Botón de ingreso (El 'command' vincula el click con nuestra función).
        self.btn_ingresar = tk.Button(self.root, text="Ingresar", command=self.procesar_login)
        self.btn_ingresar.pack(pady=20)

    def procesar_login(self):
        # 1. Capturamos lo que el usuario escribió.
        usuario_tipeado = self.entry_usuario.get()
        password_tipeada = self.entry_password.get()

        if not usuario_tipeado or not password_tipeada:
            messagebox.showwarning("Atención", "Completá todos los campos.")
            return

        # 2. Consultamos a la capa de Infraestructura.
        repo = RepoCore()
        usuario_validado = repo.autenticar_usuario(usuario_tipeado, password_tipeada)

        # 3. Lógica de validación visual.
        if usuario_validado:
            messagebox.showinfo("Éxito", f"Bienvenido, {usuario_validado.username}")
            # Acá en la Semana 5 llamaremos al orquestador para abrir el 'ui_panel.py'.
            self.root.destroy() 
        else:
            self.intentos_fallidos += 1
            intentos_restantes = 3 - self.intentos_fallidos
            
            if self.intentos_fallidos >= 3:
                self.btn_ingresar.config(state=tk.DISABLED) # Bloqueamos el botón.
                messagebox.showerror("Bloqueo", "Sistema bloqueado por seguridad. Hablá con el Administrador.")
            else:
                messagebox.showerror("Error", f"Credenciales incorrectas. Te quedan {intentos_restantes} intentos.")



# ==============================================================================================
#  ⚠️ ATENCIÓN ALICIA Y URIEL (CÓMO DEBEN ARMAR SUS VISTAS):
# ==============================================================================================
#
#  Cuando programen ui_empleados.py, ui_facturacion.py, etc., respeten esto:
#
#  1. SEPARACIÓN DE RESPONSABILIDADES:
#     - Este archivo SOLO dibuja ventanas y captura eventos (clicks, tipeo).
#     - Está PROHIBIDO importar SQLite acá. La vista no sabe que existe una base de datos.
#     - Toda consulta a la base de datos se hace llamando al Repositorio (o Controlador).
#
#  2. ESTRUCTURA ORIENTADA A OBJETOS:
#     - Metan sus pantallas adentro de una Clase (ej. class VentanaClientes).
#     - Separen el dibujo de la interfaz (Labels, Buttons, Treeviews) de las 
#       funciones lógicas (procesar_guardado, calcular_total), para que el código quede limpio.
# ==============================================================================================

# Código para probar la ventana suelta durante el desarrollo:
if __name__ == "__main__":
    app = tk.Tk()
    ventana = VentanaLogin(app)
    app.mainloop()