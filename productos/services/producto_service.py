from productos.models import Producto


class ProductoService:

    @staticmethod
    def generar_codigo_producto():
        ultimo_producto = Producto.objects.order_by('-id').first()

        if not ultimo_producto:
            return 'PROD-000001'

        nuevo_numero = ultimo_producto.id + 1

        return f'PROD-{nuevo_numero:06d}'