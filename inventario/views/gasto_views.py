import json
import openpyxl

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from gastos.models.gasto import Gasto
from gastos.models.categoria_gasto import CategoriaGasto
from compras.models.proveedor import Proveedor
from clientes.services.documento_service import DocumentoService


def gasto_list(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    usuario_id = request.GET.get('usuario', '')
    metodo_pago = request.GET.get('metodo_pago', '')
    proveedor_id = request.GET.get('proveedor', '')
    buscar = request.GET.get('buscar', '').strip()

    gastos = Gasto.objects.select_related(
        'categoria',
        'proveedor',
        'responsable'
    ).all().order_by('-fecha')

    if fecha_inicio:
        gastos = gastos.filter(fecha__date__gte=fecha_inicio)

    if fecha_fin:
        gastos = gastos.filter(fecha__date__lte=fecha_fin)

    if usuario_id:
        gastos = gastos.filter(responsable_id=usuario_id)

    if metodo_pago:
        gastos = gastos.filter(metodo_pago=metodo_pago)

    if proveedor_id:
        gastos = gastos.filter(proveedor_id=proveedor_id)

    if buscar:
        gastos = gastos.filter(
            Q(descripcion__icontains=buscar) |
            Q(proveedor__razon_social__icontains=buscar) |
            Q(categoria__nombre__icontains=buscar)
        )

    User = get_user_model()

    return render(
        request,
        'gastos/gasto_list.html',
        {
            'gastos': gastos,
            'categorias': CategoriaGasto.objects.filter(activo=True).order_by('nombre'),
            'proveedores': Proveedor.objects.all().order_by('razon_social'),
            'usuarios': User.objects.filter(is_active=True).order_by('username'),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'usuario_id': usuario_id,
            'metodo_pago': metodo_pago,
            'proveedor_id': proveedor_id,
            'buscar': buscar,
            'total_gastos': sum(g.valor for g in gastos),
        }
    )


def crear_gasto_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'mensaje': 'Método no permitido.'})

    data = json.loads(request.body)

    descripcion = data.get('descripcion', '').strip()
    valor = data.get('valor')
    categoria_id = data.get('categoria')
    proveedor_id = data.get('proveedor') or None
    metodo_pago = data.get('metodo_pago') or 'EFECTIVO'
    sacar_caja = data.get('sacar_caja', False)

    if not descripcion:
        return JsonResponse({'ok': False, 'mensaje': 'La descripción es obligatoria.'})

    if not valor or float(valor) <= 0:
        return JsonResponse({'ok': False, 'mensaje': 'El valor es obligatorio.'})

    if not categoria_id:
        return JsonResponse({'ok': False, 'mensaje': 'Seleccione una categoría.'})

    gasto = Gasto.objects.create(
        descripcion=descripcion,
        categoria_id=categoria_id,
        proveedor_id=proveedor_id,
        responsable=request.user,
        metodo_pago=metodo_pago,
        valor=valor,
        sacar_caja=sacar_caja,
        estado='PROCESADO'
    )

    return JsonResponse({
        'ok': True,
        'mensaje': 'Gasto registrado correctamente.',
        'id': gasto.id
    })


def eliminar_gasto_ajax(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)
    gasto.delete()

    return JsonResponse({
        'ok': True,
        'mensaje': 'Gasto eliminado correctamente.'
    })


def consultar_documento_proveedor_gasto_ajax(request):
    tipo = request.GET.get('tipo', '').upper()
    numero = request.GET.get('numero', '').strip()

    if tipo == 'DNI':
        resultado = DocumentoService.buscar_dni(numero)
    elif tipo == 'RUC':
        resultado = DocumentoService.buscar_ruc(numero)
    else:
        return JsonResponse({'ok': False, 'mensaje': 'Tipo de documento inválido.'})

    if not resultado.get('ok'):
        return JsonResponse(resultado)

    return JsonResponse({
        'ok': True,
        'nombre': resultado.get('nombre', ''),
        'direccion': resultado.get('direccion', '')
    })


def crear_proveedor_gasto_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'mensaje': 'Método no permitido.'})

    data = json.loads(request.body)

    numero_documento = data.get('numero_documento', '').strip()
    razon_social = data.get('razon_social', '').strip()
    tipo_documento = data.get('tipo_documento', 'RUC')

    if not numero_documento:
        return JsonResponse({'ok': False, 'mensaje': 'Ingrese documento.'})

    if not razon_social:
        return JsonResponse({'ok': False, 'mensaje': 'Ingrese nombre del proveedor.'})

    proveedor = Proveedor.objects.filter(numero_documento=numero_documento).first()

    if not proveedor:
        proveedor = Proveedor.objects.create(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            razon_social=razon_social,
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            correo=data.get('correo', '')
        )

    return JsonResponse({
        'ok': True,
        'id': proveedor.id,
        'nombre': proveedor.razon_social,
        'mensaje': 'Proveedor registrado correctamente.'
    })


def gasto_excel(request):
    gastos = Gasto.objects.select_related('categoria', 'proveedor', 'responsable').all().order_by('-fecha')

    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = 'Historial Gastos'

    hoja.append([
        'Item', 'Fecha y hora', 'Descripción', 'Categoría',
        'Proveedor', 'Responsable', 'Método pago',
        'Valor', 'Egreso caja', 'Estado'
    ])

    for index, gasto in enumerate(gastos, start=1):
        hoja.append([
            index,
            gasto.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            gasto.descripcion,
            gasto.categoria.nombre,
            gasto.proveedor.razon_social if gasto.proveedor else '',
            gasto.responsable.username if gasto.responsable else '',
            gasto.metodo_pago,
            float(gasto.valor),
            'SI' if gasto.sacar_caja else 'NO',
            gasto.estado,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=historial_gastos.xlsx'

    workbook.save(response)
    return response


def gasto_pdf(request):
    gastos = Gasto.objects.select_related('categoria', 'proveedor', 'responsable').all().order_by('-fecha')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=historial_gastos.pdf'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(40, y, 'Historial de Gastos')
    y -= 35

    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawString(40, y, 'Item')
    pdf.drawString(70, y, 'Fecha')
    pdf.drawString(160, y, 'Descripcion')
    pdf.drawString(300, y, 'Categoria')
    pdf.drawString(390, y, 'Valor')
    pdf.drawString(460, y, 'Caja')
    pdf.drawString(510, y, 'Estado')
    y -= 18

    pdf.setFont('Helvetica', 8)

    for index, gasto in enumerate(gastos, start=1):
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont('Helvetica', 8)

        pdf.drawString(40, y, str(index))
        pdf.drawString(70, y, gasto.fecha.strftime('%Y-%m-%d'))
        pdf.drawString(160, y, gasto.descripcion[:25])
        pdf.drawString(300, y, gasto.categoria.nombre[:15])
        pdf.drawString(390, y, f'S/ {gasto.valor:.2f}')
        pdf.drawString(460, y, 'SI' if gasto.sacar_caja else 'NO')
        pdf.drawString(510, y, gasto.estado)

        y -= 18

    pdf.save()
    return response