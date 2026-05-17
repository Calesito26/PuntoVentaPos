from django.contrib import admin

from productos.models import Categoria
from productos.models import Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'activo',
        'created'
    )

    search_fields = (
        'nombre',
    )

    list_filter = (
        'activo',
    )

    ordering = (
        'nombre',
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'codigo',
        'nombre',
        'categoria',
        'precio_venta',
        'stock',
        'es_insumo',
        'receta_servicio_combo',
        'activo',
    )

    search_fields = (
        'codigo',
        'nombre',
    )

    list_filter = (
        'categoria',
        'es_insumo',
        'receta_servicio_combo',
        'activo',
    )

    ordering = (
        'nombre',
    )