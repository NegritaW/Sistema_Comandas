from django.urls import path
from . import views

app_name = 'gerencia'

urlpatterns = [
    path('', views.panel_gerencia, name='panel_gerencia'),
    
    # Gestión de precios
    path('precios/', views.gestion_precios, name='gestion_precios'),
    path('precios/actualizar/<int:producto_id>/', views.actualizar_precio, name='actualizar_precio'),
    path('precios/historial/', views.historial_precios, name='historial_precios'),
    
    # Reportes y gráficos
    path('reportes/ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reportes/productos/', views.reporte_productos, name='reporte_productos'),
    path('api/ventas/', views.api_ventas, name='api_ventas'),
    path('api/productos-mas-vendidos/', views.api_productos_mas_vendidos, name='api_productos_mas_vendidos'),
]