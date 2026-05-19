import json

from django.db.models import Sum
from django.db.models import F
from django.db.models import DecimalField
from django.db.models import ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render

import openpyxl

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from compras.models import DetalleCompra
from productos.models import Categoria
from usuarios.decorators import administrador_required


def obtener_resumen_compras_categoria(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    categoria_id = request.GET.get('categoria', '')

    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'producto__categoria'
    ).filter(
        compra__estado='RECIBIDA'
    )

    if fecha_inicio:
        detalles = detalles.filter(compra__fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        detalles = detalles.filter(compra__fecha_compra__date__lte=fecha_fin)

    if categoria_id:
        detalles = detalles.filter(producto__categoria_id=categoria_id)

    valor_comprado = ExpressionWrapper(
        F('cantidad') * F('precio_compra'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    resumen = detalles.values(
        'producto__categoria__id',
        'producto__categoria__nombre',
        'producto__nombre'
    ).annotate(
        cantidad_total=Coalesce(Sum('cantidad'), 0, output_field=DecimalField()),
        valor_compra=Coalesce(Sum('precio_compra'), 0, output_field=DecimalField()),
        valor_comprado=Coalesce(Sum(valor_comprado), 0, output_field=DecimalField())
    ).order_by(
        'producto__categoria__nombre',
        'producto__nombre'
    )

    grupos = {}

    for item in resumen:
        categoria_nombre = item['producto__categoria__nombre'] or 'SIN CATEGORÍA'

        if categoria_nombre not in grupos:
            grupos[categoria_nombre] = {
                'categoria': categoria_nombre,
                'productos': [],
                'total': 0,
                'labels': [],
                'data': [],
            }

        grupos[categoria_nombre]['productos'].append(item)
        grupos[categoria_nombre]['total'] += item['valor_comprado']
        grupos[categoria_nombre]['labels'].append(
            f"{item['producto__nombre']} - {int(item['cantidad_total'])} Und"
        )
        grupos[categoria_nombre]['data'].append(float(item['cantidad_total']))

    for grupo in grupos.values():
        grupo['labels_json'] = json.dumps(grupo['labels'])
        grupo['data_json'] = json.dumps(grupo['data'])

    return grupos.values()


@administrador_required
def compras_por_categoria_list(request):
    categorias = Categoria.objects.filter(activo=True).order_by('nombre')
    grupos = obtener_resumen_compras_categoria(request)

    return render(
        request,
        'compras/compras_por_categoria_list.html',
        {
            'categorias': categorias,
            'grupos': grupos,
            'fecha_inicio': request.GET.get('fecha_inicio', ''),
            'fecha_fin': request.GET.get('fecha_fin', ''),
            'categoria_id': request.GET.get('categoria', ''),
        }
    )


@administrador_required
def compras_por_categoria_data(request):
    grupos = obtener_resumen_compras_categoria(request)

    data = []

    for grupo in grupos:
        productos = []

        for producto in grupo['productos']:
            productos.append({
                'producto': producto['producto__nombre'],
                'cantidad': int(producto['cantidad_total']),
                'valor_compra': float(producto['valor_compra']),
                'valor_comprado': float(producto['valor_comprado']),
            })

        data.append({
            'categoria': grupo['categoria'],
            'productos': productos,
            'total': float(grupo['total']),
            'labels': grupo['labels'],
            'data': grupo['data'],
        })

    return JsonResponse({
        'ok': True,
        'grupos': data
    })


@administrador_required
def compras_por_categoria_excel(request):
    grupos = obtener_resumen_compras_categoria(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Compras categorias'

    hoja.append([
        'Categoría',
        'Producto',
        'Cantidad',
        'Valor compra',
        'Descuento',
        'Valor comprado'
    ])

    total_general = 0

    for grupo in grupos:
        for producto in grupo['productos']:
            total_general += producto['valor_comprado']

            hoja.append([
                grupo['categoria'],
                producto['producto__nombre'],
                int(producto['cantidad_total']),
                float(producto['valor_compra']),
                0,
                float(producto['valor_comprado']),
            ])

    hoja.append([])
    hoja.append(['', '', '', '', 'TOTAL', float(total_general)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=compras_por_categorias.xlsx'

    workbook.save(response)
    return response


@administrador_required
def compras_por_categoria_pdf(request):
    grupos = obtener_resumen_compras_categoria(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=compras_por_categorias.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Compras por categorias')
    y -= 35

    total_general = 0

    for grupo in grupos:
        if y < 90:
            pdf.showPage()
            y = height - 50

        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(40, y, grupo['categoria'].upper())
        y -= 20

        pdf.setFont('Helvetica-Bold', 8)
        pdf.drawString(40, y, 'Item')
        pdf.drawString(75, y, 'Producto')
        pdf.drawString(270, y, 'Cantidad')
        pdf.drawString(340, y, 'Valor compra')
        pdf.drawString(440, y, 'Valor comprado')
        y -= 15

        pdf.setFont('Helvetica', 8)

        total_categoria = 0

        for index, producto in enumerate(grupo['productos'], start=1):
            if y < 50:
                pdf.showPage()
                y = height - 50

            total_categoria += producto['valor_comprado']
            total_general += producto['valor_comprado']

            pdf.drawString(40, y, str(index))
            pdf.drawString(75, y, str(producto['producto__nombre'])[:30])
            pdf.drawString(270, y, str(int(producto['cantidad_total'])))
            pdf.drawString(340, y, f"S/ {producto['valor_compra']:.2f}")
            pdf.drawString(440, y, f"S/ {producto['valor_comprado']:.2f}")
            y -= 15

        y -= 5
        pdf.setFont('Helvetica-Bold', 9)
        pdf.drawString(340, y, f"TOTAL: S/ {total_categoria:.2f}")
        y -= 30

    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(340, y, f"TOTAL GENERAL: S/ {total_general:.2f}")

    pdf.save()
    return response