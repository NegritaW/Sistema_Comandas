from django.urls import path
from . import views

app_name = 'cocina'

urlpatterns = [
    path('', views.home_cocina, name='home_cocina'),
    path('api/comandas/', views.api_comandas_list, name='api_comandas_list'),
    path('api/receive/', views.api_receive_comanda, name='api_receive_comanda'),
    path('api/comandas/<str:comanda_id>/lista/', views.api_marcar_lista, name='api_marcar_lista'),
    path('api/comandas/<str:comanda_id>/eliminar/', views.api_eliminar_comanda, name='api_eliminar_comanda'),
]
