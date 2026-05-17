from decimal import Decimal
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from productos.models import Producto
from productos.models import Categoria
from ventas.models import Venta
from ventas.models import DetalleVenta
from django.contrib.auth.decorators import login_required
from usuarios.decorators import vendedor_required

@vendedor_required
def obtener_carrito(request):
    return request.session.get('carrito', {})

@vendedor_required
def guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


@vendedor_required
def pos_venta(request):
    carrito = obtener_carrito(request)
    productos_carrito = []
    total = Decimal('0.00')
    for producto_id, item in carrito.items():
        producto = get_object_or_404(
            Producto,
            id=producto_id
        )
        cantidad = item['cantidad']
        subtotal = (
            Decimal(str(cantidad))
            * producto.precio_venta
        )
        productos_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })
        total += subtotal
    categoria_id = request.GET.get('categoria')
    productos = Producto.objects.filter(
        activo=True
    ).select_related(
        'categoria'
    )
    if categoria_id:
        productos = productos.filter(
            categoria_id=categoria_id
        )
    productos = productos.order_by('nombre')
    categorias = Categoria.objects.filter(
        activo=True
    ).order_by('nombre')
    return render(
        request,
        'ventas/pos_venta.html',
        {
            'productos_carrito': productos_carrito,
            'total': total,
            'productos': productos,
            'categorias': categorias,
        }
    )

@vendedor_required
def agregar_producto_scanner(request):
    if request.method == 'POST':
        codigo = request.POST.get(
            'codigo',
            ''
        ).strip()
        if not codigo:
            messages.error(
                request,
                'Debes ingresar o escanear un código.'
            )
            return redirect('ventas:pos_venta')
        try:
            producto = Producto.objects.get(
                codigo=codigo,
                activo=True
            )
            if producto.stock <= 0:
                messages.error(
                    request,
                    'Producto sin stock disponible.'
                )
                return redirect('ventas:pos_venta')
            carrito = obtener_carrito(request)
            producto_id = str(producto.id)
            if producto_id in carrito:
                cantidad_actual = carrito[producto_id]['cantidad']
                nueva_cantidad = cantidad_actual + 1
                if nueva_cantidad > producto.stock:
                    messages.error(
                        request,
                        f'No hay más stock disponible para {producto.nombre}.'
                    )
                    return redirect('ventas:pos_venta')
                carrito[producto_id]['cantidad'] = nueva_cantidad
            else:
                carrito[producto_id] = {
                    'cantidad': 1
                }
            guardar_carrito(request, carrito)
            messages.success(
                request,
                f'{producto.nombre} agregado al carrito.'
            )
        except Producto.DoesNotExist:
            messages.error(
                request,
                f'No existe producto con código: {codigo}'
            )
    return redirect('ventas:pos_venta')

@vendedor_required
def quitar_producto_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto_id = str(producto_id)
    if producto_id in carrito:
        del carrito[producto_id]
        guardar_carrito(request, carrito)
        messages.success(
            request,
            'Producto quitado del carrito.'
        )
    return redirect('ventas:pos_venta')

@vendedor_required
def limpiar_carrito(request):
    guardar_carrito(request, {})
    messages.success(
        request,
        'Carrito limpiado correctamente.'
    )
    return redirect('ventas:pos_venta')

@vendedor_required
def confirmar_venta(request):
    carrito = obtener_carrito(request)
    if not carrito:
        messages.error(
            request,
            'No hay productos en el carrito.'
        )
        return redirect('ventas:pos_venta')
    total = Decimal('0.00')
    venta = Venta.objects.create(
        total=0
    )
    for producto_id, item in carrito.items():
        producto = get_object_or_404(
            Producto,
            id=producto_id
        )
        cantidad = item['cantidad']
        if cantidad > producto.stock:
            messages.error(
                request,
                f'Stock insuficiente para {producto.nombre}.'
            )
            venta.delete()
            return redirect('ventas:pos_venta')
        subtotal = producto.precio_venta * cantidad
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=subtotal
        )
        producto.stock -= cantidad
        producto.save()
        total += subtotal
    venta.total = total
    venta.save()
    guardar_carrito(request, {})
    messages.success(
        request,
        f'Venta #{venta.id} registrada correctamente.'
    )
    return redirect(
        'ventas:ticket_venta',
        venta_id=venta.id
    )

@vendedor_required
def ticket_venta(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.prefetch_related(
            'detalles__producto'
        ),
        id=venta_id
    )
    return render(
        request,
        'ventas/ticket_venta.html',
        {
            'venta': venta
        }
    )

@vendedor_required
def aumentar_cantidad(request, producto_id):
    carrito = obtener_carrito(request)
    producto_id_str = str(producto_id)
    producto = get_object_or_404(
        Producto,
        id=producto_id
    )
    if producto_id_str in carrito:
        cantidad_actual = carrito[producto_id_str]['cantidad']
        nueva_cantidad = cantidad_actual + 1
        if nueva_cantidad > producto.stock:
            messages.error(
                request,
                f'No hay más stock disponible para {producto.nombre}.'
            )
            return redirect('ventas:pos_venta')
        carrito[producto_id_str]['cantidad'] = nueva_cantidad
    guardar_carrito(request, carrito)
    return redirect('ventas:pos_venta')

@vendedor_required
def disminuir_cantidad(request, producto_id):
    carrito = obtener_carrito(request)
    producto_id_str = str(producto_id)
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] -= 1
        if carrito[producto_id_str]['cantidad'] <= 0:
            del carrito[producto_id_str]
    guardar_carrito(request, carrito)
    return redirect('ventas:pos_venta')