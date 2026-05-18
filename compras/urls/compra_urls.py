from django.urls import path

from compras.views.nueva_compra_views import nueva_compra
from compras.views.nueva_compra_views import guardar_compra
from compras.views.proveedor_views import crear_proveedor_ajax
from compras.views.proveedor_views import consultar_documento_proveedor_ajax
from compras.views.nueva_compra_views import listar_compras_pendientes
from compras.views.nueva_compra_views import cargar_compra_pendiente
from compras.views.nueva_compra_views import eliminar_compra_pendiente

app_name = 'compras'

urlpatterns = [
    path('nueva/',nueva_compra,name='nueva_compra'),
    path('guardar/',guardar_compra,name='guardar_compra'),
    path('proveedores/crear/ajax/',crear_proveedor_ajax,name='crear_proveedor_ajax'),
    path('proveedores/consultar-documento/ajax/',consultar_documento_proveedor_ajax,name='consultar_documento_proveedor_ajax'),
    path('pendientes/',listar_compras_pendientes,name='listar_compras_pendientes'),
    path('pendientes/<int:pk>/',cargar_compra_pendiente,name='cargar_compra_pendiente'),
    path('pendientes/<int:pk>/eliminar/',eliminar_compra_pendiente,name='eliminar_compra_pendiente'),
]