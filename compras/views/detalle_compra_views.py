from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from compras.models import DetalleCompra, Proveedor
from inventario.models import Sede, ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required


@administrador_required
def detalle_compra_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    sede_id = request.GET.get('sede', '')
    proveedor_id = request.GET.get('proveedor', '')
    usuario_id = request.GET.get('usuario', '')
    buscar = request.GET.get('buscar', '').strip()

    sedes = Sede.objects.filter(activo=True).order_by('nombre')
    proveedores = Proveedor.objects.filter(activo=True).order_by('razon_social')
    User = get_user_model()
    usuarios = User.objects.filter(is_active=True).order_by('username')

    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'compra__sede',
        'compra__proveedor',
        'compra__responsable'
    ).all().order_by('-id')

    if fecha_inicio:
        detalles = detalles.filter(compra__fecha_compra__date__gte=fecha_inicio)

    if fecha_fin:
        detalles = detalles.filter(compra__fecha_compra__date__lte=fecha_fin)

    if sede_id:
        detalles = detalles.filter(compra__sede_id=sede_id)

    if proveedor_id:
        detalles = detalles.filter(compra__proveedor_id=proveedor_id)

    if usuario_id:
        detalles = detalles.filter(compra__responsable_id=usuario_id)

    if buscar:
        detalles = detalles.filter(
            Q(compra__codigo__icontains=buscar) |
            Q(producto__codigo__icontains=buscar) |
            Q(producto__nombre__icontains=buscar) |
            Q(compra__proveedor__razon_social__icontains=buscar)
        )

    total_compras = sum(detalle.subtotal for detalle in detalles)

    return render(
        request,
        'compras/detalle_compra_list.html',
        {
            'detalles': detalles,
            'sedes': sedes,
            'proveedores': proveedores,
            'usuarios': usuarios,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'sede_id': sede_id,
            'proveedor_id': proveedor_id,
            'usuario_id': usuario_id,
            'buscar': buscar,
            'total_compras': total_compras,
        }
    )


@login_required
def detalle_compra_excel(request):
    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'compra__proveedor',
        'compra__sede'
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Detalle Compras'

    ws.append([
        'Factura',
        'Bodega',
        'Fecha',
        'Proveedor',
        'Producto',
        'Precio Compra',
        'Devuelto',
        'Cantidad',
        'Total'
    ])

    for detalle in detalles:
        ws.append([
            detalle.compra.codigo,
            detalle.compra.sede.nombre,
            detalle.compra.fecha_compra.strftime('%Y-%m-%d %H:%M'),
            detalle.compra.proveedor.razon_social,
            detalle.producto.nombre,
            float(detalle.precio_compra),
            float(detalle.cantidad_devuelta),
            float(detalle.cantidad),
            float(detalle.subtotal)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=detalle_compras.xlsx'

    wb.save(response)
    return response


@administrador_required
@login_required
def detalle_compra_pdf(request):
    detalles = DetalleCompra.objects.select_related(
        'compra',
        'producto',
        'compra__proveedor',
        'compra__sede'
    ).all().order_by('-id')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=detalle_compras.pdf'

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
        'Detalle de Compras'
    )

    data = [[
        'Item',
        'Factura',
        'Producto',
        'Proveedor',
        'Cant.',
        'Devuelto',
        'Total',
    ]]

    total_general = 0

    for index, detalle in enumerate(detalles, start=1):
        total_general += detalle.subtotal

        data.append([
            str(index),
            detalle.compra.codigo,
            detalle.producto.nombre,
            detalle.compra.proveedor.razon_social,
            str(int(detalle.cantidad)),
            str(int(detalle.cantidad_devuelta)),
            f'S/ {detalle.subtotal:.2f}',
        ])

    data.append(['', '', '', 'TOTAL', '', '', f'S/ {total_general:.2f}'])

    tabla = Table(
        data,
        colWidths=[30, 80, 150, 130, 40, 55, 65]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0),  (-1, 0),  'Helvetica-Bold'),
        ('FONTNAME',      (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0),  (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0),  (-1, 0),  12),
        ('TOPPADDING',    (0, 1),  (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1),  (-1, -1), 8),
        ('ALIGN',         (0, 0),  (-1, -1), 'LEFT'),
        ('ALIGN',         (6, 1),  (6, -1),  'RIGHT'),
        ('TEXTCOLOR',     (0, 0),  (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response