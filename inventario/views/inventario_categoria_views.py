from decimal import Decimal

from django.db.models import Q
from django.shortcuts import render

from inventario.models import Sede
from inventario.models import StockBodega
from productos.models import Categoria
from usuarios.decorators import vendedor_required


@vendedor_required
def inventario_categoria_list(request):
    categoria_id = request.GET.get('categoria', '')
    sede_id = request.GET.get('sede', '')
    buscar = request.GET.get('buscar', '').strip()

    categorias = Categoria.objects.filter(
        activo=True
    ).order_by('nombre')

    sedes = Sede.objects.filter(
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

    if sede_id:
        stocks = stocks.filter(
            sede_id=sede_id
        )

    if buscar:
        stocks = stocks.filter(
            Q(producto__nombre__icontains=buscar) |
            Q(producto__codigo__icontains=buscar)
        )

    stocks = stocks.order_by(
        'producto__categoria__nombre',
        'producto__nombre'
    )

    total_inventario = Decimal('0.00')
    labels_grafico = []
    datos_grafico = []

    for stock in stocks:
        stock.total = stock.stock * stock.producto.precio_compra
        total_inventario += stock.total

        labels_grafico.append(stock.producto.nombre)
        datos_grafico.append(float(stock.stock))

    categoria_nombre = 'TODAS'

    if categoria_id:
        categoria = Categoria.objects.filter(id=categoria_id).first()
        if categoria:
            categoria_nombre = categoria.nombre.upper()

    return render(
        request,
        'inventario/inventario_categoria_list.html',
        {
            'stocks': stocks,
            'categorias': categorias,
            'sedes': sedes,
            'categoria_id': categoria_id,
            'sede_id': sede_id,
            'buscar': buscar,
            'total_inventario': total_inventario,
            'labels_grafico': labels_grafico,
            'datos_grafico': datos_grafico,
            'categoria_nombre': categoria_nombre,
        }
    )