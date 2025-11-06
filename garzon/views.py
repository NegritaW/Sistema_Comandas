from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse
from .models import Comanda, ComandaItem, ClienteExterno
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

# Hardcodeamos el menú (podrías moverlo a JSON o DB después)
MENU = {
    "Entradas": [
        {"id": "e1", "nombre": "Ensalada César", "ingredientes": "Lechuga, pollo, croutons, parmesano", "precio": 4500, "imagen": "/static/img/ejemplo.png"},
        {"id": "e2", "nombre": "Bruschetta", "ingredientes": "Pan, tomate, ajo, albahaca", "precio": 3200, "imagen": "/static/img/ejemplo.png"},
    ],
    "Fondos": [
        {"id": "f1", "nombre": "Lomo a lo pobre", "ingredientes": "Carne, huevo, papas", "precio": 8200, "imagen": "/static/img/ejemplo.png"},
        {"id": "f2", "nombre": "Pasta Alfredo", "ingredientes": "Pasta, crema, parmesano", "precio": 6800, "imagen": "/static/img/ejemplo.png"},
    ],
    "Bebidas": [
        {"id": "b1", "nombre": "Coca-Cola 500ml", "ingredientes": "Bebida", "precio": 1200, "imagen": "/static/img/ejemplo.png"},
        {"id": "b2", "nombre": "Jugo de Naranja", "ingredientes": "Jugo natural", "precio": 1500, "imagen": "/static/img/ejemplo.png"},
    ],
    "Postres": [
        {"id": "p1", "nombre": "Tiramisú", "ingredientes": "Queso mascarpone, café", "precio": 3800, "imagen": "/static/img/ejemplo.png"},
        {"id": "p2", "nombre": "Helado", "ingredientes": "Vainilla / Chocolate", "precio": 1800, "imagen": "/static/img/ejemplo.png"},
    ],
}


@login_required
def garzon_home(request):
    habitaciones = range(1, 41)
    return render(request, 'home_garzon.html', {'habitaciones': habitaciones})


@login_required
@require_POST
def crear_comanda(request):
    # recibe numero_habitacion desde form POST
    try:
        num = int(request.POST.get('numero_habitacion'))
    except (TypeError, ValueError):
        return redirect('garzon_home')

    # crea una nueva comanda pendiente y redirige a detalle
    comanda = Comanda.objects.create(numero_habitacion=num, created_by=request.user)
    return redirect('garzon_comanda_detail', comanda_id=comanda.id)


@login_required
def comanda_detail(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    # obtener items existentes
    items = comanda.items.all()
    return render(request, 'comanda_detail.html', {
        'comanda': comanda,
        'items': items,
        'menu': MENU,
    })


@login_required
@require_POST
def guardar_items(request, comanda_id):
    """
    Guarda items recibidos via JSON en el body.
    Estructura esperada:
    { items: [{id, nombre, precio, cantidad, ingredientes, imagen}, ...] }
    """
    import json
    comanda = get_object_or_404(Comanda, id=comanda_id)
    data = json.loads(request.body.decode('utf-8') or '{}')
    items = data.get('items', [])

    # Borra items anteriores y reemplaza (o podrías actualizar)
    comanda.items.all().delete()
    for it in items:
        ComandaItem.objects.create(
            comanda=comanda,
            nombre=it.get('nombre'),
            precio=it.get('precio'),
            cantidad=it.get('cantidad', 1),
            ingredientes=it.get('ingredientes', ''),
            imagen=it.get('imagen', '')
        )
    return JsonResponse({'ok': True})


@login_required
@require_POST
def enviar_comanda(request, comanda_id):
    """
    Confirma envío: guarda items (si vienen) y cambia estado a ENVIADA.
    """
    import json
    comanda = get_object_or_404(Comanda, id=comanda_id)
    data = json.loads(request.body.decode('utf-8') or '{}')
    items = data.get('items', [])

    # Guardar/actualizar items (si vienen)
    if items:
        comanda.items.all().delete()
        for it in items:
            ComandaItem.objects.create(
                comanda=comanda,
                nombre=it.get('nombre'),
                precio=it.get('precio'),
                cantidad=it.get('cantidad', 1),
                ingredientes=it.get('ingredientes', ''),
                imagen=it.get('imagen', '')
            )

    comanda.estado = 'E'
    comanda.save()
    # devolver url de redirección al home del garzón
    return JsonResponse({'ok': True, 'redirect': reverse('garzon_home')})

def clientes_externos(request):
    clientes = ClienteExterno.objects.order_by('-created_at')
    lista = []
    for c in clientes:
        diff = now() - c.created_at
        if diff < timedelta(minutes=1):
            tiempo = "unos segundos"
        elif diff < timedelta(hours=1):
            tiempo = f"{int(diff.seconds/60)} min"
        else:
            tiempo = f"{int(diff.seconds/3600)} h"
        lista.append({"id": c.id, "nombre": c.nombre, "tiempo": tiempo})
    return render(request, 'clientes_externos.html', {'clientes': lista})



@csrf_exempt
def agregar_cliente_externo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre")
        if not nombre:
            return JsonResponse({"ok": False})
        cliente = ClienteExterno.objects.create(nombre=nombre)
        # Crear su comanda vacía automáticamente
        comanda = Comanda.objects.create(cliente_externo=cliente, estado='P')
        return JsonResponse({"ok": True, "id": cliente.id, "nombre": cliente.nombre})
    return JsonResponse({"ok": False})

@login_required
def comanda_cliente(request, cliente_id):
    cliente = get_object_or_404(ClienteExterno, id=cliente_id)
    # Buscar si ya tiene una comanda pendiente, o crear una nueva
    comanda, created = Comanda.objects.get_or_create(
        cliente_externo=cliente,
        estado='P',
        defaults={'created_by': request.user}
    )
    return redirect('garzon_comanda_detail', comanda_id=comanda.id)