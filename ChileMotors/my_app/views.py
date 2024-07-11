from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, DatosPersonalesForm, ContactoForm
from .models import Pedido, Producto, ProductoCarrito, CarruselItem, Servicios, Categoria, DatosPersonales, Pedido, PedidoProducto
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import logout

from django.core.mail import send_mail
from django.core.mail import EmailMessage
from ChileMotors.settings import EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
import json
import uuid
from .forms import CheckoutForm
from django.urls import reverse

def index(request):
    carrusel_items = CarruselItem.objects.filter(activo=True) # Obtiene el Carrusel
    servicios_items = Servicios.objects.filter(activo=True) #Obtiene los Servicios
    productos = Producto.objects.order_by('-id')[:4]  # Obtiene los últimos 4 productos
    context = {
        'carrusel_items': carrusel_items,
        'servicios': servicios_items,
        'productos': productos,
    }
    return render(request, 'my_app/index.html', context)

def nosotros(request):
    return render(request, 'my_app/nosotros.html')

def servicios(request):
    servicios_items = Servicios.objects.filter(activo=True) #Obtiene los Servicios
    context = {
        'servicios': servicios_items,
    }
    return render(request, 'my_app/servicios.html', context)

def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            datos_personales = form.save(commit=False)
            datos_personales.fecha_envio = timezone.now()
            datos_personales.save()
            
            # Enviar correo electrónico
            subject = "Recibimos tu solicitud de contacto! ChileMotors"
            message = (
                f"Estimado {datos_personales.nombre},\n\n"
                "Recibimos tu solicitud de contacto. Quédate atento que un agente te escribirá en breve.\n\n"
                f"Detalle: {datos_personales.detalle}\n\n"
                "Saludos,\nChileMotors"
            )
            recipient = datos_personales.email

            send_mail(subject, message, EMAIL_HOST_USER, [recipient])

            return redirect('contacto_exito', nombre=datos_personales.nombre)
    else:
        form = ContactoForm()
    
    return render(request, 'my_app/contacto.html', {'form': form})


def contacto_exito(request, nombre):
    return render(request, 'my_app/contacto_exito.html', {'nombre': nombre})

def productos(request):
    categoria_id = request.GET.get('categoria_id')
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
    else:
        productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'my_app/productos.html', {'productos': productos, 'categorias': categorias})

def producto_detalle_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    imagenes = [imagen.imagen.url for imagen in producto.imagenes.all()]
    data = {
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'preciocondescuento': producto.preciocondescuento,
        'cantidad': producto.cantidad,
        'sku': producto.sku,
        'imagen': producto.imagen.url,
        'imagenes': imagenes,
        'categoria': producto.categoria.nombre if producto.categoria else ''
    }
    return JsonResponse(data)

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_exitoso')
    else:
        form = CustomUserCreationForm()
    return render(request, 'my_app/registro.html', {'form': form})

def registro_exitoso(request):
    return render(request, 'my_app/registro_exitoso.html')

def mis_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

def carrito(request):
    carrito_items = ProductoCarrito.objects.all()
    total = sum(item.precio_total() for item in carrito_items)
    return render(request, 'my_app/carrito.html', {'carrito_items': carrito_items, 'total': total})

def logout_view(request):
    logout(request)
    return render(request, 'my_app/logout.html', {'mensaje': '¡Vuelve pronto!'})

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            cantidad = int(data.get('cantidad', 1))
            producto = get_object_or_404(Producto, id=producto_id)
            
            # Obtener o crear ProductoCarrito
            producto_carrito, created = ProductoCarrito.objects.get_or_create(
                producto=producto,
                user=request.user,
                defaults={'cantidad': cantidad}
            )

            if not created:
                producto_carrito.cantidad += cantidad
                producto_carrito.save()
            
            return JsonResponse({'status': 'success', 'message': 'Producto añadido al carrito.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@login_required
def eliminar_del_carrito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('producto_id')
            producto = get_object_or_404(Producto, id=producto_id)
            producto_carrito = get_object_or_404(ProductoCarrito, producto=producto, user=request.user)
            producto_carrito.delete()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado del carrito.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

@login_required
def ver_carrito(request):
    productos_carrito = ProductoCarrito.objects.filter(user=request.user)
    productos_data = []
    for item in productos_carrito:
        productos_data.append({
            'producto': {
                'id': item.producto.id,
                'nombre': item.producto.nombre,
                'precio': item.producto.precio,
                'preciocondescuento': item.producto.preciocondescuento,
                'imagen_url': item.producto.imagen.url
            },
            'cantidad': item.cantidad,
            'precio_total': item.precio_total()
        })
    return JsonResponse({'productos_carrito': productos_data})


@login_required
def checkout(request):
    user = request.user
    try:
        datos_personales = DatosPersonales.objects.get(user=user)
    except DatosPersonales.DoesNotExist:
        datos_personales = None

    productos_carrito = ProductoCarrito.objects.filter(user=user)
    total = sum(item.precio_total() for item in productos_carrito)

    if request.method == 'POST':
        form = CheckoutForm(request.POST, instance=datos_personales)
        if form.is_valid():
            datos_personales = form.save(commit=False)
            datos_personales.user = user
            datos_personales.save()

            metodo_pago = form.cleaned_data['metodo_pago']

            pedido = Pedido.objects.create(
                user=user,
                numero_pedido=str(uuid.uuid4()),
                total=total,
                metodo_pago=metodo_pago
            )

            pedido_productos = []
            for item in productos_carrito:
                pedido_producto = PedidoProducto.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio=item.producto.preciocondescuento if item.producto.preciocondescuento else item.producto.precio
                )
                pedido_productos.append(pedido_producto)

            # Vaciar el carrito después de realizar el pedido
            productos_carrito.delete()

            # Construir detalles del pedido para el correo electrónico
            productos_detalle = ""
            for pp in pedido_productos:
                precio = pp.precio
                subtotal = precio * pp.cantidad
                productos_detalle += (
                    f"Producto: {pp.producto.nombre}\n"
                    f"Cantidad: {pp.cantidad}\n"
                    f"Precio unitario: ${precio}\n"
                    f"Subtotal: ${subtotal}\n\n"
                )

            # Enviar correo electrónico de confirmación
            subject = "Confirmación de tu pedido - ChileMotors"
            message = (
                f"Estimado {datos_personales.nombre},\n\n"
                "Tu pedido ha sido recibido con éxito. Aquí están los detalles de tu pedido:\n\n"
                f"Número de pedido: {pedido.numero_pedido}\n"
                f"Fecha: {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Método de pago: {metodo_pago}\n\n"
                f"Productos:\n{productos_detalle}"
                f"Total: ${total}\n\n"
                "Gracias por tu compra en ChileMotors.\n"
                "Saludos,\nChileMotors"
            )
            recipient = datos_personales.email

            send_mail(subject, message, EMAIL_HOST_USER, [recipient])

            return redirect('pedido_exitoso')
    else:
        form = CheckoutForm(instance=datos_personales)

    return render(request, 'my_app/checkout.html', {
        'form': form,
        'productos_carrito': productos_carrito,
        'total': total
    })

@login_required
def pedido_exitoso(request):
    return render(request, 'my_app/pedido_exitoso.html')

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-fecha_pedido')
    for pedido in pedidos:
        for item in pedido.pedido_productos.all():
            item.subtotal = int(item.precio * item.cantidad)
    return render(request, 'my_app/mis_pedidos.html', {'pedidos': pedidos})