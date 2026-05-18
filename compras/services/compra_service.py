from decimal import Decimal

from django.db import transaction

from compras.models import Compra
from compras.models import DetalleCompra
from inventario.models import StockBodega
from productos.models import Producto


class CompraService:

    @staticmethod
    @transaction.atomic
    def registrar_compra(data, usuario):
        estado = data.get('estado', 'RECIBIDA')

        compra = Compra.objects.create(
            proveedor_id=data.get('proveedor'),
            sede_id=data.get('sede'),
            tipo_comprobante=data.get('tipo_comprobante', 'FACTURA'),
            numero_comprobante=data.get('numero_comprobante') or '',
            observacion=data.get('observacion') or '',
            subtotal=Decimal(str(data.get('subtotal', 0))),
            impuesto=Decimal(str(data.get('impuesto', 0))),
            total=Decimal(str(data.get('total', 0))),
            responsable=usuario,
            estado=estado,
        )

        productos = data.get('productos', [])

        for item in productos:
            producto = Producto.objects.get(id=item['producto_id'])

            cantidad = Decimal(str(item.get('cantidad', 0)))
            precio_compra = Decimal(str(item.get('precio_compra', 0)))
            precio_venta = Decimal(str(item.get('precio_venta', producto.precio_venta)))

            DetalleCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=cantidad,
                precio_compra=precio_compra,
                subtotal=cantidad * precio_compra,
            )

            producto.precio_compra = precio_compra
            producto.precio_venta = precio_venta
            producto.save()

            if estado == 'RECIBIDA':
                stock_bodega, creado = StockBodega.objects.get_or_create(
                    sede_id=data.get('sede'),
                    producto=producto,
                    defaults={
                        'stock': Decimal('0.00'),
                        'stock_minimo': Decimal('5.00'),
                        'activo': True,
                    }
                )

                stock_bodega.stock += cantidad
                stock_bodega.save()

        return compra