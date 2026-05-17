from django.db import models


class Cliente(models.Model):

    TIPO_DOCUMENTO = (
        ('SD', 'Sin documento'),
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carnet Extranjería'),
    )

    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO,
        default='SD'
    )

    numero_documento = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    nombre = models.CharField(
        max_length=255
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=255,
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
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        if self.numero_documento:
            return f'{self.nombre} - {self.numero_documento}'


        return self.nombre