from django.urls import path

from clientes.views.cliente_views import cliente_create
from clientes.views.cliente_views import cliente_list
from clientes.views.cliente_views import cliente_update
from clientes.views.cliente_views import buscar_documento

app_name = 'clientes'

urlpatterns = [
    path('', cliente_list, name='cliente_list'),
    path('nuevo/', cliente_create, name='cliente_create'),
    path('editar/<int:pk>/', cliente_update, name='cliente_update'),
    path('buscar-documento/', buscar_documento, name='buscar_documento'),
]