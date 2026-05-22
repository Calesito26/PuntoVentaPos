from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect

from inventario.models import (
    ConfiguracionEmpresa
)

from inventario.forms import (
    ConfiguracionEmpresaForm
)

from usuarios.decorators import (
    administrador_required
)


@administrador_required
def configuracion_empresa(request):

    empresa = (
        ConfiguracionEmpresa
        .obtener_configuracion()
    )

    if request.method == 'POST':

        form = ConfiguracionEmpresaForm(
            request.POST,
            request.FILES,
            instance=empresa
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Configuración actualizada correctamente.'
            )

            return redirect(
                'inventario:configuracion_empresa'
            )

    else:

        form = ConfiguracionEmpresaForm(
            instance=empresa
        )

    return render(
        request,
        'inventario/configuracion_empresa.html',
        {
            'form': form,
            'empresa': empresa
        }
    )