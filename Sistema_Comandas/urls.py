from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),  # redirección automática al login
    path('admin/', admin.site.urls),
    path('login/', include('login.urls')),
    path('garzon/', include('garzon.urls')),
]