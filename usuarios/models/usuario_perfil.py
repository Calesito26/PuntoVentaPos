from django.contrib.auth.models import User
from django.db import models


class UsuarioPerfil(models.Model):
    TIPO_DOCUMENTO = (
        ('DNI', 'DNI'),
        ('RUC', 'RUC'),
        ('CE', 'Carnet de extranjería'),
    )

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    tipo_documento = models.CharField(
        max_length=10,
        choices=TIPO_DOCUMENTO,
        default='DNI'
    )

    numero_documento = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.usuario.username