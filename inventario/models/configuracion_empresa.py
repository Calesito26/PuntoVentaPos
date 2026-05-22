from django.db import models


class ConfiguracionEmpresa(models.Model):
    nombre_empresa = models.CharField(
        max_length=200,
        default='PuntoVentaPOS'
    )

    razon_social = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    ruc = models.CharField(
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

    email = models.EmailField(
        blank=True,
        null=True
    )

    pagina_web = models.URLField(
        blank=True,
        null=True
    )

    logo = models.ImageField(
        upload_to='empresa/logo/',
        blank=True,
        null=True
    )

    logo_sidebar = models.ImageField(
        upload_to='empresa/sidebar/',
        blank=True,
        null=True
    )

    pie_ticket = models.TextField(
        blank=True,
        null=True,
        default='Gracias por su compra'
    )

    smtp_email = models.EmailField(
        blank=True,
        null=True
    )

    smtp_password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    smtp_host = models.CharField(
        max_length=100,
        default='smtp.gmail.com'
    )

    smtp_port = models.IntegerField(
        default=587
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
        verbose_name = 'Configuración de Empresa'
        verbose_name_plural = 'Configuración de Empresa'

    def __str__(self):
        return self.nombre_empresa

    @staticmethod
    def obtener_configuracion():
        config = ConfiguracionEmpresa.objects.filter(
            activo=True
        ).first()

        if not config:
            config = ConfiguracionEmpresa.objects.create(
                nombre_empresa='PuntoVentaPOS',
                activo=True
            )

        return config