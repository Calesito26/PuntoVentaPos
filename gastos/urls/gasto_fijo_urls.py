from django.urls import path

from gastos.views.gasto_fijo_views import *


urlpatterns = [
    path(
        '',
        gasto_fijo_list,
        name='gasto_fijo_list'
    ),

    path(
        'marcar/<int:gasto_id>/ajax/',
        marcar_gasto_fijo_ajax,
        name='marcar_gasto_fijo_ajax'
    ),

    path(
        'actualizar/<int:gasto_id>/ajax/',
        actualizar_gasto_fijo_ajax,
        name='actualizar_gasto_fijo_ajax'
    ),

    path(
        'aplicar/ajax/',
        aplicar_gastos_fijos,
        name='aplicar_gastos_fijos'
    ),
]