import openpyxl

from django.http import HttpResponse
from django.db.models import Q

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from inventario.models import StockBodega, ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import vendedor_required


def obtener_stocks_categoria(request):
    categoria_id = request.GET.get('categoria', '').strip()
    sede_id = request.GET.get('sede', '').strip()
    buscar = request.GET.get('buscar', '').strip()

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

    return stocks.order_by(
        'producto__categoria__nombre',
        'producto__nombre'
    )


@vendedor_required
def exportar_inventario_categoria_excel(request):
    stocks = obtener_stocks_categoria(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Inventario Categorias'

    hoja.append([
        'Item',
        'Categoría',
        'Bodega',
        'Código',
        'Producto',
        'Cantidad',
        'Valor compra',
        'Total',
    ])

    total_general = 0

    for index, stock in enumerate(stocks, start=1):
        total = stock.stock * stock.producto.precio_compra
        total_general += total

        hoja.append([
            index,
            stock.producto.categoria.nombre if stock.producto.categoria else '-',
            stock.sede.nombre,
            stock.producto.codigo,
            stock.producto.nombre,
            float(stock.stock),
            float(stock.producto.precio_compra),
            float(total),
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', '', 'TOTAL', float(total_general)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=inventario_por_categorias.xlsx'

    workbook.save(response)
    return response


@vendedor_required
def exportar_inventario_categoria_pdf(request):
    stocks = obtener_stocks_categoria(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=inventario_por_categorias.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    elementos = []

    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Inventario por Categorías'
    )

    data = [[
        'Item',
        'Categoría',
        'Bodega',
        'Código',
        'Producto',
        'Cantidad',
        'Compra',
        'Total',
    ]]

    total_general = 0

    for index, stock in enumerate(stocks, start=1):
        total = stock.stock * stock.producto.precio_compra
        total_general += total

        data.append([
            str(index),
            stock.producto.categoria.nombre if stock.producto.categoria else '-',
            stock.sede.nombre,
            stock.producto.codigo,
            stock.producto.nombre,
            str(int(stock.stock)),
            f'S/ {stock.producto.precio_compra:.2f}',
            f'S/ {total:.2f}',
        ])

    data.append(['', '', '', '', '', '', 'TOTAL', f'S/ {total_general:.2f}'])

    tabla = Table(
        data,
        colWidths=[25, 80, 70, 60, 110, 45, 55, 60]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0),  (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',      (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0),  (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0),  (-1, 0),  12),
        ('TOPPADDING',    (0, 1),  (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1),  (-1, -1), 8),
        ('ALIGN',         (0, 0),  (-1, -1), 'LEFT'),
        ('ALIGN',         (7, 1),  (7, -1),  'RIGHT'),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response