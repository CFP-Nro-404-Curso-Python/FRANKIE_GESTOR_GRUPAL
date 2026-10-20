from dominio.entidades_core import Persona


class Cliente(Persona):
    def __init__(
        self, nombre, apellido, dni, cuit_cliente, email=None, telefono=None
    ):
        # Invocamos el constructor de la superclase Persona
        super().__init__(nombre, apellido, dni)
        self.cuit_cliente = cuit_cliente
        self.email = email
        self.telefono = telefono

    def __str__(self):
        return (
            f"Cliente: {self.nombre} {self.apellido} (CUIT: {self.cuit_cliente})"
        )


class Factura:
    def __init__(
        self,
        id_factura,
        cliente,
        fecha,
        total,
        detalles=None,
        estado="Pendiente",
    ):
        self.id_factura = id_factura
        self.cliente = cliente  # Instancia de la clase Cliente
        self.fecha = fecha
        self.total = total
        self.detalles = detalles if detalles is not None else []
        self.estado = estado

    def __str__(self):
        return f"Factura #{self.id_factura} - {self.cliente.nombre} {self.cliente.apellido} - Total: ${self.total}"