import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from compras.models import Compra
from compras.models import Proveedor
from compras.services.compra_service import CompraService
from inventario.models import Sede
from inventario.models import StockBodega
from usuarios.decorators import administrador_required


@administrador_required
def nueva_compra(request):
    buscar = request.GET.get('buscar', '').strip()

    productos_stock = StockBodega.objects.select_related(
        'producto',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    )

    if buscar:
        productos_stock = productos_stock.filter(
            producto__nombre__icontains=buscar
        ) | productos_stock.filter(
            producto__codigo__icontains=buscar
        )

    proveedores = Proveedor.objects.filter(activo=True).order_by('razon_social')
    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    return render(
        request,
        'compras/nueva_compra.html',
        {
            'productos_stock': productos_stock,
            'proveedores': proveedores,
            'sedes': sedes,
            'buscar': buscar,
        }
    )


@administrador_required
def guardar_compra(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if not data.get('proveedor'):
            return JsonResponse({'ok': False, 'mensaje': 'Seleccione un proveedor.'})

        if not data.get('sede'):
            return JsonResponse({'ok': False, 'mensaje': 'Seleccione una sede.'})

        if not data.get('productos'):
            return JsonResponse({'ok': False, 'mensaje': 'Agregue productos a la compra.'})

        compra = CompraService.registrar_compra(data, request.user)

        return JsonResponse({
            'ok': True,
            'mensaje': 'Compra registrada correctamente.',
            'codigo': compra.codigo,
            'estado': compra.estado,
        })

    return JsonResponse({'ok': False, 'mensaje': 'Método no permitido.'})

@administrador_required
def listar_compras_pendientes(request):
    compras = Compra.objects.prefetch_related(
        'detalles',
        'detalles__producto'
    ).filter(
        estado='PENDIENTE',
        responsable=request.user
    ).order_by('id')

    data = []

    for compra in compras:
        data.append({
            'id': compra.id,
            'codigo': compra.codigo,
        })

    return JsonResponse({
        'ok': True,
        'compras': data
    })

@administrador_required
def cargar_compra_pendiente(request, pk):
    compra = Compra.objects.prefetch_related(
        'detalles',
        'detalles__producto'
    ).filter(
        id=pk,
        estado='PENDIENTE',
        responsable=request.user
    ).first()

    if not compra:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Compra pendiente no encontrada.'
        })

    productos = []

    for detalle in compra.detalles.all():
        productos.append({
            'producto_id': str(detalle.producto.id),
            'stock': 0,
            'codigo': detalle.producto.codigo,
            'nombre': detalle.producto.nombre,
            'cantidad': float(detalle.cantidad),
            'precio_compra': float(detalle.precio_compra),
            'precio_venta': float(detalle.producto.precio_venta),
            'descuento': 0,
            'retencion': 0,
            'impuesto': 18,
        })

    return JsonResponse({
        'ok': True,
        'id': compra.id,
        'codigo': compra.codigo,
        'productos': productos
    })


@administrador_required
def eliminar_compra_pendiente(request, pk):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    compra = Compra.objects.filter(
        id=pk,
        estado='PENDIENTE',
        responsable=request.user
    ).first()

    if not compra:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Compra pendiente no encontrada.'
        })

    compra.delete()

    return JsonResponse({
        'ok': True,
        'mensaje': 'Compra pendiente eliminada correctamente.'
    })