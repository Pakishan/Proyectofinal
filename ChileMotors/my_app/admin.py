from django.contrib import admin
from .models import Producto, ImagenProducto, Contacto
from .models import Pedido, ProductoCarrito, DatosPersonales, CarruselItem, Servicios, Categoria

admin.site.register(ProductoCarrito)
admin.site.register(DatosPersonales)
admin.site.register(Pedido)
admin.site.register(CarruselItem)
admin.site.register(Servicios)
admin.site.register(Categoria)

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    inlines = [ImagenProductoInline]

admin.site.register(Producto, ProductoAdmin)
admin.site.register(ImagenProducto)
admin.site.register(Contacto)