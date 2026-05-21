from django.urls import path

from gastos.views.gasto_categoria_views import *


urlpatterns = [
    path(
        '',
        gasto_categoria_list,
        name='gasto_categoria_list'
    ),

    path(
        'exportar/excel/',
        gasto_categoria_excel,
        name='gasto_categoria_excel'
    ),

    path(
        'exportar/pdf/',
        gasto_categoria_pdf,
        name='gasto_categoria_pdf'
    ),
]