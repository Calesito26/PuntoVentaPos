from django.urls import path

from clientes.views.cliente_views import cliente_create
from clientes.views.cliente_views import cliente_list
from clientes.views.cliente_views import cliente_update
from clientes.views.cliente_views import buscar_documento
from clientes.views.cliente_detalle_views import cliente_detalle
from clientes.views.exportar_cliente_views import exportar_clientes_excel
from clientes.views.exportar_cliente_views import exportar_clientes_pdf
from clientes.views.eliminar_cliente_views import eliminar_cliente
from clientes.views.importar_cliente_views import importar_clientes
from clientes.views.importar_cliente_views import descargar_ejemplo_clientes
from clientes.views.exportar_cliente_detalle_views import exportar_detalle_cliente_excel
from clientes.views.cliente_views import cliente_create_ajax

app_name = 'clientes'

urlpatterns = [
    path('', cliente_list, name='cliente_list'),
    path('nuevo/', cliente_create, name='cliente_create'),
    path('editar/<int:pk>/', cliente_update, name='cliente_update'),
    path('buscar-documento/', buscar_documento, name='buscar_documento'),
    path('detalle/<int:cliente_id>/',cliente_detalle,name='cliente_detalle'),
    path('exportar/excel/',exportar_clientes_excel,name='exportar_clientes_excel'),
    path('exportar/pdf/',exportar_clientes_pdf,name='exportar_clientes_pdf'),
    path('eliminar/<int:cliente_id>/',eliminar_cliente,name='eliminar_cliente'),
    path('importar/',importar_clientes,name='importar_clientes'),
    path('ejemplo/',descargar_ejemplo_clientes,name='descargar_ejemplo_clientes'),
    path('detalle/<int:cliente_id>/exportar/excel/',exportar_detalle_cliente_excel,name='exportar_detalle_cliente_excel'),
    path('crear/ajax/', cliente_create_ajax, name='cliente_create_ajax'),
]