from django.db import models

from compras.models.compra import Compra
from productos.models import Producto


class DetalleCompra(models.Model):

    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle de compra'
        verbose_name_plural = 'Detalles de compras'

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_compra
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.compra.codigo} - {self.producto.nombre}'