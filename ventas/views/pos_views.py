from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from clientes.models import Cliente
from productos.models import Producto, Categoria
from ventas.models import Venta, DetalleVenta
from inventario.models import StockBodega, Sede
from usuarios.decorators import vendedor_required
from usuarios.models import UsuarioSede


def money(valor):
    return Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@vendedor_required
def obtener_carrito(request):
    return request.session.get('carrito', {})


@vendedor_required
def guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


def usuario_es_admin_o_super(usuario):
    return usuario.is_superuser or usuario.groups.filter(name='Administrador').exists()


def obtener_sede_pos(request):
    usuario = request.user

    if usuario_es_admin_o_super(usuario):
        sede_id = request.session.get('sede_pos_id')
        if sede_id:
            return Sede.objects.filter(id=sede_id, activo=True).first()
        return None

    usuario_sede = UsuarioSede.objects.filter(
        usuario=usuario
    ).select_related('sede').first()

    return usuario_sede.sede if usuario_sede else None


@vendedor_required
def seleccionar_sede_pos(request):
    if not usuario_es_admin_o_super(request.user):
        return redirect('ventas:pos_venta')

    sedes = Sede.objects.filter(activo=True).order_by('nombre')

    if request.method == 'POST':
        sede_id = request.POST.get('sede_id')

        if not sede_id:
            messages.error(request, 'Seleccione una sede.')
            return redirect('ventas:seleccionar_sede_pos')

        request.session['sede_pos_id'] = sede_id
        request.session.modified = True

        return redirect('ventas:pos_venta')

    return render(
        request,
        'ventas/seleccionar_sede_pos.html',
        {
            'sedes': sedes
        }
    )


def validar_stock_carrito(carrito, sede):
    if not sede:
        return False, 'No hay sede seleccionada para vender.'

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(item['cantidad'])

        if cantidad <= 0:
            return False, f'Cantidad inválida para {producto.nombre}.'

        stock_bodega = StockBodega.objects.filter(
            producto=producto,
            sede=sede,
            activo=True
        ).first()

        if not stock_bodega:
            return False, f'{producto.nombre} no tiene stock en la sede {sede.nombre}.'

        if cantidad > stock_bodega.stock:
            return False, (
                f'Stock insuficiente para {producto.nombre}. '
                f'Stock disponible en {sede.nombre}: {stock_bodega.stock}.'
            )

    return True, ''


def calcular_subtotal_carrito(carrito):
    subtotal = Decimal('0.00')

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = Decimal(str(item['cantidad']))
        subtotal += producto.precio_venta * cantidad

    return money(subtotal)


def calcular_totales_venta(request, subtotal):
    cortesia = request.POST.get('cortesia') == 'on'
    envio_domicilio = request.POST.get('envio_domicilio') == 'on'

    descuento_porcentaje = money(request.POST.get('descuento_porcentaje') or 0)
    costo_envio = money(request.POST.get('costo_envio') or 0) if envio_domicilio else Decimal('0.00')

    if descuento_porcentaje < 0:
        descuento_porcentaje = Decimal('0.00')

    if descuento_porcentaje > 100:
        descuento_porcentaje = Decimal('100.00')

    if cortesia:
        descuento = subtotal
        impuesto = Decimal('0.00')
        total = Decimal('0.00')
        costo_envio = Decimal('0.00')
    else:
        descuento = money(subtotal * descuento_porcentaje / Decimal('100'))
        base = subtotal - descuento
        impuesto = money(base * Decimal('0.18'))
        total = money(base + impuesto + costo_envio)

    return {
        'cortesia': cortesia,
        'envio_domicilio': envio_domicilio,
        'descuento': descuento,
        'impuesto': impuesto,
        'costo_envio': costo_envio,
        'total': total,
    }


@vendedor_required
def pos_venta(request):
    sede_actual = obtener_sede_pos(request)

    if not sede_actual:
        if usuario_es_admin_o_super(request.user):
            return redirect('ventas:seleccionar_sede_pos')

        messages.error(request, 'Tu usuario vendedor no tiene una sede asignada.')
        return redirect('home')

    carrito = obtener_carrito(request)

    productos_carrito = []
    total = Decimal('0.00')

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(item['cantidad'])

        stock_bodega = StockBodega.objects.filter(
            producto=producto,
            sede=sede_actual,
            activo=True
        ).first()

        producto.stock_pos = stock_bodega.stock if stock_bodega else 0
        subtotal = money(Decimal(str(cantidad)) * producto.precio_venta)

        productos_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

        total += subtotal

    categoria_id = request.GET.get('categoria')

    stocks = StockBodega.objects.select_related(
        'producto',
        'producto__categoria',
        'sede'
    ).filter(
        sede=sede_actual,
        activo=True,
        producto__activo=True,
        stock__gt=0
    )

    if categoria_id:
        stocks = stocks.filter(producto__categoria_id=categoria_id)

    productos = []

    for stock in stocks.order_by('producto__nombre'):
        producto = stock.producto
        producto.stock_pos = stock.stock
        productos.append(producto)

    categorias = Categoria.objects.filter(activo=True).order_by('nombre')

    ventas_espera = Venta.objects.filter(
        estado='ESPERA'
    ).prefetch_related(
        'detalles__producto'
    ).order_by('id')

    clientes = Cliente.objects.filter(
        activo=True
    ).order_by('nombre')

    return render(
        request,
        'ventas/pos_venta.html',
        {
            'productos_carrito': productos_carrito,
            'total': money(total),
            'productos': productos,
            'categorias': categorias,
            'ventas_espera': ventas_espera,
            'sede_actual': sede_actual,
            'es_admin_o_super': usuario_es_admin_o_super(request.user),
            'clientes': clientes,
        }
    )


@vendedor_required
def agregar_producto_scanner(request):
    sede_actual = obtener_sede_pos(request)

    if not sede_actual:
        messages.error(request, 'Seleccione una sede para vender.')
        return redirect('ventas:pos_venta')

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        if not codigo:
            messages.error(request, 'Debes ingresar o escanear un código.')
            return redirect('ventas:pos_venta')

        producto = Producto.objects.filter(
            codigo=codigo,
            activo=True
        ).first()

        if not producto:
            messages.error(request, f'No existe producto con código: {codigo}')
            return redirect('ventas:pos_venta')

        stock_bodega = StockBodega.objects.filter(
            producto=producto,
            sede=sede_actual,
            activo=True
        ).first()

        if not stock_bodega or stock_bodega.stock <= 0:
            messages.error(request, f'{producto.nombre} no tiene stock disponible en {sede_actual.nombre}.')
            return redirect('ventas:pos_venta')

        carrito = obtener_carrito(request)
        producto_id = str(producto.id)

        if producto_id in carrito:
            nueva_cantidad = int(carrito[producto_id]['cantidad']) + 1

            if nueva_cantidad > stock_bodega.stock:
                messages.error(
                    request,
                    f'No hay más stock disponible para {producto.nombre}. '
                    f'Stock en {sede_actual.nombre}: {stock_bodega.stock}.'
                )
                return redirect('ventas:pos_venta')

            carrito[producto_id]['cantidad'] = nueva_cantidad
        else:
            carrito[producto_id] = {'cantidad': 1}

        guardar_carrito(request, carrito)

    return redirect('ventas:pos_venta')


@vendedor_required
@transaction.atomic
def guardar_venta_espera(request):
    sede_actual = obtener_sede_pos(request)
    carrito = obtener_carrito(request)

    if not carrito:
        messages.error(request, 'No hay productos para guardar en espera.')
        return redirect('ventas:pos_venta')

    stock_ok, mensaje = validar_stock_carrito(carrito, sede_actual)

    if not stock_ok:
        messages.error(request, mensaje)
        return redirect('ventas:pos_venta')

    subtotal_venta = calcular_subtotal_carrito(carrito)

    venta = Venta.objects.create(
        sede=sede_actual,
        subtotal=subtotal_venta,
        descuento=Decimal('0.00'),
        impuesto=Decimal('0.00'),
        total=subtotal_venta,
        estado='ESPERA',
        metodo_pago='EFECTIVO',
        monto_recibido=Decimal('0.00'),
        cambio=Decimal('0.00')
    )

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(item['cantidad'])
        subtotal = money(producto.precio_venta * cantidad)

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=subtotal
        )

    guardar_carrito(request, {})

    messages.success(request, f'Venta #{venta.id} guardada en espera.')
    return redirect('ventas:pos_venta')


@vendedor_required
def cargar_venta_espera(request, venta_id):
    sede_actual = obtener_sede_pos(request)

    venta = get_object_or_404(
        Venta.objects.prefetch_related('detalles__producto'),
        id=venta_id,
        estado='ESPERA'
    )

    carrito = {}

    for detalle in venta.detalles.all():
        stock_bodega = StockBodega.objects.filter(
            producto=detalle.producto,
            sede=sede_actual,
            activo=True
        ).first()

        if not stock_bodega:
            messages.error(request, f'{detalle.producto.nombre} no tiene stock en {sede_actual.nombre}.')
            return redirect('ventas:pos_venta')

        if detalle.cantidad > stock_bodega.stock:
            messages.error(request, f'Stock insuficiente para {detalle.producto.nombre}.')
            return redirect('ventas:pos_venta')

        carrito[str(detalle.producto.id)] = {
            'cantidad': int(detalle.cantidad)
        }

    guardar_carrito(request, carrito)

    request.session['venta_espera_id'] = venta.id
    request.session.modified = True

    messages.success(request, f'Venta #{venta.id} cargada correctamente.')
    return redirect('ventas:pos_venta')


@vendedor_required
def eliminar_venta_espera(request, venta_id):
    venta = get_object_or_404(
        Venta,
        id=venta_id,
        estado='ESPERA'
    )

    venta.delete()

    if request.session.get('venta_espera_id') == venta_id:
        request.session.pop('venta_espera_id', None)
        guardar_carrito(request, {})

    messages.success(request, 'Venta en espera eliminada.')
    return redirect('ventas:pos_venta')


@vendedor_required
@transaction.atomic
def confirmar_venta(request):
    sede_actual = obtener_sede_pos(request)
    carrito = obtener_carrito(request)

    if not carrito:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:pos_venta')

    stock_ok, mensaje = validar_stock_carrito(carrito, sede_actual)

    if not stock_ok:
        messages.error(request, mensaje)
        return redirect('ventas:pos_venta')

    subtotal_venta = calcular_subtotal_carrito(carrito)
    totales = calcular_totales_venta(request, subtotal_venta)

    metodo_pago = request.POST.get('metodo_pago', 'EFECTIVO')
    monto_recibido = money(request.POST.get('monto_recibido') or 0)

    cliente_id = request.POST.get('cliente_id') or None

    if totales['cortesia']:
        monto_recibido = Decimal('0.00')
        cambio = Decimal('0.00')
    elif metodo_pago == 'EFECTIVO':
        if monto_recibido < totales['total']:
            messages.error(request, 'El monto recibido no puede ser menor al total.')
            return redirect('ventas:pos_venta')

        cambio = money(monto_recibido - totales['total'])
    else:
        monto_recibido = totales['total']
        cambio = Decimal('0.00')

    venta_espera_id = request.session.get('venta_espera_id')

    if venta_espera_id:
        venta = get_object_or_404(
            Venta,
            id=venta_espera_id,
            estado='ESPERA'
        )
        venta.detalles.all().delete()
    else:
        venta = Venta.objects.create(
            sede=sede_actual,
            total=Decimal('0.00'),
            estado='PAGADA'
        )

    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(item['cantidad'])

        stock_bodega = get_object_or_404(
            StockBodega,
            producto=producto,
            sede=sede_actual,
            activo=True
        )

        subtotal = money(producto.precio_venta * cantidad)

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            subtotal=subtotal
        )

        stock_bodega.stock -= cantidad
        stock_bodega.save()

    venta.cliente_id = cliente_id
    venta.sede = sede_actual
    venta.subtotal = subtotal_venta
    venta.descuento = totales['descuento']
    venta.impuesto = totales['impuesto']
    venta.total = totales['total']
    venta.metodo_pago = metodo_pago
    venta.monto_recibido = monto_recibido
    venta.cambio = cambio
    venta.cortesia = totales['cortesia']
    venta.envio_domicilio = totales['envio_domicilio']
    venta.origen_envio = request.POST.get('origen_envio') or ''
    venta.destino_envio = request.POST.get('destino_envio') or ''
    venta.costo_envio = totales['costo_envio']
    venta.estado = 'PAGADA'
    venta.save()

    guardar_carrito(request, {})

    request.session.pop('venta_espera_id', None)
    request.session.modified = True

    messages.success(request, f'Venta #{venta.id} registrada correctamente.')

    return redirect(
        'ventas:resumen_venta',
        venta_id=venta.id
    )

@vendedor_required
def quitar_producto_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto_id = str(producto_id)

    if producto_id in carrito:
        del carrito[producto_id]
        guardar_carrito(request, carrito)

    return redirect('ventas:pos_venta')


@vendedor_required
def limpiar_carrito(request):
    guardar_carrito(request, {})

    request.session.pop('venta_espera_id', None)
    request.session.modified = True

    messages.success(request, 'Carrito limpiado correctamente.')
    return redirect('ventas:pos_venta')


@vendedor_required
def aumentar_cantidad(request, producto_id):
    sede_actual = obtener_sede_pos(request)
    carrito = obtener_carrito(request)
    producto_id_str = str(producto_id)

    producto = get_object_or_404(Producto, id=producto_id)

    stock_bodega = StockBodega.objects.filter(
        producto=producto,
        sede=sede_actual,
        activo=True
    ).first()

    if not stock_bodega:
        messages.error(request, f'{producto.nombre} no tiene stock en esta sede.')
        return redirect('ventas:pos_venta')

    if producto_id_str in carrito:
        nueva_cantidad = int(carrito[producto_id_str]['cantidad']) + 1

        if nueva_cantidad > stock_bodega.stock:
            messages.error(
                request,
                f'No hay más stock disponible para {producto.nombre}. '
                f'Stock en {sede_actual.nombre}: {stock_bodega.stock}.'
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
        carrito[producto_id_str]['cantidad'] = int(
            carrito[producto_id_str]['cantidad']
        ) - 1

        if carrito[producto_id_str]['cantidad'] <= 0:
            del carrito[producto_id_str]

    guardar_carrito(request, carrito)
    return redirect('ventas:pos_venta')


@vendedor_required
def ticket_venta(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.select_related(
            'cliente',
            'sede'
        ).prefetch_related(
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
def resumen_venta(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.prefetch_related('detalles__producto'),
        id=venta_id
    )

    return render(
        request,
        'ventas/resumen_venta.html',
        {
            'venta': venta
        }
    )

@vendedor_required
def imprimir_ticket(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.select_related(
            'cliente',
            'sede'
        ).prefetch_related(
            'detalles__producto'
        ),
        id=venta_id
    )

    return render(
        request,
        'ventas/imprimir_ticket.html',
        {
            'venta': venta
        }
    )


@vendedor_required
def imprimir_carta(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.select_related(
            'cliente',
            'sede'
        ).prefetch_related(
            'detalles__producto'
        ),
        id=venta_id
    )

    return render(
        request,
        'ventas/imprimir_carta.html',
        {
            'venta': venta
        }
    )


@vendedor_required
def enviar_factura_correo(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.select_related(
            'cliente',
            'sede'
        ).prefetch_related(
            'detalles__producto'
        ),
        id=venta_id
    )

    return render(
        request,
        'ventas/enviar_factura_correo.html',
        {
            'venta': venta
        }
    )