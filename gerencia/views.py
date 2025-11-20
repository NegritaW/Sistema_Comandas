from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from garzon.models import Producto, Comanda, ComandaItem, Categoria
from .models import HistorialPrecio

@login_required
def panel_gerencia(request):
    """
    Panel principal de gerencia
    """
    # Verificar que el usuario tenga rol de gerencia
    if getattr(request.user, 'rol', '').lower() != 'gerencia':
        return redirect('garzon:garzon_home')
    
    # Estadísticas rápidas
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)
    
    # Ventas
    ventas_hoy = Comanda.objects.filter(
        created_at__date=hoy, 
        estado__in=['E', 'L']
    ).count()
    
    ventas_semana = Comanda.objects.filter(
        created_at__date__gte=semana_pasada,
        estado__in=['E', 'L']
    ).count()
    
    ventas_mes = Comanda.objects.filter(
        created_at__date__gte=mes_pasado,
        estado__in=['E', 'L']
    ).count()
    
    # Ingresos
    ingresos_hoy = ComandaItem.objects.filter(
        comanda__created_at__date=hoy,
        comanda__estado__in=['E', 'L']
    ).aggregate(total=Sum('precio_unitario'))['total'] or 0
    
    # Productos más vendidos esta semana
    productos_mas_vendidos = ComandaItem.objects.filter(
        comanda__estado__in=['E', 'L'],
        comanda__created_at__date__gte=semana_pasada
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'ventas_hoy': ventas_hoy,
        'ventas_semana': ventas_semana,
        'ventas_mes': ventas_mes,
        'ingresos_hoy': float(ingresos_hoy),
        'productos_mas_vendidos': productos_mas_vendidos,
    }
    
    return render(request, 'panel_gerencia.html', context)

@login_required
def gestion_precios(request):
    """
    Gestión de precios de productos
    """
    if getattr(request.user, 'rol', '').lower() != 'gerencia':
        return redirect('garzon:garzon_home')
    
    categorias = Categoria.objects.prefetch_related('productos').all()
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        nuevo_precio = request.POST.get('nuevo_precio')
        razon = request.POST.get('razon', '')
        
        try:
            producto = get_object_or_404(Producto, id=producto_id)
            precio_anterior = producto.precio
            
            # Crear registro en historial antes de actualizar
            HistorialPrecio.objects.create(
                producto=producto,
                precio_anterior=precio_anterior,
                precio_nuevo=nuevo_precio,
                razon_cambio=razon,
                usuario=request.user
            )
            
            # Actualizar precio del producto
            producto.precio = nuevo_precio
            producto.save()
            
            return JsonResponse({
                'ok': True, 
                'mensaje': f'Precio de {producto.nombre} actualizado: ${precio_anterior} → ${nuevo_precio}'
            })
            
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'gestion_precios.html', context)

@login_required
@require_POST
def actualizar_precio(request, producto_id):
    """
    API para actualizar precio (AJAX)
    """
    producto = get_object_or_404(Producto, id=producto_id)
    data = json.loads(request.body)
    nuevo_precio = data.get('nuevo_precio')
    razon = data.get('razon', '')
    
    precio_anterior = producto.precio
    
    # Registrar en historial
    HistorialPrecio.objects.create(
        producto=producto,
        precio_anterior=precio_anterior,
        precio_nuevo=nuevo_precio,
        razon_cambio=razon,
        usuario=request.user
    )
    
    # Actualizar producto
    producto.precio = nuevo_precio
    producto.save()
    
    return JsonResponse({
        'ok': True,
        'precio_anterior': float(precio_anterior),
        'precio_nuevo': float(nuevo_precio),
        'producto': producto.nombre
    })

@login_required
def historial_precios(request):
    """
    Historial de cambios de precios
    """
    if getattr(request.user, 'rol', '').lower() != 'gerencia':
        return redirect('garzon:garzon_home')
    
    historial = HistorialPrecio.objects.select_related('producto', 'usuario').order_by('-fecha_cambio')
    
    # Filtros
    producto_id = request.GET.get('producto')
    if producto_id:
        historial = historial.filter(producto_id=producto_id)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        historial = historial.filter(fecha_cambio__date__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        historial = historial.filter(fecha_cambio__date__lte=fecha_hasta)
    
    productos = Producto.objects.all()
    
    context = {
        'historial': historial,
        'productos': productos,
    }
    return render(request, 'historial_precios.html', context)

@login_required
def reporte_ventas(request):
    """
    Reporte de ventas con gráficos
    """
    if getattr(request.user, 'rol', '').lower() != 'gerencia':
        return redirect('garzon:garzon_home')
    
    return render(request, 'reporte_ventas.html')

@login_required
def reporte_productos(request):
    """
    Reporte de productos más vendidos
    """
    if getattr(request.user, 'rol', '').lower() != 'gerencia':
        return redirect('garzon:garzon_home')
    
    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
    }
    return render(request, 'reporte_productos.html', context)

# APIs para gráficos
@login_required
def api_ventas(request):
    """
    API para datos de ventas (gráfico)
    """
    # Parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin = request.GET.get('fecha_fin', timezone.now().strftime('%Y-%m-%d'))
    tipo_agrupacion = request.GET.get('agrupacion', 'dia')
    
    # Filtro base - comandas enviadas o listas
    comandas = Comanda.objects.filter(
        estado__in=['E', 'L'],
        created_at__date__range=[fecha_inicio, fecha_fin]
    )
    
    datos = []
    
    if tipo_agrupacion == 'semana':
        # Agrupar por semana usando annotate
        from django.db.models.functions import ExtractWeek, ExtractYear
        ventas_por_semana = comandas.annotate(
            semana=ExtractWeek('created_at'),
            año=ExtractYear('created_at')
        ).values('año', 'semana').annotate(
            total_ventas=Count('id')
        ).order_by('año', 'semana')
        
        for item in ventas_por_semana:
            datos.append({
                'periodo': f"Sem {item['semana']}-{item['año']}",
                'ventas': item['total_ventas']
            })
    
    else:  # Agrupación por día
        ventas_por_dia = comandas.extra({
            'fecha': "DATE(created_at)"
        }).values('fecha').annotate(
            total_ventas=Count('id')
        ).order_by('fecha')
        
        for item in ventas_por_dia:
            # CORREGIDO: item['fecha'] ya es string, no necesita strftime
            datos.append({
                'fecha': item['fecha'],  # Ya viene como string 'YYYY-MM-DD'
                'ventas': item['total_ventas']
            })
    
    return JsonResponse({'datos': datos})

@login_required
def api_productos_mas_vendidos(request):
    """
    API para productos más vendidos
    """
    # Parámetros de filtro
    categoria_id = request.GET.get('categoria_id')
    fecha_inicio = request.GET.get('fecha_inicio', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    fecha_fin = request.GET.get('fecha_fin', timezone.now().strftime('%Y-%m-%d'))
    
    # Filtro base
    items = ComandaItem.objects.filter(
        comanda__estado__in=['E', 'L'],
        comanda__created_at__date__range=[fecha_inicio, fecha_fin]
    )
    
    # Aplicar filtros
    if categoria_id and categoria_id != 'todas':
        items = items.filter(producto__categoria_id=categoria_id)
    
    # Agrupar y contar
    productos_vendidos = items.values(
        'producto__nombre', 
        'producto__categoria__nombre'
    ).annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('precio_unitario')
    ).order_by('-total_vendido')[:15]
    
    datos = []
    for item in productos_vendidos:
        datos.append({
            'producto': item['producto__nombre'],
            'categoria': item['producto__categoria__nombre'],
            'cantidad': item['total_vendido'] or 0,
            'ingresos': float(item['total_ingresos'] or 0)
        })
    
    return JsonResponse({'datos': datos})