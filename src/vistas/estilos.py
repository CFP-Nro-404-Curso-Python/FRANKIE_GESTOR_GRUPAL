"""
===============================================================================
MÓDULO UNIFICADO DE ESTILOS Y APARIENCIA GLOBAL (vistas/estilos.py)
===============================================================================
Centraliza paletas de colores accesibles (WCAG), tipografía 'Atkinson Hyperlegible New'
(tamaños >= 12pt) y estilos personalizados de ttk.
===============================================================================
"""

from tkinter import ttk

# ==========================================
#  PALETA DE COLORES Y VARIABLES GLOBALES (WCAG Compliant)
# ==========================================
COLOR_FONDO = "#F5F7FA"         # Gris claro de fondo general
COLOR_TARJETA = "#FFFFFF"       # Blanco puro para contenedores / tarjetas
COLOR_PRIMARIO = "#2C3E50"      # Azul oscuro corporativo principal
COLOR_SECUNDARIO = "#34495e"    # Azul secundario para paneles de apoyo
COLOR_ACCENTO = "#27ae60"       # Verde menta/esmeralda de alto contraste para acciones
COLOR_TEXTO = "#1A1A1A"         # Negro suave / gris muy oscuro de altísimo contraste (WCAG AAA)
COLOR_TEXTO_MUTED = "#5A6268"   # Gris optimizado para subtítulos / placeholders
COLOR_BLANCO = "#FFFFFF"        # Blanco para textos sobre fondos oscuros
COLOR_ERROR = "#C0392B"         # Rojo oscuro optimizado para alertas de error
COLOR_FOCO = "#D1ECF1"          # Fondo destacado de alto contraste para campos activos (Foco teclado)

# ==========================================
#  TIPOGRAFÍA ACCESIBLE (Atkinson Hyperlegible New >= 12pt)
# ==========================================
FUENTE_BASE = ("Atkinson Hyperlegible New", 12)
FUENTE_TITULO = ("Atkinson Hyperlegible New", 14, "bold")
FUENTE_ENCABEZADO = ("Atkinson Hyperlegible New", 12, "bold")


def aplicar_estilos_base(root):
    """
    Configura la hoja de estilos global de ttk aplicando criterios WCAG:
    - Tipografía Atkinson Hyperlegible New con tamaños accesibles (>= 12pt).
    - Colores de alto contraste para evitar fatiga visual y cumplir normativas.
    - Indicadores de foco de teclado claros y accesibles.
    """
    style = ttk.Style(root)
    style.theme_use("clam")  # 'clam' permite personalizar colores de forma limpia y robusta

    # Configuración general de la ventana raíz
    root.configure(bg=COLOR_FONDO)

    # 1. Contenedores y Marcos (Frames)
    style.configure(".", background=COLOR_FONDO, font=FUENTE_BASE, foreground=COLOR_TEXTO)

    style.configure("TFrame", background=COLOR_FONDO)
    style.configure("Card.TFrame", background=COLOR_TARJETA, relief="flat")

    style.configure("TLabelframe", background=COLOR_FONDO, borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=COLOR_FONDO, foreground=COLOR_PRIMARIO, font=FUENTE_TITULO)

    # 2. Etiquetas de Texto (Labels)
    style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FUENTE_BASE)
    style.configure("Subtitulo.TLabel", font=FUENTE_TITULO, foreground=COLOR_PRIMARIO, background=COLOR_FONDO)
    style.configure("Muted.TLabel", font=FUENTE_BASE, foreground=COLOR_TEXTO_MUTED, background=COLOR_FONDO)

    # 3. Entradas de Texto (Inputs / Entries)
    style.configure(
        "TEntry",
        fieldbackground=COLOR_BLANCO,
        foreground=COLOR_TEXTO,
        padding=6,
        font=FUENTE_BASE
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", COLOR_FOCO)],
        bordercolor=[("focus", COLOR_PRIMARIO)]
    )

    # 4. Botones accesibles
    style.configure(
        "TButton",
        font=FUENTE_ENCABEZADO,
        padding=(12, 8),
        background=COLOR_PRIMARIO,
        foreground=COLOR_BLANCO
    )
    style.map(
        "TButton",
        background=[("active", COLOR_ACCENTO), ("disabled", "#BDC3C7")],
        foreground=[("active", COLOR_BLANCO), ("disabled", COLOR_TEXTO_MUTED)]
    )

    # 5. Tablas interactivas (Treeview)
    style.configure(
        "Treeview",
        background=COLOR_BLANCO,
        fieldbackground=COLOR_BLANCO,
        foreground=COLOR_TEXTO,
        rowheight=32,  # Mayor altura para facilitar clics y legibilidad táctil/visual
        font=FUENTE_BASE
    )

    style.configure(
        "Treeview.Heading",
        font=FUENTE_ENCABEZADO,
        background=COLOR_PRIMARIO,
        foreground=COLOR_BLANCO,
        padding=8
    )

    style.map(
        "Treeview",
        background=[("selected", COLOR_ACCENTO)],
        foreground=[("selected", COLOR_BLANCO)]
    )