import openpyxl

from django.db.models import F
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from inventario.models import ConfiguracionEmpresa, StockBodega
from core.services.pdf_empresa_service import agregar_cabecera_empresa
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
        'Productos de Baja Existencia'
    )

    data = [[
        'Item',
        'Bodega',
        'Código',
        'Nombre',
        'Stock',
        'Mínimo',
        'Compra',
        'Venta',
        'Estado',
    ]]

    for index, stock in enumerate(stocks, start=1):
        data.append([
            str(index),
            stock.sede.nombre,
            stock.producto.codigo,
            stock.producto.nombre,
            str(stock.stock),
            str(stock.stock_minimo),
            str(stock.producto.precio_compra),
            str(stock.producto.precio_venta),
            'Activo' if stock.activo else 'Inactivo',
        ])

    tabla = Table(
        data,
        colWidths=[30, 70, 60, 130, 45, 45, 50, 50, 45]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  10),
        ('TOPPADDING',    (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

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
        'Estado del Inventario'
    )

    data = [[
        'Item',
        'Código',
        'Nombre',
        'Stock',
        'Compra',
        'T. Costo',
        'Venta',
        'T. Venta',
    ]]

    costo_total = 0
    venta_total = 0

    for index, stock in enumerate(stocks, start=1):
        total_costo = stock.stock * stock.producto.precio_compra
        total_venta = stock.stock * stock.producto.precio_venta

        costo_total += total_costo
        venta_total += total_venta

        data.append([
            str(index),
            stock.producto.codigo,
            stock.producto.nombre,
            str(stock.stock),
            str(stock.producto.precio_compra),
            str(round(total_costo, 2)),
            str(stock.producto.precio_venta),
            str(round(total_venta, 2)),
        ])

    data.append(['', '', '', '', '', '', '', ''])
    data.append(['', '', '', '', 'COSTO TOTAL', str(round(costo_total, 2)), '', ''])
    data.append(['', '', '', '', 'VENTA TOTAL', str(round(venta_total, 2)), '', ''])

    tabla = Table(
        data,
        colWidths=[30, 65, 140, 45, 55, 60, 55, 60]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0),  (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',      (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0),  (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0),  (-1, 0),  10),
        ('TOPPADDING',    (0, 1),  (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1),  (-1, -1), 6),
        ('ALIGN',         (0, 0),  (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response