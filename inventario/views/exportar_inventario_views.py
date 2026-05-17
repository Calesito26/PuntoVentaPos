import openpyxl

from django.db.models import F
from django.http import HttpResponse

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import StockBodega
from usuarios.decorators import vendedor_required


def obtener_baja_existencia():
    return StockBodega.objects.select_related(
        'producto',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True,
        stock__lte=F('stock_minimo')
    ).order_by('sede__nombre', 'producto__nombre')


def obtener_estado_inventario():
    return StockBodega.objects.select_related(
        'producto',
        'sede'
    ).filter(
        activo=True,
        producto__activo=True
    ).order_by('producto__nombre')


@vendedor_required
def exportar_baja_existencia_excel(request):
    stocks = obtener_baja_existencia()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Baja existencia'

    hoja.append([
        'Item',
        'Bodega',
        'Código',
        'Nombre',
        'Stock',
        'Stock mínimo',
        'Compra',
        'Venta',
        'Estado',
    ])

    for index, stock in enumerate(stocks, start=1):
        hoja.append([
            index,
            stock.sede.nombre,
            stock.producto.codigo,
            stock.producto.nombre,
            float(stock.stock),
            float(stock.stock_minimo),
            float(stock.producto.precio_compra),
            float(stock.producto.precio_venta),
            'Activo' if stock.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=baja_existencia.xlsx'

    workbook.save(response)

    return response


@vendedor_required
def exportar_baja_existencia_pdf(request):
    stocks = obtener_baja_existencia()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=baja_existencia.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Productos de baja existencia')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Bodega')
    pdf.drawString(150, y, 'Código')
    pdf.drawString(230, y, 'Nombre')
    pdf.drawString(410, y, 'Stock')
    pdf.drawString(470, y, 'Mínimo')
    y -= 15

    pdf.setFont('Helvetica', 8)

    for index, stock in enumerate(stocks, start=1):
        if y < 40:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, stock.sede.nombre[:12])
        pdf.drawString(150, y, stock.producto.codigo[:12])
        pdf.drawString(230, y, stock.producto.nombre[:28])
        pdf.drawString(410, y, str(stock.stock))
        pdf.drawString(470, y, str(stock.stock_minimo))

        y -= 15

    pdf.save()

    return response


@vendedor_required
def exportar_estado_inventario_excel(request):
    stocks = obtener_estado_inventario()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Estado inventario'

    hoja.append([
        'Item',
        'Bodega',
        'Código',
        'Nombre',
        'Stock',
        'Compra',
        'Total Costo',
        'Venta',
        'Total Venta',
    ])

    costo_total = 0
    venta_total = 0

    for index, stock in enumerate(stocks, start=1):
        total_costo = stock.stock * stock.producto.precio_compra
        total_venta = stock.stock * stock.producto.precio_venta

        costo_total += total_costo
        venta_total += total_venta

        hoja.append([
            index,
            stock.sede.nombre,
            stock.producto.codigo,
            stock.producto.nombre,
            float(stock.stock),
            float(stock.producto.precio_compra),
            float(total_costo),
            float(stock.producto.precio_venta),
            float(total_venta),
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', 'COSTO TOTAL INVENTARIO', float(costo_total)])
    hoja.append(['', '', '', '', '', 'VENTA TOTAL INVENTARIO', float(venta_total)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=estado_inventario.xlsx'

    workbook.save(response)

    return response


@vendedor_required
def exportar_estado_inventario_pdf(request):
    stocks = obtener_estado_inventario()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=estado_inventario.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Estado del inventario')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Código')
    pdf.drawString(150, y, 'Nombre')
    pdf.drawString(330, y, 'Stock')
    pdf.drawString(390, y, 'Compra')
    pdf.drawString(460, y, 'Venta')
    y -= 15

    pdf.setFont('Helvetica', 8)

    costo_total = 0
    venta_total = 0

    for index, stock in enumerate(stocks, start=1):
        total_costo = stock.stock * stock.producto.precio_compra
        total_venta = stock.stock * stock.producto.precio_venta

        costo_total += total_costo
        venta_total += total_venta

        if y < 60:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, stock.producto.codigo[:12])
        pdf.drawString(150, y, stock.producto.nombre[:28])
        pdf.drawString(330, y, str(stock.stock))
        pdf.drawString(390, y, str(stock.producto.precio_compra))
        pdf.drawString(460, y, str(stock.producto.precio_venta))

        y -= 15

    y -= 20
    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(300, y, f'COSTO TOTAL INVENTARIO: {costo_total}')
    y -= 15
    pdf.drawString(300, y, f'VENTA TOTAL INVENTARIO: {venta_total}')

    pdf.save()

    return response