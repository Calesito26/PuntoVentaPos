from django.db import models


class Categoria(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True
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
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre