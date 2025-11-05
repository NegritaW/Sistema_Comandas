from django.urls import path
from . import views

urlpatterns = [
    path('', views.garzon_home, name='garzon_home'),
]
