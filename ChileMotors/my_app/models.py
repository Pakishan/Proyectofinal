from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Modelo CarruselItem
class CarruselItem(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='carrusel/')
    activo = models.BooleanField(default=True)
    boton_texto = models.CharField(max_length=50, blank=True, null=True)
    boton_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo

# Modelo Servicios
class Servicios(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='carrusel/')
    activo = models.BooleanField(default=True)
    boton_texto = models.CharField(max_length=50, blank=True, null=True)
    boton_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo
    
# Modelo Categoria
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
# Modelo Contactos
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    fecha_envio = models.DateTimeField(default=timezone.now)  
    detalle = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
# Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()
    preciocondescuento = models.IntegerField(null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    imagen = models.ImageField(upload_to='imgproducto/')
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='productos', null=True, blank=True)

    def total(self):
        return self.precio * self.cantidad

    def __str__(self):
        return self.nombre
    
#Para imagenes adicionales
class ImagenProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='imgproducto/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

class ProductoCarrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='productos_carrito')

    def precio_total(self):
        if self.producto.preciocondescuento:
            return self.producto.preciocondescuento * self.cantidad
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class DatosPersonales(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class PedidoProducto(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='pedido_productos')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Pedido: {self.pedido.numero_pedido})"

class Pedido(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    numero_pedido = models.CharField(max_length=20)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=[('efectivo', 'Efectivo'), ('debito', 'Débito')], null=True)

    def __str__(self):
        return self.numero_pedido