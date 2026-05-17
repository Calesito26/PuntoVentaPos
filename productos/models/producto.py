from django.db import models

from productos.models.categoria import Categoria


class Producto(models.Model):

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    nombre = models.CharField(
        max_length=150
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True
    )

    imagen_url = models.URLField(
        blank=True,
        null=True
    )

    barcode_image = models.ImageField(
        upload_to='barcodes/',
        blank=True,
        null=True
    )

    activo = models.BooleanField(
        default=True
    )

    es_insumo = models.BooleanField(
        default=False
    )

    TIPO_RECETA_SERVICIO_COMBO = (
        ('NINGUNO', 'NINGUNO'),
        ('RECETA', 'RECETA'),
        ('SERVICIO', 'SERVICIO'),
        ('COMBO', 'COMBO'),
    )

    receta_servicio_combo = models.CharField(
        max_length=20,
        choices=TIPO_RECETA_SERVICIO_COMBO,
        default='NINGUNO'
    )


    created = models.DateTimeField(
        auto_now_add=True
    )

    updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} - {self.codigo}'