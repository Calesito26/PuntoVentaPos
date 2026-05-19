from django.urls import path

from compras.views.nueva_compra_views import nueva_compra
from compras.views.nueva_compra_views import guardar_compra
from compras.views.proveedor_views import crear_proveedor_ajax
from compras.views.proveedor_views import consultar_documento_proveedor_ajax
from compras.views.nueva_compra_views import listar_compras_pendientes
from compras.views.nueva_compra_views import cargar_compra_pendiente
from compras.views.nueva_compra_views import eliminar_compra_pendiente
from compras.views.historial_compra_views import historial_compra_list
from compras.views.historial_compra_views import compra_devolucion_data
from compras.views.historial_compra_views import procesar_devolucion_compra
from compras.views.historial_compra_views import eliminar_compra
from compras.views.historial_compra_views import imprimir_compra
from compras.views.exportar_historial_compra_views import exportar_historial_compras_excel
from compras.views.exportar_historial_compra_views import exportar_historial_compras_pdf

app_name = 'compras'

urlpatterns = [
    path('nueva/',nueva_compra,name='nueva_compra'),
    path('guardar/',guardar_compra,name='guardar_compra'),
    path('proveedores/crear/ajax/',crear_proveedor_ajax,name='crear_proveedor_ajax'),
    path('proveedores/consultar-documento/ajax/',consultar_documento_proveedor_ajax,name='consultar_documento_proveedor_ajax'),
    path('pendientes/',listar_compras_pendientes,name='listar_compras_pendientes'),
    path('pendientes/<int:pk>/',cargar_compra_pendiente,name='cargar_compra_pendiente'),
    path('pendientes/<int:pk>/eliminar/',eliminar_compra_pendiente,name='eliminar_compra_pendiente'),
    path('historial/',historial_compra_list,name='historial_compra_list'),
    path('historial/<int:pk>/devolucion/',compra_devolucion_data,name='compra_devolucion_data'),
    path('historial/<int:pk>/devolver/',procesar_devolucion_compra,name='procesar_devolucion_compra'),
    path('historial/<int:pk>/eliminar/',eliminar_compra,name='eliminar_compra'),
    path('historial/<int:pk>/imprimir/',imprimir_compra,name='imprimir_compra'),
    path('historial/exportar/excel/',exportar_historial_compras_excel,name='exportar_historial_compras_excel'),
    path('historial/exportar/pdf/',exportar_historial_compras_pdf,name='exportar_historial_compras_pdf'),
]