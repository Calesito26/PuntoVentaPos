from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.db.models import Q

from clientes.forms import ClienteForm
from clientes.models import Cliente
from usuarios.decorators import vendedor_required

from django.http import JsonResponse
from clientes.services.documento_service import DocumentoService
from django.http import JsonResponse

@vendedor_required
def buscar_documento(request):
    tipo_documento = request.GET.get('tipo_documento', '').upper()
    numero_documento = request.GET.get('numero_documento', '').strip()

    if not numero_documento:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Ingrese un número de documento.'
        })

    if tipo_documento == 'DNI':
        resultado = DocumentoService.buscar_dni(numero_documento)

    elif tipo_documento == 'RUC':
        resultado = DocumentoService.buscar_ruc(numero_documento)

    else:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Seleccione DNI o RUC.'
        })

    return JsonResponse(resultado)

@vendedor_required
def cliente_list(request):
    buscar = request.GET.get('buscar', '').strip()

    clientes = Cliente.objects.all().order_by('nombre')

    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) |
            Q(numero_documento__icontains=buscar) |
            Q(tipo_documento__icontains=buscar)
        )

    return render(
        request,
        'clientes/cliente_list.html',
        {
            'clientes': clientes,
            'buscar': buscar
        }
    )


@vendedor_required
def cliente_create(request):
    form = ClienteForm(
        request.POST or None
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            return redirect(
                'clientes:cliente_list'
            )

    return render(
        request,
        'clientes/cliente_form.html',
        {
            'form': form,
            'titulo': 'Registrar cliente'
        }
    )


@vendedor_required
def cliente_update(request, pk):
    cliente = get_object_or_404(
        Cliente,
        pk=pk
    )

    form = ClienteForm(
        request.POST or None,
        instance=cliente
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            return redirect(
                'clientes:cliente_list'
            )

    return render(
        request,
        'clientes/cliente_form.html',
        {
            'form': form,
            'titulo': 'Editar cliente'
        }
    )


def cliente_create_ajax(request):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'error': 'Método no permitido.'
        })

    tipo_documento = request.POST.get('tipo_documento', '').strip()
    numero_documento = request.POST.get('numero_documento', '').strip()
    nombre = request.POST.get('nombre', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    email = request.POST.get('email', '').strip()
    direccion = request.POST.get('direccion', '').strip()

    if not nombre:
        return JsonResponse({
            'ok': False,
            'error': 'Ingrese el nombre del cliente.'
        })

    if numero_documento:
        cliente_existente = Cliente.objects.filter(
            numero_documento=numero_documento
        ).first()

        if cliente_existente:
            return JsonResponse({
                'ok': True,
                'id': cliente_existente.id,
                'nombre': cliente_existente.nombre,
                'mensaje': 'El cliente ya existía y fue seleccionado.'
            })

    cliente = Cliente.objects.create(
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombre=nombre,
        telefono=telefono,
        email=email,
        direccion=direccion,
        activo=True
    )

    return JsonResponse({
        'ok': True,
        'id': cliente.id,
        'nombre': cliente.nombre,
        'mensaje': 'Cliente creado correctamente.'
    })