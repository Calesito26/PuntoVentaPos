from django.urls import path

from gastos.views.gasto_views import gasto_list
from gastos.views.gasto_views import crear_gasto_ajax
from gastos.views.gasto_views import eliminar_gasto_ajax
from gastos.views.gasto_views import gasto_excel
from gastos.views.gasto_views import gasto_pdf


urlpatterns = [
    path('', gasto_list, name='gasto_list'),
    path('crear/ajax/',crear_gasto_ajax,name='crear_gasto_ajax'),
    path('eliminar/<int:gasto_id>/ajax/', eliminar_gasto_ajax, name='eliminar_gasto_ajax'),
    path('exportar/excel/',gasto_excel,name='gasto_excel'),
    path('exportar/pdf/',gasto_pdf,name='gasto_pdf'),
]