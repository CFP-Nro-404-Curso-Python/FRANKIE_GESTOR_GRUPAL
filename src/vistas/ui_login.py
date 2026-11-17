"""
===============================================================================
MÓDULO DE VISTAS: VENTANA DE LOGIN (src/vistas/ui_login.py)
===============================================================================
Gestiona la interfaz de autenticación, verifica las credenciales mediante
el repositorio core y abre el Panel Principal corporativo al validar con éxito.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox

from infraestructura.repo_core import RepoCore
from vistas.ui_panel import PanelPrincipal
from vistas.estilos import COLOR_TEXTO_MUTED


class VentanaLogin:
    """
    Formulario de inicio de sesión del Sistema Frankie.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Frankie - Iniciar Sesión")
        self.root.geometry("420x340")
        self.root.resizable(False, False)

        self.var_usuario = tk.StringVar()
        self.var_password = tk.StringVar()

        self._crear_interfaz()

    def _crear_interfaz(self):
        # Contenedor principal con padding accesible
        frame = ttk.Frame(self.root, padding=25)
        frame.pack(fill="both", expand=True)

        # Título principal
        lbl_titulo = ttk.Label(
            frame,
            text="SISTEMA FRANKIE",
            style="Subtitulo.TLabel"
        )
        lbl_titulo.pack(pady=(10, 5))

        lbl_sub = ttk.Label(
            frame,
            text="Ingrese sus credenciales de acceso",
            foreground=COLOR_TEXTO_MUTED
        )
        lbl_sub.pack(pady=(0, 20))

        # Campo Usuario
        ttk.Label(frame, text="Usuario:").pack(anchor="w", pady=(0, 2))
        entry_user = ttk.Entry(frame, textvariable=self.var_usuario, width=32)
        entry_user.pack(pady=(0, 12), fill="x", ipady=3)
        entry_user.focus_set()

        # Campo Contraseña
        ttk.Label(frame, text="Contraseña:").pack(anchor="w", pady=(0, 2))
        entry_pass = ttk.Entry(frame, textvariable=self.var_password, show="*", width=32)
        entry_pass.pack(pady=(0, 20), fill="x", ipady=3)
        entry_pass.bind("<Return>", lambda _event: self.intentar_login())

        # Botón de Ingreso (Corregido a ipady=6)
        btn_login = ttk.Button(frame, text="Ingresar al Sistema", command=self.intentar_login)
        btn_login.pack(fill="x", ipady=6)

    def intentar_login(self):
        """Valida las credenciales ingresadas y efectúa el salto al panel principal."""
        username = self.var_usuario.get().strip()
        password = self.var_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Campos Incompletos", "Por favor, ingrese usuario y contraseña.")
            return

        # Validación segura mediante infraestructura Core
        try:
            usuario_valido = RepoCore.autenticar(username, password)
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo verificar la autenticación: {e}")
            return

        if usuario_valido:
            messagebox.showinfo("Éxito", f"¡Bienvenido/a, {usuario_valido.username}!")
            self.root.destroy()  # Cierra la ventana de login

            # Abre el Panel Principal corporativo pasando el objeto de usuario autenticado
            root_panel = tk.Tk()
            PanelPrincipal(root_panel, usuario_actual=usuario_valido)
            root_panel.mainloop()
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")