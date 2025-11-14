from django.urls import path
from . import views

urlpatterns = [
    path('', views.garzon_home, name='garzon_home'),
    path('crear/', views.crear_comanda, name='garzon_crear_comanda'),
    path('comanda/<int:comanda_id>/', views.comanda_detail, name='garzon_comanda_detail'),
    path('comanda/<int:comanda_id>/guardar_items/', views.guardar_items, name='garzon_guardar_items'),
    path('comanda/<int:comanda_id>/enviar/', views.enviar_comanda, name='garzon_enviar_comanda'),
    path('clientes_externos/', views.clientes_externos, name='clientes_externos'),
    path('agregar_cliente_externo/', views.agregar_cliente_externo, name='agregar_cliente_externo'),
    path('comanda_cliente/<int:cliente_id>/', views.comanda_cliente, name='comanda_cliente'),
]
