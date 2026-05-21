import json
from decimal import Decimal, InvalidOperation

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

def validar_precio_compra_productos(productos):
    for item in productos:
        producto_id = item.get('producto_id')

        if not producto_id:
            return {
                'ok': False,
                'mensaje': 'Hay un producto sin ID.'
            }

        stock = StockBodega.objects.select_related(
            'producto'
        ).filter(
            producto_id=producto_id,
            activo=True
        ).first()

        if not stock:
            return {
                'ok': False,
                'mensaje': 'Uno de los productos no existe en bodega.'
            }

        producto = stock.producto

        try:
            precio_compra = Decimal(str(item.get('precio_compra', 0)))
            precio_venta = Decimal(str(producto.precio_venta))
        except (InvalidOperation, TypeError):
            return {
                'ok': False,
                'mensaje': f'Precio inválido en el producto {producto.nombre}.'
            }

        if precio_compra <= 0:
            return {
                'ok': False,
                'mensaje': f'El precio de compra de {producto.nombre} debe ser mayor a 0.'
            }

        if precio_compra > precio_venta:
            return {
                'ok': False,
                'mensaje': (
                    f'No se puede registrar la compra. '
                    f'El producto "{producto.nombre}" tiene precio de compra '
                    f'S/ {precio_compra} mayor que su precio de venta '
                    f'S/ {precio_venta}.'
                )
            }

    return {
        'ok': True,
        'mensaje': 'Precios válidos.'
    }

@administrador_required
def guardar_compra(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if not data.get('proveedor'):
            return JsonResponse({
                'ok': False,
                'mensaje': 'Seleccione un proveedor.'
            })

        if not data.get('sede'):
            return JsonResponse({
                'ok': False,
                'mensaje': 'Seleccione una sede.'
            })

        if not data.get('productos'):
            return JsonResponse({
                'ok': False,
                'mensaje': 'Agregue productos a la compra.'
            })

        validacion = validar_precio_compra_productos(
            data.get('productos')
        )

        if not validacion['ok']:
            return JsonResponse(validacion)

        compra = CompraService.registrar_compra(
            data,
            request.user
        )

        return JsonResponse({
            'ok': True,
            'mensaje': 'Compra registrada correctamente.',
            'codigo': compra.codigo,
            'estado': compra.estado,
        })

    return JsonResponse({
        'ok': False,
        'mensaje': 'Método no permitido.'
    })


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