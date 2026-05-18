import json

from django.http import JsonResponse

from compras.models import Proveedor
from compras.services.proveedor_service import ProveedorService
from compras.services.documento_proveedor_service import DocumentoProveedorService
from usuarios.decorators import administrador_required


@administrador_required
def consultar_documento_proveedor_ajax(request):
    tipo = request.GET.get('tipo', '').upper()
    numero = request.GET.get('numero', '').strip()

    if not tipo or not numero:
        return JsonResponse({
            'ok': False,
            'mensaje': 'Ingrese tipo y número de documento.'
        })

    if tipo == 'DNI':
        resultado = DocumentoProveedorService.buscar_dni(numero)
    elif tipo == 'RUC':
        resultado = DocumentoProveedorService.buscar_ruc(numero)
    else:
        resultado = {
            'ok': False,
            'mensaje': 'Tipo de documento no válido.'
        }

    return JsonResponse(resultado)


@administrador_required
def crear_proveedor_ajax(request):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'mensaje': 'Método no permitido.'
        })

    data = json.loads(request.body)

    if not data.get('numero_documento'):
        return JsonResponse({
            'ok': False,
            'mensaje': 'Ingrese el documento del proveedor.'
        })

    if not data.get('razon_social'):
        return JsonResponse({
            'ok': False,
            'mensaje': 'Ingrese el nombre del proveedor.'
        })

    existe = Proveedor.objects.filter(
        numero_documento=data.get('numero_documento')
    ).first()

    if existe:
        return JsonResponse({
            'ok': True,
            'mensaje': 'El proveedor ya existe. Se seleccionó automáticamente.',
            'id': existe.id,
            'nombre': existe.razon_social
        })

    proveedor = ProveedorService.crear_proveedor(data)

    return JsonResponse({
        'ok': True,
        'mensaje': 'Proveedor creado correctamente.',
        'id': proveedor.id,
        'nombre': proveedor.razon_social
    })