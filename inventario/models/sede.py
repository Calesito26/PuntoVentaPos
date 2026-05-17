from django.db import models


class Sede(models.Model):

    nombre = models.CharField(
        max_length=150,
        unique=True
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    descripcion = models.TextField(
        blank=True,
        null=True
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
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre