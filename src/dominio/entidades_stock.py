"""
===============================================================================
MÓDULO 4: GESTIÓN DE INVENTARIOS Y PROVEEDORES
Entregable 1: Entidades de Dominio (Proveedor y Producto)
===============================================================================
Este módulo define las clases de datos (Data Classes) para representar
las entidades de Proveedor y Producto de forma limpia, alineadas exactamente
con la estructura de las tablas 'proveedores', 'personas' y 'productos'
definidas en esquema.sql.
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Proveedor:
    """
    Representa a un Proveedor del sistema.
    Combina la extensión de la tabla 'proveedores' con los datos generales
    de contacto provenientes de la tabla 'personas'.
    """
    id_persona: int
    rubro: str
    id: Optional[int] = None
    contacto_secundario: Optional[str] = None

    # Datos complementarios de la entidad Persona (para presentación en UI)
    tipo_persona: str = "Juridica"  # 'Fisica' o 'Juridica'
    razon_social: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_documento: str = "CUIT"
    nro_documento: str = ""
    telefono: Optional[str] = None
    email: Optional[str] = None
    domicilio: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None

    @property
    def nombre_comercial(self) -> str:
        """
        Retorna la Razón Social si es persona Jurídica,
        o el Nombre Completo si es persona Física.
        """
        if self.tipo_persona == "Juridica" and self.razon_social:
            return self.razon_social

        partes = [self.apellidos, self.nombres]
        nombre_completo = " ".join(p for p in partes if p)
        return nombre_completo if nombre_completo else "Sin Nombre / Razón Social"


@dataclass
class Producto:
    """
    Representa un Artículo / Producto dentro del Inventario.
    Corresponde directamente a la tabla 'productos' en esquema.sql.
    """
    codigo: str
    descripcion: str
    id_proveedor: int
    precio_costo: float
    precio_venta: float
    id: Optional[int] = None
    stock_actual: int = 0
    stock_minimo: int = 5
    categoria: Optional[str] = None
    ubicacion: Optional[str] = None
    vencimiento: Optional[str] = None

    # Atributo informativo (nombre del proveedor para mostrar en tablas Tkinter)
    nombre_proveedor: str = field(default="", repr=False)

    @property
    def requiere_reposicion(self) -> bool:
        """
        Regla de Negocio / Alerta:
        Retorna True si el stock actual está en o por debajo del stock mínimo exigido.
        Se activa la alerta para emisión de Orden de Compra.
        """
        return self.stock_actual <= self.stock_minimo

    @property
    def margen_ganancia(self) -> float:
        """ Retorna el margen de ganancia nominal por unidad. """
        return self.precio_venta - self.precio_costo