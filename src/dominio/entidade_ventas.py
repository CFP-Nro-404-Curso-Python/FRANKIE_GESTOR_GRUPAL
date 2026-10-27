"""
===============================================================================
MÓDULO DE DOMINIO: ENTIDADES DE VENTAS (dominio/entidades_ventas.py)
===============================================================================
"""

from typing import List, Optional
from dominio.entidades_core import Persona


class Cliente(Persona):
    """ Entidad Cliente. Hereda obligatoriamente de la superclase Persona. """
    def __init__(
        self,
        nombre: str,
        apellido: str,
        dni: str,
        cuit_cliente: str,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        id_cliente: Optional[int] = None,
        id_persona: Optional[int] = None
    ):
        super().__init__(nombre=nombre, apellido=apellido, dni=dni)
        self.id_cliente = id_cliente
        self.id_persona = id_persona or id_cliente
        self.cuit_cliente = cuit_cliente
        self.email = email
        self.telefono = telefono

    def __str__(self):
        return f"Cliente: {self.nombre} {self.apellido} (CUIT: {self.cuit_cliente})"


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
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.descuento_porcentaje = descuento_porcentaje
        self.subtotal = subtotal


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
        self.subtotal_base = subtotal_base
        self.monto_iva = monto_iva
        self.total = total
        self.detalles = detalles if detalles is not None else []
        self.estado = estado

    def __str__(self):
        return f"Factura #{self.id_factura} - {self.cliente.nombre} {self.cliente.apellido} - Total: ${self.total:.2f}"
