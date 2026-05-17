from django.contrib import admin
from clientes.models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'numero_documento',
        'telefono',
        'activo'
    )

    search_fields = (
        'nombre',
        'numero_documento'
    )