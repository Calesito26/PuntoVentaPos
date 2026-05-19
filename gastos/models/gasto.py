from django.conf import settings
from django.db import models

from gastos.models.categoria_gasto import CategoriaGasto
from compras.models.proveedor import Proveedor


class Gasto(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    categoria = models.ForeignKey(
        CategoriaGasto,
        on_delete=models.PROTECT
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    metodo_pago = models.CharField(max_length=50, default='EFECTIVO')
    tipo_gasto = models.CharField(max_length=20, default='CONTADO')

    valor = models.DecimalField(max_digits=12, decimal_places=2)
    sacar_caja = models.BooleanField(default=False)

    estado = models.CharField(max_length=20, default='PROCESADO')

    es_fijo = models.BooleanField(default=False)
    pagar_fijo = models.BooleanField(default=False)
    sacar_caja_fijo = models.BooleanField(default=False)
    fecha_aplicacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.descripcion