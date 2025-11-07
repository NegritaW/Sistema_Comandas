import uuid
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Almacenamiento en memoria (temporal)
# Cada comanda: {
#   "id": str,
#   "numero_orden": int,
#   "confirmado_at": ISO datetime str,
#   "items": [ {"nombre":..., "cantidad":..., "detalles":...}, ... ],
#   "numero_habitacion": int or None,
#   "estado": "EN_PROCESO"|"LISTO"
# }
COMMANDS = []

# Ejemplos hardcodeados iniciales (opcional)
COMMANDS.extend([
    {
        "id": str(uuid.uuid4()),
        "numero_orden": 101,
        "confirmado_at": timezone.now().isoformat(),
        "items": [
            {"nombre": "Lomo a lo pobre", "cantidad": 1, "detalles": "Sin cebolla"},
            {"nombre": "Coca-Cola 500ml", "cantidad": 2, "detalles": ""}
        ],
        "numero_habitacion": 12,
        "estado": "EN_PROCESO"
    },
    {
        "id": str(uuid.uuid4()),
        "numero_orden": 102,
        "confirmado_at": timezone.now().isoformat(),
        "items": [
            {"nombre": "Pasta Alfredo", "cantidad": 1, "detalles": "Extra parmesano"},
            {"nombre": "Tiramisú", "cantidad": 1, "detalles": "Sin licor"}
        ],
        "numero_habitacion": None,
        "estado": "EN_PROCESO"
    }
])


@login_required
def home_cocina(request):
    """
    Página principal que muestra las comandas.
    El template hace polling a /api/comandas/ para obtener la lista.
    """
    return render(request, 'home_cocina.html', {})


@require_GET
@login_required
def api_comandas_list(request):
    """
    Devuelve JSON con las comandas (ordenadas por confirmado_at asc).
    """
    # ordenar por confirmado_at
    def key_fn(c):
        return c.get('confirmado_at') or ''
    data = sorted(COMMANDS, key=key_fn)
    return JsonResponse({"ok": True, "comandas": data})


@require_POST
@login_required
def api_receive_comanda(request):
    """
    Endpoint que la app de garzón puede llamar para enviar una comanda.
    Espera JSON con:
    {
      "numero_orden": 123,
      "numero_habitacion": 5 | null,
      "items": [{ "nombre": "...", "cantidad": 1, "detalles": "..." }, ... ]
    }
    Responde con la comanda creada.
    """
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    numero_orden = payload.get('numero_orden')
    items = payload.get('items', [])
    numero_habitacion = payload.get('numero_habitacion')

    if not numero_orden or not isinstance(items, list):
        return HttpResponseBadRequest("Falta numero_orden o items")

    comanda = {
        "id": str(uuid.uuid4()),
        "numero_orden": numero_orden,
        "confirmado_at": timezone.now().isoformat(),
        "items": items,
        "numero_habitacion": numero_habitacion,
        "estado": "EN_PROCESO"
    }
    COMMANDS.append(comanda)
    return JsonResponse({"ok": True, "comanda": comanda})


@require_POST
@login_required
def api_marcar_lista(request, comanda_id):
    """
    Marca la comanda como LISTO.
    """
    # buscar por id
    for c in COMMANDS:
        if c['id'] == comanda_id:
            c['estado'] = "LISTO"
            # opcional: guardar cuando se completó
            c['listo_at'] = timezone.now().isoformat()
            return JsonResponse({"ok": True, "comanda": c})
    return JsonResponse({"ok": False, "error": "Comanda no encontrada"}, status=404)


@require_POST
@login_required
def api_eliminar_comanda(request, comanda_id):
    """
    Elimina la comanda (borrar).
    """
    global COMMANDS
    before = len(COMMANDS)
    COMMANDS = [c for c in COMMANDS if c['id'] != comanda_id]
    after = len(COMMANDS)
    if before == after:
        return JsonResponse({"ok": False, "error": "Comanda no encontrada"}, status=404)
    return JsonResponse({"ok": True})
