from django.conf import settings
from django.db import models

from compras.models.compra import Compra
from compras.models.proveedor import Proveedor


class DevolucionCompra(models.Model):
    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='devoluciones'
    )
    codigo = models.CharField(max_length=20, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='PROCESADA')

    class Meta:
        verbose_name = 'Devolución de compra'
        verbose_name_plural = 'Devoluciones de compras'
        ordering = ['-fecha']

    def __str__(self):
        return self.codigo