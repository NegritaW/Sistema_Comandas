from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    # Vistas por rol
    path('home/cocina/', views.home_cocina, name='home_cocina'),
    path('home/gerencia/', views.home_gerencia, name='home_gerencia'),
    path('home/general/', views.home_general, name='home_general'),
]

