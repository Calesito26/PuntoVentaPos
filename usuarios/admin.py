from django.contrib import admin
from usuarios.models import UsuarioSede

@admin.register(UsuarioSede)
class UsuarioSedeAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'sede')
    search_fields = ('usuario__username', 'sede__nombre')