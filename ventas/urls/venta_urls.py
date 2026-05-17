from django.urls import path

from ventas.views.pos_views import pos_venta
from ventas.views.pos_views import agregar_producto_scanner
from ventas.views.pos_views import quitar_producto_carrito
from ventas.views.pos_views import limpiar_carrito
from ventas.views.pos_views import confirmar_venta
from ventas.views.pos_views import ticket_venta
from ventas.views.pos_views import aumentar_cantidad
from ventas.views.pos_views import disminuir_cantidad


app_name = 'ventas'

urlpatterns = [
    path('', pos_venta, name='pos_venta'),
    path('agregar/', agregar_producto_scanner, name='agregar_producto_scanner'),
    path('quitar/<int:producto_id>/', quitar_producto_carrito, name='quitar_producto_carrito'),
    path('limpiar/', limpiar_carrito, name='limpiar_carrito'),
    path('confirmar/', confirmar_venta, name='confirmar_venta'),
    path('ticket/<int:venta_id>/', ticket_venta, name='ticket_venta'),
    path('aumentar/<int:producto_id>/', aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir/<int:producto_id>/', disminuir_cantidad, name='disminuir_cantidad'),
]