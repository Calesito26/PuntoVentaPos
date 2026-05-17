from django.shortcuts import render
from django.db.models import F
from django.db.models import Q
from inventario.models import Sede
from inventario.models import StockBodega
from usuarios.decorators import vendedor_required


@vendedor_required
def baja_existencia_list(request):
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True,
        stock__lte=F('stock_minimo')
    )

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)

    if buscar:
        stocks = stocks.filter( Q(producto__nombre__icontains=buscar) | Q(producto__codigo__icontains=buscar))

    stocks = stocks.order_by('sede__nombre', 'producto__nombre')

    return render(
        request,
        'inventario/baja_existencia_list.html',
        {
            'stocks': stocks,
            'sedes': sedes,
            'sede_id': sede_id,
            'buscar': buscar,
        }
    )