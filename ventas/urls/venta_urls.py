from django.urls import path

from ventas.views.pos_views import pos_venta
from ventas.views.pos_views import agregar_producto_scanner
from ventas.views.pos_views import quitar_producto_carrito
from ventas.views.pos_views import limpiar_carrito
from ventas.views.pos_views import confirmar_venta
from ventas.views.pos_views import ticket_venta
from ventas.views.pos_views import aumentar_cantidad
from ventas.views.pos_views import disminuir_cantidad
from ventas.views.pos_views import guardar_venta_espera
from ventas.views.pos_views import cargar_venta_espera
from ventas.views.pos_views import eliminar_venta_espera
from ventas.views.pos_views import seleccionar_sede_pos
from ventas.views.pos_views import resumen_venta
from ventas.views.pos_views import (imprimir_ticket, imprimir_carta, enviar_factura_correo,)

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
    path('guardar_espera/', guardar_venta_espera, name='guardar_venta_espera'),
    path('guardar-espera/',guardar_venta_espera, name='guardar_venta_espera'),
    path('espera/<int:venta_id>/eliminar/',eliminar_venta_espera,name='eliminar_venta_espera'),
    path('espera/<int:venta_id>/cargar/', cargar_venta_espera, name='cargar_venta_espera'),
    path('seleccionar-sede/',seleccionar_sede_pos, name='seleccionar_sede_pos'),
    path('resumen/<int:venta_id>/',resumen_venta,name='resumen_venta'),
    path('imprimir-ticket/<int:venta_id>/',imprimir_ticket, name='imprimir_ticket'),
    path('imprimir-carta/<int:venta_id>/',imprimir_carta,name='imprimir_carta'),
    path('enviar-factura-correo/<int:venta_id>/',enviar_factura_correo,name='enviar_factura_correo'),
]