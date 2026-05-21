from django.conf import settings
from django.db import models

from compras.models.proveedor import Proveedor
from inventario.models import Sede


class Compra(models.Model):

    METODO_PAGO_CHOICES = (
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('YAPE', 'Yape'),
        ('PLIN', 'Plin'),
    )

    metodo_pago = models.CharField(
        max_length=30,
        choices=METODO_PAGO_CHOICES,
        default='EFECTIVO'
    )

    salio_caja = models.BooleanField(default=True)

    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('RECIBIDA', 'Recibida'),
        ('ANULADA', 'Anulada'),
    )

    TIPO_COMPROBANTE = (
        ('FACTURA', 'Factura'),
        ('BOLETA', 'Boleta'),
        ('NOTA', 'Nota de compra'),
        ('NINGUNO', 'Sin comprobante'),
    )

    codigo = models.CharField(max_length=20, unique=True, blank=True)

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT)

    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE, default='FACTURA')
    numero_comprobante = models.CharField(max_length=50, blank=True, null=True)

    fecha_compra = models.DateTimeField(auto_now_add=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RECIBIDA')

    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    observacion = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha_compra']

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Compra.objects.order_by('id').last()
            numero = ultimo.id + 1 if ultimo else 1
            self.codigo = f'COM-{numero:06d}'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo