from django.conf import settings
from django.db import models

from inventario.models import Sede


class UsuarioSede(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuario_sede'
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f'{self.usuario.username} - {self.sede.nombre}'