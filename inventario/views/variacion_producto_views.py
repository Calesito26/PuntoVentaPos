from django.shortcuts import render

from inventario.models import StockBodega
from productos.models import Categoria
from usuarios.decorators import vendedor_required


@vendedor_required
def variacion_producto_list(request):
    categoria_id = request.GET.get('categoria', '')
    buscar = request.GET.get('buscar', '').strip()

    categorias = Categoria.objects.filter(
        activo=True
    ).order_by('nombre')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    )

    if categoria_id:
        stocks = stocks.filter(
            producto__categoria_id=categoria_id
        )

    if buscar:
        stocks = stocks.filter(
            producto__nombre__icontains=buscar
        )

    stocks = stocks.order_by(
        'producto__categoria__nombre',
        'producto__nombre'
    )

    return render(
        request,
        'inventario/variacion_producto_list.html',
        {
            'stocks': stocks,
            'categorias': categorias,
            'categoria_id': categoria_id,
            'buscar': buscar,
        }
    )