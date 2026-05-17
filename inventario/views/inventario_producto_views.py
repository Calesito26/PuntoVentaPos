from django.shortcuts import render

from inventario.models import Sede
from inventario.models import StockBodega
from productos.models import Categoria
from usuarios.decorators import vendedor_required


@vendedor_required
def inventario_producto_list(request):
    sede_id = request.GET.get('sede', '')
    categoria_id = request.GET.get('categoria', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True
    )

    if sede_id:
        stocks = stocks.filter(sede_id=sede_id)

    if categoria_id:
        stocks = stocks.filter(producto__categoria_id=categoria_id)

    if buscar:
        stocks = stocks.filter(producto__nombre__icontains=buscar)

    stocks = stocks.order_by('producto__nombre')

    return render(
        request,
        'inventario/inventario_producto_list.html',
        {
            'stocks': stocks,
            'sedes': sedes,
            'categorias': categorias,
            'sede_id': sede_id,
            'categoria_id': categoria_id,
            'buscar': buscar,
        }
    )