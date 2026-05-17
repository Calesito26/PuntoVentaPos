from django.db.models import Q
from django.shortcuts import render

from inventario.models import Sede
from inventario.models import StockBodega
from inventario.models import TrasladoBodega
from productos.models import Producto
from usuarios.decorators import vendedor_required


@vendedor_required
def seguimiento_producto_list(request):
    buscar = request.GET.get('buscar', '').strip()
    sede_id = request.GET.get('sede', '')

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    productos = Producto.objects.filter(activo=True).order_by('nombre')

    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) |
            Q(codigo__icontains=buscar)
        )

    stocks = StockBodega.objects.select_related(
        'producto',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    )

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)

    if buscar:
        stocks = stocks.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar)
        )

    traslados = TrasladoBodega.objects.select_related(
        'producto',
        'sede_origen',
        'sede_destino',
        'responsable'
    ).all()

    if buscar:
        traslados = traslados.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar) |
            Q(codigo__icontains=buscar)
        )

    if sede_id:
        traslados = traslados.filter(
            Q(sede_origen_id=sede_id) |
            Q(sede_destino_id=sede_id)
        )

    return render(
        request,
        'inventario/seguimiento_producto_list.html',
        {
            'sedes': sedes,
            'stocks': stocks,
            'traslados': traslados,
            'buscar': buscar,
            'sede_id': sede_id,
        }
    )