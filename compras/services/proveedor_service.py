from compras.models import Proveedor


class ProveedorService:

    @staticmethod
    def crear_proveedor(data):
        proveedor = Proveedor.objects.create(
            tipo_documento=data.get('tipo_documento', 'RUC'),
            numero_documento=data.get('numero_documento'),
            razon_social=data.get('razon_social'),
            telefono=data.get('telefono') or '',
            email=data.get('email') or '',
            direccion=data.get('direccion') or '',
            activo=True
        )

        return proveedor