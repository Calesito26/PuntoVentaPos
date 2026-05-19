from django.db.models import Q
from django.shortcuts import render

from compras.models import Compra
from inventario.models import Sede
from usuarios.decorators import administrador_required

import json
from django.http import JsonResponse
from django.db import transaction
from compras.models import DetalleCompra
from inventario.models import StockBodega
from django.shortcuts import get_object_or_404

@administrador_required
def historial_compra_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    estado = request.GET.get('estado', '')
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    compras = Compra.objects.select_related(
        'proveedor',
        'sede',
        'responsable'
    ).all()

    if fecha_inicio:
        compras = compras.filter(fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        compras = compras.filter(fecha_compra__date__lte=fecha_fin)

    if estado:
        compras = compras.filter(estado=estado)

    if sede_id:
        compras = compras.filter(sede_id=sede_id)

    if buscar:
        compras = compras.filter(
            Q(codigo__icontains=buscar) |
            Q(numero_comprobante__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar) |
            Q(proveedor__numero_documento__icontains=buscar)
        )

    total_compras = sum(compra.total for compra in compras)

    return render(
        request,
        'compras/historial_compra_list.html',
        {
            'compras': compras,
            'sedes': sedes,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'estado': estado,
            'sede_id': sede_id,
            'buscar': buscar,
            'total_compras': total_compras,
        }
    )

@administrador_required
def compra_devolucion_data(request, pk):
    compra = Compra.objects.prefetch_related(
        'detalles',
        'detalles__producto'
    ).select_related(
        'proveedor',
        'sede'
    ).filter(
        id=pk
    ).first()

    if not compra:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Compra no encontrada.'
        })

    productos = []

    for detalle in compra.detalles.all():
        productos.append({
            'producto_id': detalle.producto.id,
            'producto': detalle.producto.nombre,
            'precio_compra': float(detalle.precio_compra),
            'cantidad': float(detalle.cantidad),
        })

    return JsonResponse({
        'ok': True,
        'id': compra.id,
        'codigo': compra.codigo,
        'documento': compra.proveedor.numero_documento,
        'proveedor': compra.proveedor.razon_social,
        'productos': productos,
    })


@administrador_required
@transaction.atomic
def procesar_devolucion_compra(request, pk):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    compra = Compra.objects.select_related(
        'sede'
    ).filter(
        id=pk
    ).first()

    if not compra:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Compra no encontrada.'
        })

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Datos inválidos.'
        })

    items = data.get('items', [])

    if not items:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Ingrese productos a devolver.'
        })

    from decimal import Decimal

    total_devuelto = Decimal('0.00')

    for item in items:
        producto_id = item.get('producto_id')
        cantidad_devolver = Decimal(str(item.get('cantidad', 0)))

        if not producto_id or cantidad_devolver <= 0:
            continue

        detalle = DetalleCompra.objects.filter(
            compra=compra,
            producto_id=producto_id
        ).first()

        if not detalle:
            return JsonResponse({
                'ok': False,
                'mensaje': 'El producto no pertenece a esta compra.'
            })

        if cantidad_devolver > detalle.cantidad:
            return JsonResponse({
                'ok': False,
                'mensaje': f'No puede devolver más unidades de {detalle.producto.nombre}.'
            })

        stock = StockBodega.objects.filter(
            sede=compra.sede,
            producto_id=producto_id
        ).first()

        if stock:
            stock.stock -= cantidad_devolver
            stock.save()

        detalle.cantidad -= cantidad_devolver
        detalle.cantidad_devuelta += cantidad_devolver
        detalle.subtotal = detalle.cantidad * detalle.precio_compra
        detalle.save()

        total_devuelto += cantidad_devolver * detalle.precio_compra

    compra.total -= total_devuelto

    if compra.total < 0:
        compra.total = Decimal('0.00')

    compra.save()

    return JsonResponse({
        'ok': True,
        'mensaje': 'Devolución procesada correctamente.'
    })


@administrador_required
def eliminar_compra(request, pk):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    compra = Compra.objects.filter(id=pk).first()

    if not compra:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Compra no encontrada.'
        })

    compra.estado = 'ANULADA'
    compra.save()

    return JsonResponse({
        'ok': True,
        'mensaje': 'Compra anulada correctamente.'
    })

@administrador_required
def imprimir_compra(request, pk):
    compra = get_object_or_404(
        Compra.objects.select_related(
            'proveedor',
            'sede',
            'responsable'
        ).prefetch_related(
            'detalles',
            'detalles__producto'
        ),
        pk=pk
    )

    return render(
        request,
        'compras/imprimir_compra.html',
        {
            'compra': compra
        }
    )