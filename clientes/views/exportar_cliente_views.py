import openpyxl

from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from clientes.models import Cliente
from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


@administrador_required
def exportar_clientes_excel(request):
    clientes = Cliente.objects.all().order_by('nombre')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Clientes'

    hoja.append([
        'Item',
        'Nombre',
        'Tipo documento',
        'Número documento',
        'Teléfono',
        'Correo',
        'Dirección',
        'Municipio',
        'Estado',
    ])

    for index, cliente in enumerate(clientes, start=1):
        hoja.append([
            index,
            cliente.nombre,
            getattr(cliente, 'tipo_documento', ''),
            cliente.numero_documento,
            cliente.telefono or '',
            getattr(cliente, 'correo', '') or getattr(cliente, 'email', ''),
            cliente.direccion or '',
            getattr(cliente, 'municipio', ''),
            'Activo' if getattr(cliente, 'activo', True) else 'Inactivo',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'

    workbook.save(response)
    return response


@administrador_required
def exportar_clientes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=clientes.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    elementos = []

    # ✅ Cabecera dinámica con logo y datos de empresa
    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Lista de Clientes'
    )

    data = [[
        'Item',
        'Nombre',
        'Documento',
        'Teléfono',
        'Correo',
    ]]

    clientes = Cliente.objects.all().order_by('nombre')

    for index, cliente in enumerate(clientes, start=1):
        correo = getattr(cliente, 'correo', '') or getattr(cliente, 'email', '')

        data.append([
            str(index),
            str(cliente.nombre),
            str(cliente.numero_documento),
            str(cliente.telefono or '-'),
            str(correo or '-'),
        ])

    tabla = Table(
        data,
        colWidths=[35, 160, 100, 90, 130]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response