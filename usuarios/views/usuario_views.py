from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from inventario.models import ConfiguracionEmpresa
from core.services.pdf_empresa_service import agregar_cabecera_empresa
from usuarios.decorators import administrador_required
from usuarios.forms import UsuarioSistemaForm


@administrador_required
def usuario_list(request):
    usuarios = User.objects.all().order_by('username')

    return render(
        request,
        'usuarios/usuario_list.html',
        {
            'usuarios': usuarios
        }
    )


@administrador_required
def usuario_create(request):
    form = UsuarioSistemaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Usuario registrado correctamente.'
            )

            return redirect('usuarios:usuario_list')

    return render(
        request,
        'usuarios/usuario_form.html',
        {
            'form': form,
            'titulo': 'Registrar usuario del sistema',
            'editar': False
        }
    )


@administrador_required
def usuario_update(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)

    form = UsuarioSistemaForm(
        request.POST or None,
        instance=usuario
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Usuario actualizado correctamente.'
            )

            return redirect('usuarios:usuario_list')

    return render(
        request,
        'usuarios/usuario_form.html',
        {
            'form': form,
            'titulo': 'Editar usuario del sistema',
            'editar': True
        }
    )


@administrador_required
def usuario_delete(request, usuario_id):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    usuario = get_object_or_404(User, id=usuario_id)

    if usuario == request.user:
        return JsonResponse({
            'ok': False,
            'mensaje': 'No puedes eliminar tu propio usuario.'
        })

    usuario.delete()

    return JsonResponse({
        'ok': True,
        'mensaje': 'Usuario eliminado correctamente.'
    })


@administrador_required
def exportar_usuarios_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Usuarios'

    ws.append([
        'Item',
        'Usuario',
        'Nombre',
        'Correo',
        'Rol',
        'Estado'
    ])

    usuarios = User.objects.all().order_by('username')

    for index, usuario in enumerate(usuarios, start=1):
        if usuario.is_superuser:
            rol = 'Superusuario'
        else:
            grupos = usuario.groups.all()
            rol = ', '.join([g.name for g in grupos]) if grupos else 'Sin rol'

        estado = 'Activo' if usuario.is_active else 'Inactivo'

        ws.append([
            index,
            usuario.username,
            f'{usuario.first_name} {usuario.last_name}',
            usuario.email,
            rol,
            estado
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=usuarios.xlsx'

    wb.save(response)
    return response


@administrador_required
def exportar_usuarios_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=usuarios.pdf'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    elementos = []

    # Cabecera dinámica con logo y datos de empresa
    empresa = ConfiguracionEmpresa.obtener_configuracion()

    agregar_cabecera_empresa(
        elementos,
        empresa,
        'Lista de Usuarios'
    )

    data = [[
        'Item',
        'Usuario',
        'Nombre',
        'Correo',
        'Rol',
        'Estado'
    ]]

    usuarios = User.objects.all().order_by('username')

    for index, usuario in enumerate(usuarios, start=1):
        if usuario.is_superuser:
            rol = 'Superusuario'
        else:
            grupos = usuario.groups.all()
            rol = ', '.join([g.name for g in grupos]) if grupos else 'Sin rol'

        estado = 'Activo' if usuario.is_active else 'Inactivo'

        data.append([
            str(index),
            usuario.username,
            f'{usuario.first_name} {usuario.last_name}',
            usuario.email or '-',
            rol,
            estado
        ])

    tabla = Table(
        data,
        colWidths=[40, 80, 140, 130, 90, 60]
    )

    tabla.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  12),
        ('TOPPADDING',    (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response