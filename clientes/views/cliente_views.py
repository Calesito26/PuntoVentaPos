from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from clientes.forms import ClienteForm
from clientes.models import Cliente
from usuarios.decorators import vendedor_required

from django.http import JsonResponse
from clientes.services.documento_service import DocumentoService

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
    clientes = Cliente.objects.all().order_by(
        'nombre'
    )

    return render(
        request,
        'clientes/cliente_list.html',
        {
            'clientes': clientes
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