from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

import openpyxl

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from compras.models import DevolucionCompra
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


def filtrar_devoluciones_compra(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    usuario_id = request.GET.get('usuario', '')
    buscar = request.GET.get('buscar', '').strip()

    devoluciones = DevolucionCompra.objects.select_related(
        'compra',
        'responsable',
        'proveedor'
    ).all()

    if fecha_inicio:
        devoluciones = devoluciones.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        devoluciones = devoluciones.filter(fecha__date__lte=fecha_fin)

    if usuario_id:
        devoluciones = devoluciones.filter(responsable_id=usuario_id)

    if buscar:
        devoluciones = devoluciones.filter(
            Q(codigo__icontains=buscar) |
            Q(compra__codigo__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar)
        )

    return devoluciones.order_by('-fecha')


@administrador_required
def devolucion_compra_list(request):
    User = get_user_model()

    devoluciones = filtrar_devoluciones_compra(request)
    usuarios = User.objects.filter(is_active=True).order_by('username')

    total_devoluciones = sum(dev.valor for dev in devoluciones)

    return render(
        request,
        'compras/devolucion_compra_list.html',
        {
            'devoluciones': devoluciones,
            'usuarios': usuarios,
            'fecha_inicio': request.GET.get('fecha_inicio', ''),
            'fecha_fin': request.GET.get('fecha_fin', ''),
            'usuario_id': request.GET.get('usuario', ''),
            'buscar': request.GET.get('buscar', ''),
            'total_devoluciones': total_devoluciones,
        }
    )


@administrador_required
def devolucion_compra_excel(request):
    devoluciones = filtrar_devoluciones_compra(request)

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Devoluciones compras'

    hoja.append([
        'Item',
        'Devolución',
        'Factura',
        'Fecha y hora',
        'Responsable',
        'Proveedor',
        'Valor',
        'Estado',
    ])

    total = 0

    for index, dev in enumerate(devoluciones, start=1):
        total += dev.valor

        hoja.append([
            index,
            dev.codigo,
            dev.compra.codigo,
            dev.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            dev.responsable.username if dev.responsable else '',
            dev.proveedor.razon_social if dev.proveedor else '',
            float(dev.valor),
            dev.estado,
        ])

    hoja.append([])
    hoja.append(['', '', '', '', '', 'TOTAL', float(total), ''])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=devoluciones_compras.xlsx'

    workbook.save(response)
    return response


@administrador_required
def devolucion_compra_pdf(request):
    devoluciones = filtrar_devoluciones_compra(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=devoluciones_compras.pdf'

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
        'Devoluciones Compras'
    )

    data = [[
        'Item',
        'Devolución',
        'Factura',
        'Fecha',
        'Proveedor',
        'Valor',
        'Estado',
    ]]

    total = 0

    for index, dev in enumerate(devoluciones, start=1):
        total += dev.valor

        data.append([
            str(index),
            dev.codigo,
            dev.compra.codigo,
            dev.fecha.strftime('%Y-%m-%d %H:%M'),
            dev.proveedor.razon_social if dev.proveedor else '-',
            f'S/ {dev.valor:.2f}',
            dev.estado,
        ])

    data.append(['', '', '', '', 'TOTAL', f'S/ {total:.2f}', ''])

    tabla = Table(
        data,
        colWidths=[30, 80, 80, 100, 120, 60, 55]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',      (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN',         (5, 1), (5, -1),  'RIGHT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response