from django.db import models


class CategoriaGasto(models.Model):
    nombre = models.CharField(
        max_length=150
    )

    activo = models.BooleanField(
        default=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre