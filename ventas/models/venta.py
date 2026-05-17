from django.db import models
from clientes.models import Cliente


class Venta(models.Model):

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    METODOS_PAGO = (
        ('EFECTIVO', 'EFECTIVO'),
        ('YAPE', 'YAPE'),
        ('PLIN', 'PLIN'),
        ('TARJETA', 'TARJETA'),
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='EFECTIVO'
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'Venta #{self.id}'
    