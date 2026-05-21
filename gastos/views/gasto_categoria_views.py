from collections import defaultdict

import openpyxl

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from gastos.models.gasto import Gasto
from gastos.models.categoria_gasto import CategoriaGasto


def gasto_categoria_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    categoria_id = request.GET.get('categoria', '')
    tipo_gasto = request.GET.get('tipo_gasto', '')
    usuario_id = request.GET.get('usuario', '')

    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    if fecha_inicio:
        gastos = gastos.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        gastos = gastos.filter(fecha__date__lte=fecha_fin)

    if categoria_id:
        gastos = gastos.filter(categoria_id=categoria_id)

    if tipo_gasto:
        gastos = gastos.filter(tipo_gasto=tipo_gasto)

    if usuario_id:
        gastos = gastos.filter(responsable_id=usuario_id)

    grupos_dict = defaultdict(list)

    for gasto in gastos:
        grupos_dict[gasto.categoria.nombre].append(gasto)

    grupos = []

    for categoria, lista_gastos in grupos_dict.items():
        total = sum(g.valor for g in lista_gastos)
        contado = sum( g.valor for g in lista_gastos if g.sacar_caja )
        credito = sum( g.valor for g in lista_gastos if not g.sacar_caja)
        grupos.append({
            'categoria': categoria,
            'gastos': lista_gastos,
            'total': total,
            'contado': contado,
            'credito': credito,
        })

    User = get_user_model()

    return render(
        request,
        'gastos/gasto_categoria_list.html',
        {
            'grupos': grupos,
            'categorias': CategoriaGasto.objects.all().order_by('nombre'),
            'usuarios': User.objects.filter(is_active=True).order_by('username'),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'categoria_id': categoria_id,
            'tipo_gasto': tipo_gasto,
            'usuario_id': usuario_id,
        }
    )


def gasto_categoria_excel(request):
    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Gastos por categoria'

    hoja.append([
        'Item',
        'Fecha y Hora',
        'Descripción',
        'Categoría',
        'Tipo',
        'Proveedor',
        'Responsable',
        'Método de pago',
        'Valor',
        'Abonado',
        'Saldo',
        'Egreso de caja',
        'Estado',
    ])

    for index, gasto in enumerate(gastos, start=1):
        hoja.append([
            index,
            gasto.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            gasto.descripcion,
            gasto.categoria.nombre,
            gasto.tipo_gasto,
            gasto.proveedor.razon_social if gasto.proveedor else '',
            gasto.responsable.username if gasto.responsable else '',
            gasto.metodo_pago,
            float(gasto.valor),
            float(gasto.valor) if gasto.tipo_gasto == 'CONTADO' else 0,
            0 if gasto.tipo_gasto == 'CONTADO' else float(gasto.valor),
            'SI' if gasto.sacar_caja else 'NO',
            gasto.estado,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=gastos_por_categoria.xlsx'

    workbook.save(response)
    return response


def gasto_categoria_pdf(request):
    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('categoria__nombre', '-fecha')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=gastos_por_categoria.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Gastos por Categoria')
    y -= 30

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Fecha')
    pdf.drawString(140, y, 'Descripcion')
    pdf.drawString(280, y, 'Categoria')
    pdf.drawString(370, y, 'Valor')
    pdf.drawString(430, y, 'Tipo')
    pdf.drawString(500, y, 'Estado')
    y -= 18

    pdf.setFont('Helvetica', 8)

    for index, gasto in enumerate(gastos, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, gasto.fecha.strftime('%Y-%m-%d'))
        pdf.drawString(140, y, gasto.descripcion[:25])
        pdf.drawString(280, y, gasto.categoria.nombre[:15])
        pdf.drawString(370, y, f'S/ {gasto.valor}')
        pdf.drawString(430, y, gasto.tipo_gasto)
        pdf.drawString(500, y, gasto.estado)

        y -= 18

    pdf.save()
    return response