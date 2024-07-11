from django.urls import path
from . import views
from .views import producto_detalle_view
from .views import pedido_exitoso
from .views import add_to_cart, ver_carrito, eliminar_del_carrito
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('servicios/', views.servicios, name='servicios'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto/exito/<str:nombre>/', views.contacto_exito, name='contacto_exito'),
    path('productos/', views.productos, name='productos'),
    path('producto/<int:pk>/', producto_detalle_view, name='producto_detalle'),
    path('registro/', views.registro, name='registro'),
    path('registro_exitoso/', views.registro_exitoso, name='registro_exitoso'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('carrito/', views.carrito, name='carrito'),
    path('producto/<int:pk>/', producto_detalle_view, name='producto_detalle'),
    path('pedido_exitoso/', pedido_exitoso, name='pedido_exitoso'),
    path('login/', auth_views.LoginView.as_view(template_name='my_app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('ver_carrito/', ver_carrito, name='ver_carrito'),
    path('eliminar_del_carrito/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido_exitoso/', views.pedido_exitoso, name='pedido_exitoso'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]
