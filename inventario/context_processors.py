from inventario.models import ConfiguracionEmpresa


def empresa_config(request):
    return {
        'empresa_config': ConfiguracionEmpresa.obtener_configuracion()
    }