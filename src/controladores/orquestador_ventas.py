"""
===============================================================================
MÓDULO DE CONTROL: ORQUESTADOR DE VENTAS (controladores/orquestador_ventas.py)
===============================================================================
"""

from typing import List, Dict, Tuple, Optional
from dominio.entidades_ventas import Cliente, Factura, DetalleFactura
from infraestructura.repo_ventas import RepositorioVentas


class OrquestadorVentas:
    PORCENTAJE_IVA = 0.21

    def __init__(self, repo_ventas: Optional[RepositorioVentas] = None):
        self.repo = repo_ventas or RepositorioVentas()

    @classmethod
    def calcular_renglon(cls, cantidad: int, precio_unitario: float, descuento_porc: float) -> float:
        subtotal_bruto = cantidad * precio_unitario
        descuento_monto = subtotal_bruto * (descuento_porc / 100.0)
        return round(subtotal_bruto - descuento_monto, 2)

    @classmethod
    def calcular_totales_factura(cls, lista_detalles: List[DetalleFactura], aplicar_iva: bool = True) -> Tuple[float, float, float]:
        subtotal_base = sum(det.subtotal for det in lista_detalles)
        monto_iva = (subtotal_base * cls.PORCENTAJE_IVA) if aplicar_iva else 0.0
        total_final = subtotal_base + monto_iva
        return round(subtotal_base, 2), round(monto_iva, 2), round(total_final, 2)

    def emitir_factura(self, id_cliente: int, id_vendedor: int, items_raw: List[Dict], aplicar_iva: bool = True) -> Factura:
        cliente = self.repo.obtener_cliente_por_id(id_cliente)
        if not cliente:
            raise ValueError(f"El Cliente con ID #{id_cliente} no existe en el sistema.")

        detalles_entidad: List[DetalleFactura] = []
        for item in items_raw:
            subtotal_item = self.calcular_renglon(item["cantidad"], item["precio_unitario"], item.get("descuento", 0.0))
            det = DetalleFactura(
                id_producto=item["id_producto"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio_unitario"],
                descuento_porcentaje=item.get("descuento", 0.0),
                subtotal=subtotal_item
            )
            detalles_entidad.append(det)

        subtotal_base, monto_iva, total_final = self.calcular_totales_factura(detalles_entidad, aplicar_iva)

        factura = Factura(
            id_factura=None,
            cliente=cliente,
            id_vendedor=id_vendedor,
            subtotal_base=subtotal_base,
            monto_iva=monto_iva,
            total=total_final,
            detalles=detalles_entidad
        )

        return self.repo.guardar_factura(factura)
