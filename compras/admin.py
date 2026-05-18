from django.contrib import admin

from compras.models import Proveedor
from compras.models import Compra
from compras.models import DetalleCompra


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'tipo_documento',
        'numero_documento',
        'razon_social',
        'telefono',
        'activo',
    )

    search_fields = (
        'numero_documento',
        'razon_social',
    )

    list_filter = (
        'tipo_documento',
        'activo',
    )


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'codigo',
        'proveedor',
        'sede',
        'fecha_compra',
        'total',
        'estado',
        'responsable',
    )

    search_fields = (
        'codigo',
        'proveedor__razon_social',
        'numero_comprobante',
    )

    list_filter = (
        'estado',
        'sede',
        'tipo_comprobante',
    )

    inlines = [
        DetalleCompraInline
    ]


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'compra',
        'producto',
        'cantidad',
        'precio_compra',
        'subtotal',
    )

    search_fields = (
        'compra__codigo',
        'producto__nombre',
        'producto__codigo',
    )