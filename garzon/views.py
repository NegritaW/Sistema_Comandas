import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Comanda, ComandaItem, ClienteExterno, Producto, Categoria

@login_required
def garzon_home(request):
    habitaciones = range(1, 41)
    return render(request, 'home_garzon.html', {'habitaciones': habitaciones})

@login_required
@require_POST
def crear_comanda(request):
    try:
        num = int(request.POST.get('numero_habitacion'))
    except (TypeError, ValueError):
        return redirect('garzon:garzon_home')

    comanda = Comanda.objects.create(numero_habitacion=num, created_by=request.user)
    return redirect('garzon:garzon_comanda_detail', comanda_id=comanda.id)

@login_required
def comanda_detail(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    
    # Obtener productos organizados por categoría desde la base de datos
    categorias = Categoria.objects.prefetch_related('productos').all()
    menu_por_categoria = {}
    
    for categoria in categorias:
        menu_por_categoria[categoria.nombre] = [
            {
                'id': str(producto.id),
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'ingredientes': producto.descripcion or '',
                'imagen': producto.imagen_url or '/static/img/ejemplo.png'
            }
            for producto in categoria.productos.filter(activo=True)
        ]
    
    items = comanda.items.all()
    return render(request, 'comanda_detail.html', {
        'comanda': comanda,
        'items': items,
        'menu': menu_por_categoria,
    })

@login_required
@require_POST
def guardar_items(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    data = json.loads(request.body.decode('utf-8') or '{}')
    items = data.get('items', [])

    comanda.items.all().delete()
    for it in items:
        try:
            producto = Producto.objects.get(id=it.get('id'))
            ComandaItem.objects.create(
                comanda=comanda,
                producto=producto,
                cantidad=it.get('cantidad', 1),
                precio_unitario=producto.precio,
                notas=it.get('ingredientes', '')
            )
        except Producto.DoesNotExist:
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
    comanda = get_object_or_404(Comanda, id=comanda_id)
    data = json.loads(request.body.decode('utf-8') or '{}')
    items = data.get('items', [])

    if items:
        comanda.items.all().delete()
        for it in items:
            try:
                producto = Producto.objects.get(id=it.get('id'))
                ComandaItem.objects.create(
                    comanda=comanda,
                    producto=producto,
                    cantidad=it.get('cantidad', 1),
                    precio_unitario=producto.precio,
                    notas=it.get('ingredientes', '')
                )
            except Producto.DoesNotExist:
                ComandaItem.objects.create(
                    comanda=comanda,
                    nombre=it.get('nombre'),
                    precio=it.get('precio'),
                    cantidad=it.get('cantidad', 1),
                    ingredientes=it.get('ingredientes', ''),
                    imagen=it.get('imagen', '')
                )
    comanda.estado = 'E'  # Enviada
    comanda.save()
    return JsonResponse({'ok': True, 'redirect': reverse('garzon:garzon_home')})

@login_required
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
        comanda = Comanda.objects.create(cliente_externo=cliente, estado='P')
        return JsonResponse({"ok": True, "id": cliente.id, "nombre": cliente.nombre})
    return JsonResponse({"ok": False})

@login_required
def comanda_cliente(request, cliente_id):
    cliente = get_object_or_404(ClienteExterno, id=cliente_id)
    comanda, created = Comanda.objects.get_or_create(
        cliente_externo=cliente,
        estado='P',
        defaults={'created_by': request.user}
    )
    return redirect('garzon:garzon_comanda_detail', comanda_id=comanda.id)