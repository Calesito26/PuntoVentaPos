import openpyxl

from django.http import HttpResponse
from django.shortcuts import render

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from inventario.models import StockBodega
from usuarios.decorators import administrador_required


def obtener_stocks_exportar():
    return StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        activo=True
    ).order_by(
        'producto__nombre'
    )


@administrador_required
def preview_exportar_productos(request):
    stocks = obtener_stocks_exportar()

    return render(
        request,
        'inventario/preview_exportar_productos.html',
        {
            'stocks': stocks
        }
    )


@administrador_required
def exportar_productos_excel(request):
    stocks = obtener_stocks_exportar()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Productos'

    hoja.append([
        'Item',
        'Código',
        'Nombre',
        'Categoría',
        'Bodega',
        'Stock',
        'Compra',
        'Venta',
        'Estado',
    ])

    for index, stock in enumerate(stocks, start=1):
        hoja.append([
            index,
            stock.producto.codigo,
            stock.producto.nombre,
            stock.producto.categoria.nombre if stock.producto.categoria else '',
            stock.sede.nombre if stock.sede else '',
            float(stock.stock),
            float(stock.producto.precio_compra),
            float(stock.producto.precio_venta),
            'Activo' if stock.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=productos_inventario.xlsx'

    workbook.save(response)

    return response


@administrador_required
def exportar_productos_pdf(request):
    stocks = obtener_stocks_exportar()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=productos_inventario.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 40

    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(40, y, 'Productos de inventario')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Código')
    pdf.drawString(150, y, 'Nombre')
    pdf.drawString(330, y, 'Bodega')
    pdf.drawString(430, y, 'Stock')
    pdf.drawString(480, y, 'Venta')
    y -= 15

    pdf.setFont('Helvetica', 8)

    for index, stock in enumerate(stocks, start=1):
        if y < 40:
            pdf.showPage()
            y = height - 40
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, stock.producto.codigo)
        pdf.drawString(150, y, stock.producto.nombre[:28])
        pdf.drawString(330, y, stock.sede.nombre[:15])
        pdf.drawString(430, y, str(stock.stock))
        pdf.drawString(480, y, f'S/ {stock.producto.precio_venta}')

        y -= 15

    pdf.save()

    return response