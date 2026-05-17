from django.conf import settings
from django.db import models

from inventario.models import Sede
from productos.models import Producto


class TrasladoBodega(models.Model):

    ESTADO_CHOICES = (
        ('REALIZADO', 'Realizado'),
        ('ANULADO', 'Anulado'),
    )

    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    sede_origen = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name='traslados_origen'
    )

    sede_destino = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        related_name='traslados_destino'
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT
    )

    cantidad_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    cantidad_traslado = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    cantidad_final = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    valor_traslado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    observacion = models.TextField(
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='REALIZADO'
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Traslado entre bodega'
        verbose_name_plural = 'Traslados entre bodegas'
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = TrasladoBodega.objects.order_by('id').last()

            if ultimo:
                numero = ultimo.id + 1
            else:
                numero = 1

            self.codigo = f'TR-{numero:06d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.codigo} - {self.producto.nombre}'