from django.contrib import admin

from ventas.models import Venta
from ventas.models import DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cliente',
        'metodo_pago',
        'total',
        'created',
    )

    inlines = [
        DetalleVentaInline
    ]