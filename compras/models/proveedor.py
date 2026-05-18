from django.db import models


class Proveedor(models.Model):

    TIPO_DOCUMENTO = (
        ('RUC', 'RUC'),
        ('DNI', 'DNI'),
        ('CE', 'Carnet Extranjería'),
    )

    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO, default='RUC')
    numero_documento = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)

    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    activo = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon_social']

    def __str__(self):
        return f'{self.razon_social} - {self.numero_documento}'