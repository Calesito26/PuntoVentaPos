from django.conf import settings
from django.db import models


class Promocion(models.Model):

    nombre = models.CharField(max_length=150)

    fecha_inicio = models.DateTimeField()

    fecha_fin = models.DateTimeField()

    porcentaje_descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre