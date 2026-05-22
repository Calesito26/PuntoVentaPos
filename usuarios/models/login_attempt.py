from datetime import timedelta

from django.db import models
from django.utils import timezone


class LoginAttempt(models.Model):

    username = models.CharField(
        max_length=150
    )

    ip_address = models.CharField(
        max_length=255
    )

    intentos = models.IntegerField(
        default=0
    )

    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    def esta_bloqueado(self):

        if (
            self.bloqueado_hasta
            and
            self.bloqueado_hasta > timezone.now()
        ):
            return True

        return False

    def bloquear(self):

        self.bloqueado_hasta = (
            timezone.now()
            + timedelta(minutes=30)
        )

        self.save()

    def reiniciar(self):

        self.intentos = 0
        self.bloqueado_hasta = None
        self.save()