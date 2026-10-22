import tkinter as tk
from tkinter import ttk, messagebox
# Importamos la vista de Alicia para integrarla.
from vistas.ui_empleados import InterfazRRHH
# Importamos nuestro orquestador para el backup.
from controladores.orquestador_core import OrquestadorCore



class VentanaPrincipal:
    """
    Panel Principal (Orquestador Visual).
    Contiene el menú lateral (con filtro RBAC) y el área de trabajo central.
    """
    def __init__(self, root, usuario_actual):
        self.root = root
        self.root.title(f"Frankie Gestor - Usuario: {usuario_actual.username}")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        self.usuario_actual = usuario_actual

        self._dibujar_interfaz()

    def _dibujar_interfaz(self):



        # ========================
        #  ESTRUCTURA BASE (Grid)
        # ========================

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)



        # =======================================================
        #  MENÚ LATERAL (Izquierda) CON RBAC (Control de Acceso)
        # =======================================================

        self.frame_menu = ttk.Frame(self.root, width=220, relief="raised", padding=10)
        self.frame_menu.grid(row=0, column=0, sticky="ns")
        self.frame_menu.grid_propagate(False) 

        lbl_menu = ttk.Label(self.frame_menu, text="MENÚ PRINCIPAL", font=("Arial", 12, "bold"))
        lbl_menu.pack(pady=(10, 20))

        # Analizamos los roles que trajo el usuario desde la base de datos.
        nombres_roles = [rol.nombre for rol in self.usuario_actual.roles]
        es_admin = "Administrador" in nombres_roles
        es_gerente = "Gerente" in nombres_roles
        es_ventas = "Empleado - Ventas" in nombres_roles
        es_compras = "Empleado - Compras" in nombres_roles



        # ========================================
        #  BOTONES DE MÓDULOS (Filtrados por Rol)
        # ========================================
        
        if es_admin or es_gerente:
            btn_rrhh = ttk.Button(self.frame_menu, text="Recursos Humanos", command=self.abrir_modulo_rrhh)
            btn_rrhh.pack(fill="x", pady=5)

        if es_admin or es_gerente or es_ventas:

            # ⚠️ URIEL: Cuando termines 'ui_facturacion.py', cambiá 'abrir_modulo_ventas_MOCK' por el nombre 
            # de la función real que vas a crear más abajo.
            btn_ventas = ttk.Button(self.frame_menu, text="Ventas y Facturación", command=self.abrir_modulo_ventas_MOCK)
            btn_ventas.pack(fill="x", pady=5)

        if es_admin or es_gerente or es_compras:

            # ⚠️ ALICIA: Cuando termines 'ui_inventario.py', cambiá 'abrir_modulo_inventario_MOCK' por tu 
            # función real para enchufar la vista de stock.
            btn_inventario = ttk.Button(self.frame_menu, text="Inventario y Stock", command=self.abrir_modulo_inventario_MOCK)
            btn_inventario.pack(fill="x", pady=5)

        ttk.Separator(self.frame_menu, orient="horizontal").pack(fill="x", pady=15)



        # ========================
+       #  ZONA DE ADMINISTRACIÓN
        # ========================

        if es_admin:
            btn_backup = ttk.Button(self.frame_menu, text="Backup Sistema", command=self.ejecutar_backup)
            btn_backup.pack(fill="x", pady=5)

        ttk.Separator(self.frame_menu, orient="horizontal").pack(fill="x", pady=15)

        btn_salir = ttk.Button(self.frame_menu, text="Cerrar Sesión", command=self.cerrar_sesion)
        btn_salir.pack(fill="x", pady=5, side="bottom")



        # ========================
        #  ÁREA CENTRAL (Derecha)
        # ========================

        self.frame_contenido = ttk.Frame(self.root, relief="sunken", padding=10)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")

        self.lbl_bienvenida = ttk.Label(
            self.frame_contenido, 
            text=f"Bienvenido al Sistema Frankie, {self.usuario_actual.username}.\nSeleccioná una opción del menú lateral.",
            justify="center",
            font=("Arial", 14)
        )
        self.lbl_bienvenida.place(relx=0.5, rely=0.5, anchor="center")



    # ===========================
    #  FUNCIONES DE ORQUESTACIÓN
    # ===========================

    def limpiar_area_central(self):
        """Borra la pantalla actual antes de cargar una nueva."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def abrir_modulo_rrhh(self):
        self.limpiar_area_central()
        vista_rrhh = InterfazRRHH(self.frame_contenido)
        vista_rrhh.pack(fill="both", expand=True)

    def ejecutar_backup(self):
        """Llama al Controlador para hacer el respaldo de la base de datos."""
        orquestador = OrquestadorCore()
        resultado = orquestador.ejecutar_backup()
        
        # La vista solo muestra el texto que le devuelve el orquestador.
        if "exitoso" in resultado.lower():
            messagebox.showinfo("Backup Completado", resultado)
        else:
            messagebox.showerror("Error de Backup", resultado)

    def cerrar_sesion(self):
        if messagebox.askyesno("Salir", "¿Estás seguro que querés cerrar la sesión?"):
            self.root.destroy()



    # =========================================================================
    #  ⚠️ MOCKS PARA EL EQUIPO (URIEL Y ALICIA)
    #  Reemplacen estas funciones por las reales importando sus clases arriba.
    # =========================================================================
    
    def abrir_modulo_ventas_MOCK(self):
        self.limpiar_area_central()
        ttk.Label(self.frame_contenido, text="Módulo de Ventas en construcción (Uriel)...", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")

    def abrir_modulo_inventario_MOCK(self):
        self.limpiar_area_central()
        ttk.Label(self.frame_contenido, text="Módulo de Inventario en construcción (Alicia)...", font=("Arial", 16)).place(relx=0.5, rely=0.5, anchor="center")