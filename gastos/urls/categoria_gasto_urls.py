from django.urls import path

from gastos.views.categoria_gasto_views import *


urlpatterns = [
    path(
        '',
        categoria_gasto_list,
        name='categoria_gasto_list'
    ),

    path(
        'guardar/',
        categoria_gasto_save,
        name='categoria_gasto_save'
    ),

    path(
        'eliminar/<int:pk>/',
        categoria_gasto_delete,
        name='categoria_gasto_delete'
    ),
    path(
        'exportar/excel/',
        categoria_gasto_excel,
        name='categoria_gasto_excel'
    ),

    path(
        'exportar/pdf/',
        categoria_gasto_pdf,
        name='categoria_gasto_pdf'
    ),
]