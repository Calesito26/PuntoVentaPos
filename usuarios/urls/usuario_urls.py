from django.urls import path

from usuarios.views.usuario_views import usuario_create
from usuarios.views.usuario_views import usuario_list


app_name = 'usuarios'

urlpatterns = [
    path('', usuario_list, name='usuario_list'),
    path('nuevo/', usuario_create, name='usuario_create'),
]