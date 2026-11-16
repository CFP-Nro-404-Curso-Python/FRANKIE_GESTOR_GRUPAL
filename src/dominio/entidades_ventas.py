"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE VENTAS (src/dominio/entidades_ventas.py)
===============================================================================
"""

from typing import List, Optional
from dominio.entidades_persona import Persona


class Cliente(Persona):
    """ Entidad Cliente. Hereda obligatoriamente de la superclase Persona. """
    def __init__(
        self,
        nombres: str = "",
        apellidos: str = "",
        nro_documento: str = "",
        cuit_cliente: str = "",
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        id_cliente: Optional[int] = None,
        id_persona: Optional[int] = None,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        dni: Optional[str] = None
    ):
        nombres_reales = nombres or nombre or ""
        apellidos_reales = apellidos or apellido or ""
        doc_real = nro_documento or dni or ""

        super().__init__(
            id_persona=id_persona,
            nombres=nombres_reales,
            apellidos=apellidos_reales,
            nro_documento=doc_real,
            email=email or "",
            telefono=telefono or ""
        )
        self.id_cliente = id_cliente
        self.id_persona = id_persona  # Declaración explícita para el linter
        self.cuit_cliente = cuit_cliente or doc_real

    @property
    def nombre(self) -> str:
        return self.nombres

    @property
    def apellido(self) -> str:
        return self.apellidos

    def __str__(self):
        return f"Cliente: {self.apellidos}, {self.nombres} (CUIT/DNI: {self.cuit_cliente or self.nro_documento})"


class DetalleFactura:
    """ Representa una línea o renglón dentro de la factura. """
    def __init__(
        self,
        id_producto: int,
        cantidad: int,
        precio_unitario: float,
        descuento_porcentaje: float = 0.0,
        subtotal: float = 0.0,
        id_detalle: Optional[int] = None,
        id_factura: Optional[int] = None
    ):
        self.id_detalle = id_detalle
        self.id_factura = id_factura
        self.id_producto = id_producto
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.descuento_porcentaje = float(descuento_porcentaje)
        self.subtotal = float(subtotal) if subtotal > 0.0 else (self.cantidad * self.precio_unitario * (1 - self.descuento_porcentaje / 100))


class Factura:
    """ Representa la cabecera de la factura de venta. """
    def __init__(
        self,
        id_factura: Optional[int],
        cliente: Cliente,
        id_vendedor: int,
        fecha: Optional[str] = None,
        subtotal_base: float = 0.0,
        monto_iva: float = 0.0,
        total: float = 0.0,
        detalles: Optional[List[DetalleFactura]] = None,
        estado: str = "Emitida"
    ):
        self.id_factura = id_factura
        self.cliente = cliente
        self.id_vendedor = id_vendedor
        self.fecha = fecha
        self.subtotal_base = float(subtotal_base)
        self.monto_iva = float(monto_iva)
        self.total = float(total)
        self.detalles = detalles if detalles is not None else []
        self.estado = estado

    def __str__(self):
        return f"Factura #{self.id_factura} - Cliente: {self.cliente.apellidos}, {self.cliente.nombres} - Total: ${self.total:.2f}"