from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from garzon.models import Comanda, ComandaItem
import json

@login_required
def home_cocina(request):
    """
    Vista principal de cocina - renderiza el template
    """
    return render(request, 'home_cocina.html')

@login_required
def api_comandas_list(request):
    """
    API para obtener lista de comandas en formato compatible con el template
    """
    # Comandas en estado 'Pendiente'
    comandas = Comanda.objects.filter(estado='E').prefetch_related('items__producto').order_by('created_at')
    
    comandas_data = []
    for comanda in comandas:
        # Calcular tiempo transcurrido
        tiempo_transcurrido = timezone.now() - comanda.created_at
        minutos = int(tiempo_transcurrido.total_seconds() // 60)
        segundos = int(tiempo_transcurrido.total_seconds() % 60)
        
        # Formatear items para el template
        items_data = []
        for item in comanda.items.all():
            # CORREGIDO: Usar solo el campo 'notas' que existe en el modelo
            detalles = item.notas or ''
            
            items_data.append({
                'nombre': item.producto.nombre if item.producto else item.nombre,
                'cantidad': item.cantidad,
                'detalles': detalles
            })
        
        comandas_data.append({
            'id': comanda.id,
            'numero_orden': comanda.id,  # Para compatibilidad con template
            'numero_habitacion': comanda.numero_habitacion,
            'confirmado_at': comanda.created_at.isoformat(),  # Para el timer
            'estado': 'PENDIENTE',  # Para compatibilidad
            'items': items_data,
            'tiempo_transcurrido': f"{minutos}m {segundos}s"
        })
    
    return JsonResponse({'ok': True, 'comandas': comandas_data})

@login_required
@require_POST
def api_marcar_lista(request, comanda_id):
    """
    API para marcar comanda como lista
    """
    comanda = get_object_or_404(Comanda, id=comanda_id, estado='E')
    comanda.estado = 'L'  # Lista
    comanda.save()
    return JsonResponse({'ok': True})

@login_required
@require_POST
def api_eliminar_comanda(request, comanda_id):
    """
    API para eliminar/anular comanda
    """
    comanda = get_object_or_404(Comanda, id=comanda_id, estado='E')
    comanda.estado = 'A'  # Anulada
    comanda.save()
    return JsonResponse({'ok': True})

# Vistas adicionales para compatibilidad (si las necesitas)
@login_required
@require_POST
def api_receive_comanda(request):
    """
    API para recibir comandas (si usas comunicación entre apps)
    """
    return JsonResponse({'ok': True, 'message': 'Comanda recibida'})

# Vistas no-API (para usar si prefieres no-AJAX)
@login_required
@require_POST
def marcar_comanda_lista(request, comanda_id):
    """Vista normal (no API) para marcar como lista"""
    comanda = get_object_or_404(Comanda, id=comanda_id, estado='E')
    comanda.estado = 'L'
    comanda.save()
    return redirect('cocina:home_cocina')

@login_required
@require_POST
def anular_comanda(request, comanda_id):
    """Vista normal (no API) para anular comanda"""
    comanda = get_object_or_404(Comanda, id=comanda_id, estado='E')
    comanda.estado = 'A'
    comanda.save()
    return redirect('cocina:home_cocina')