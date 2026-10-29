"""
Módulo de Estilos y Apariencia Global (Simil CSS)
Centraliza paletas de colores, fuentes, dimensiones y estilos de ttk.
Cualquier cambio aquí se refleja automáticamente en todas las pantallas.
"""

import tkinter as tk
from tkinter import ttk

# ==========================================
#  VARIABLES GLOBALES DE DISEÑO (Variables CSS)
# ==========================================
COLOR_FONDO = "#F5F7FA"  # Gris claro de fondo
COLOR_TARJETA = "#FFFFFF"  # Blanco para contenedores
COLOR_PRIMARIO = "#2C3E50"  # Azul oscuro corporativo
COLOR_ACCENTO = "#18BC9C"  # Verde menta/turquesa para acciones
COLOR_TEXTO = "#2B2B2B"  # Gris oscuro de alto contraste
COLOR_TEXTO_MUTED = "#6C757D"  # Gris medio para subtítulos/placeholders
COLOR_FOCO = "#E8F0FE"  # Fondo para campos activos (Foco teclado)

FUENTE_BASE = ("Segoe UI", 10)
FUENTE_TITULO = ("Segoe UI", 12, "bold")
FUENTE_ENCABEZADO = ("Segoe UI", 10, "bold")


def aplicar_estilos_base(root):
    """
    Configura la hoja de estilos global de ttk.
    Aplica temas de alto contraste, tipografía accesible y foco visible.
    """
    style = ttk.Style(root)
    style.theme_use(
        "clam")  # 'clam' permite personalizar colores de forma limpia

    # Configuración general de la ventana
    root.configure(bg=COLOR_FONDO)

    # 1. Contenedores y Marcos (Frames)
    style.configure(".", background=COLOR_FONDO, font=FUENTE_BASE,
                    foreground=COLOR_TEXTO)

    style.configure("TFrame", background=COLOR_FONDO)
    style.configure("Card.TFrame", background=COLOR_TARJETA, relief="flat")

    style.configure("TLabelframe", background=COLOR_FONDO, borderwidth=1,
                    relief="solid")
    style.configure("TLabelframe.Label", background=COLOR_FONDO,
                    foreground=COLOR_PRIMARIO, font=FUENTE_TITULO)

    # 2. Etiquetas de Texto
    style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO,
                    font=FUENTE_BASE)
    style.configure("Subtitulo.TLabel", font=FUENTE_TITULO,
                    foreground=COLOR_PRIMARIO)

    # 3. Entradas de Texto (Inputs)
    style.configure("TEntry", fieldbackground="#FFFFFF", foreground=COLOR_TEXTO,
                    padding=5)
    style.map("TEntry",
              fieldbackground=[("focus", COLOR_FOCO)],
              bordercolor=[("focus", COLOR_PRIMARIO)]
              )

    # 4. Botones
    style.configure("TButton", font=FUENTE_ENCABEZADO, padding=(10, 6),
                    background=COLOR_PRIMARIO, foreground="#FFFFFF")
    style.map("TButton",
              background=[("active", COLOR_ACCENTO), ("disabled", "#BDC3C7")],
              foreground=[("active", "#FFFFFF")]
              )

    # 5. Tablas (Treeview)
    style.configure("Treeview",
                    background="#FFFFFF",
                    fieldbackground="#FFFFFF",
                    foreground=COLOR_TEXTO,
                    rowheight=28,
                    font=FUENTE_BASE)

    style.configure("Treeview.Heading",
                    font=FUENTE_ENCABEZADO,
                    background=COLOR_PRIMARIO,
                    foreground="#FFFFFF",
                    padding=6)

    style.map("Treeview",
              background=[("selected", COLOR_ACCENTO)],
              foreground=[("selected", "#FFFFFF")])