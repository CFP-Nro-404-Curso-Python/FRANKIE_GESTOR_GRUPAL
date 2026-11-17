"""
===============================================================================
MÓDULO DE PANEL PRINCIPAL (src/vistas/ui_panel.py)
===============================================================================
Orquestador visual principal con menú lateral, control RBAC y área de trabajo.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controladores.orquestador_core import OrquestadorCore

# Importaciones seguras de las vistas modulares del sistema
try:
    from vistas.ui_empleados import InterfazEmpleados
except ImportError:
    try:
        from src.vistas.ui_empleados import InterfazEmpleados
    except ImportError:
        InterfazEmpleados = None

try:
    from vistas.ui_proveedores import InterfazProveedores
except ImportError:
    try:
        from src.vistas.ui_proveedores import InterfazProveedores
    except ImportError:
        InterfazProveedores = None

try:
    from vistas.ui_inventario import InterfazInventario
except ImportError:
    try:
        from src.vistas.ui_inventario import InterfazInventario
    except ImportError:
        InterfazInventario = None

try:
    from vistas.ui_haberes import InterfazHaberes
except ImportError:
    try:
        from src.vistas.ui_haberes import InterfazHaberes
    except ImportError:
        InterfazHaberes = None


class PanelPrincipal:
    """
    Ventana contenedora principal del sistema bajo arquitectura de menú lateral.
    """

    def __init__(self, root: tk.Tk, usuario_actual):
        self.root = root
        self.usuario_actual = usuario_actual

        roles_txt = ", ".join(r.nombre for r in self.usuario_actual.roles) if self.usuario_actual.roles else "Sin Roles"
        self.root.title(f"Frankie Gestor Comercial - Usuario: {usuario_actual.username} [{roles_txt}]")
        self.root.geometry("1150x750")
        self.root.minsize(950, 650)

        self.pantalla_actual = None
        self._dibujar_interfaz()

    def _dibujar_interfaz(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # =======================================================
        # MENÚ LATERAL (Izquierda)
        # =======================================================
        self.frame_menu = ttk.Frame(self.root, width=240, relief="raised", padding=10)
        self.frame_menu.grid(row=0, column=0, sticky="ns")
        self.frame_menu.grid_propagate(False)

        lbl_menu = ttk.Label(self.frame_menu, text="MENÚ PRINCIPAL", font=("Arial", 12, "bold"))
        lbl_menu.pack(pady=(15, 10))

        nombres_roles = [r.nombre for r in self.usuario_actual.roles]
        es_admin = "Administrador" in nombres_roles

        # Botones de Navegación Modular
        btn_rrhh = ttk.Button(self.frame_menu, text="👥 Padrón Empleados", command=self.abrir_modulo_rrhh)
        btn_rrhh.pack(fill="x", pady=4)

        btn_haberes = ttk.Button(self.frame_menu, text="💰 Liquidación Haberes", command=self.abrir_modulo_haberes)
        btn_haberes.pack(fill="x", pady=4)

        btn_proveedores = ttk.Button(self.frame_menu, text="🏭 Padrón Proveedores",
                                     command=self.abrir_modulo_proveedores)
        btn_proveedores.pack(fill="x", pady=4)

        btn_inventario = ttk.Button(self.frame_menu, text="📦 Control de Stock", command=self.abrir_modulo_inventario)
        btn_inventario.pack(fill="x", pady=4)

        ttk.Separator(self.frame_menu, orient="horizontal").pack(fill="x", pady=15)

        # Zona exclusiva de administración
        if es_admin:
            btn_backup = ttk.Button(self.frame_menu, text="💾 Backup Sistema", command=self.ejecutar_backup)
            btn_backup.pack(fill="x", pady=4)

        ttk.Separator(self.frame_menu, orient="horizontal").pack(fill="x", pady=15)

        btn_salir = ttk.Button(self.frame_menu, text="🚪 Cerrar Sesión", command=self.cerrar_sesion)
        btn_salir.pack(side="bottom", fill="x", pady=10)

        # =======================================================
        # ÁREA DE TRABAJO CENTRAL (Derecha)
        # =======================================================
        self.frame_contenido = ttk.Frame(self.root, relief="sunken", padding=15)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_bienvenida = ttk.Label(
            self.frame_contenido,
            text=f"Bienvenido/a al Sistema Frankie, {self.usuario_actual.username}.\nSeleccione una opción del menú lateral para comenzar.",
            justify="center",
            font=("Arial", 13)
        )
        self.lbl_bienvenida.place(relx=0.5, rely=0.5, anchor="center")

    def limpiar_area_central(self):
        """Elimina la vista activa anterior."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def gestionar_apertura(self, ClaseVista, mensaje_fallback: str):
        self.limpiar_area_central()
        if ClaseVista is not None:
            try:
                self.pantalla_actual = ClaseVista(self.frame_contenido)
                if hasattr(self.pantalla_actual, "pack"):
                    self.pantalla_actual.pack(fill="both", expand=True)
            except Exception as e:
                self.mostrar_mensaje_error(f"Error al cargar la vista: {e}")
        else:
            self.mostrar_mensaje_error(mensaje_fallback)

    def mostrar_mensaje_error(self, texto: str):
        lbl = ttk.Label(self.frame_contenido, text=texto, font=("Arial", 11), foreground="red")
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.pantalla_actual = lbl

    def abrir_modulo_rrhh(self):
        self.gestionar_apertura(InterfazEmpleados, "Módulo de Empleados no disponible.")

    def abrir_modulo_haberes(self):
        self.gestionar_apertura(InterfazHaberes, "Módulo de Liquidación de Haberes no disponible.")

    def abrir_modulo_proveedores(self):
        self.gestionar_apertura(InterfazProveedores, "Módulo de Proveedores no disponible.")

    def abrir_modulo_inventario(self):
        self.gestionar_apertura(InterfazInventario, "Módulo de Inventario no disponible.")

    def ejecutar_backup(self):
        orquestador = OrquestadorCore()
        resultado = orquestador.ejecutar_backup()
        if "exitoso" in resultado.lower():
            messagebox.showinfo("Backup Completado", resultado)
        else:
            messagebox.showerror("Error de Backup", resultado)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea salir del sistema?"):
            self.root.destroy()