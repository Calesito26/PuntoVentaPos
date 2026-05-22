import openpyxl

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from inventario.models import ConfiguracionEmpresa, Promocion
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


def obtener_promociones_exportar():
    return Promocion.objects.select_related(
        'responsable'
    ).all().order_by('-fecha_inicio')


@administrador_required
def exportar_promociones_excel(request):
    promociones = obtener_promociones_exportar()

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Promociones'

    hoja.append([
        'Item',
        'Nombre',
        'Fecha inicio',
        'Fecha fin',
        'Descuento',
        'Responsable',
        'Estado',
    ])

    for index, promocion in enumerate(promociones, start=1):
        hoja.append([
            index,
            promocion.nombre,
            promocion.fecha_inicio.strftime('%d/%m/%Y %H:%M'),
            promocion.fecha_fin.strftime('%d/%m/%Y %H:%M'),
            float(promocion.porcentaje_descuento),
            promocion.responsable.username if promocion.responsable else '',
            'Activo' if promocion.activo else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=promociones.xlsx'

    workbook.save(response)

    return response


@administrador_required
def exportar_promociones_pdf(request):
    promociones = obtener_promociones_exportar()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=promociones.pdf'

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
        'Historial de Promociones'
    )

    data = [[
        'Item',
        'Nombre',
        'Inicio',
        'Fin',
        'Desc.',
        'Responsable',
        'Estado',
    ]]

    for index, promocion in enumerate(promociones, start=1):
        data.append([
            str(index),
            promocion.nombre,
            promocion.fecha_inicio.strftime('%d/%m/%Y'),
            promocion.fecha_fin.strftime('%d/%m/%Y'),
            f'{promocion.porcentaje_descuento}%',
            promocion.responsable.username if promocion.responsable else '-',
            'Activo' if promocion.activo else 'Inactivo',
        ])

    tabla = Table(
        data,
        colWidths=[30, 150, 70, 70, 40, 90, 55]
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