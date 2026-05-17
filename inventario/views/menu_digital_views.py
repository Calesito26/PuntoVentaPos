from django.shortcuts import render

from inventario.models import StockBodega
from productos.models import Categoria
from usuarios.decorators import vendedor_required


@vendedor_required
def menu_digital_productos(request):
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

    stocks = stocks.order_by('producto__nombre')

    return render(
        request,
        'inventario/menu_digital_productos.html',
        {
            'stocks': stocks,
            'categorias': categorias,
            'categoria_id': categoria_id,
            'buscar': buscar,
        }
    )