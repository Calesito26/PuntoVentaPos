from django.urls import path

from clientes.views.cliente_views import buscar_documento
from usuarios.views.usuario_views import usuario_create
from usuarios.views.usuario_views import usuario_delete
from usuarios.views.usuario_views import usuario_list
from usuarios.views.usuario_views import usuario_update
from usuarios.views.usuario_views import exportar_usuarios_excel
from usuarios.views.usuario_views import exportar_usuarios_pdf
from usuarios.views.auth_views import login_view

app_name = 'usuarios'

urlpatterns = [
    path('login/',login_view,name='login'),
    path('', usuario_list, name='usuario_list'),
    path('nuevo/',usuario_create,name='usuario_create'),
    path('editar/<int:usuario_id>/',usuario_update,name='usuario_update'),
    path('eliminar/<int:usuario_id>/',usuario_delete,name='usuario_delete'),
    path('exportar/excel/',exportar_usuarios_excel,name='exportar_usuarios_excel'),
    path('exportar/pdf/', exportar_usuarios_pdf, name='exportar_usuarios_pdf'),
    path('buscar-documento/',buscar_documento,name='buscar_documento'),
    
]