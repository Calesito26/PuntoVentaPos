from django.db import models

from inventario.models import Sede
from productos.models import Producto


class StockBodega(models.Model):

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='stocks'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='stocks_bodega'
    )

    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stock_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5
    )

    activo = models.BooleanField(
        default=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Stock por bodega'
        verbose_name_plural = 'Stock por bodegas'
        unique_together = ('sede', 'producto')
        ordering = ['producto__nombre']

    def __str__(self):
        return f'{self.producto.nombre} - {self.sede.nombre}: {self.stock}'