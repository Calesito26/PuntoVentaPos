import openpyxl

from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.db.models import Q
from inventario.models import StockBodega
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
            stock.producto.categoria.nombre if stock.producto.categoria else '',
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

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Inventario por Categorias')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Codigo')
    pdf.drawString(145, y, 'Producto')
    pdf.drawString(350, y, 'Cant.')
    pdf.drawString(410, y, 'Compra')
    pdf.drawString(480, y, 'Total')
    y -= 15

    pdf.setFont('Helvetica', 8)

    total_general = 0

    for index, stock in enumerate(stocks, start=1):
        total = stock.stock * stock.producto.precio_compra
        total_general += total

        if y < 50:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, stock.producto.codigo[:12])
        pdf.drawString(145, y, stock.producto.nombre[:32])
        pdf.drawString(350, y, str(int(stock.stock)))
        pdf.drawString(410, y, f'S/ {stock.producto.precio_compra:.2f}')
        pdf.drawString(480, y, f'S/ {total:.2f}')

        y -= 15

    y -= 15
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(400, y, f'TOTAL: S/ {total_general:.2f}')

    pdf.save()

    return response