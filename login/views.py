from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm


# --- Función que decide a qué "home" va cada rol ---
def redirect_by_role(user):
    rol = (user.rol or "").lower()
    if rol == "garzon":
        return 'garzon_home'
    if rol == "cocina":
        return 'home_cocina'
    if rol == "gerencia":
        return 'home_gerencia'
    if user.is_superuser or rol == "admin":
        return 'admin:index'
    return 'home_general'


# --- LOGIN ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                destino = redirect_by_role(user)
                try:
                    return redirect(destino)
                except Exception:
                    return redirect('home_general')
            else:
                messages.error(request, 'Tu cuenta está pendiente de activación.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')


# --- REGISTRO ---
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta registrada correctamente. Espera aprobación del administrador.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})


# --- HOME por rol (todas usan el mismo template "home.html") ---
@login_required
def home_garzon(request):
    return render(request, 'home.html', {
        'titulo': 'Panel Garzón 🍽️',
        'mensaje': f'Bienvenido {request.user.nombre_completo}, aquí verás tus pedidos y mesas.',
        'rol': 'garzon'
    })


@login_required
def home_cocina(request):
    return render(request, 'home.html', {
        'titulo': 'Panel Cocina 🔪',
        'mensaje': f'Bienvenido {request.user.nombre_completo}, aquí verás los pedidos en preparación.',
        'rol': 'cocina'
    })


@login_required
def home_gerencia(request):
    return render(request, 'home.html', {
        'titulo': 'Panel Gerencia 📊',
        'mensaje': f'Bienvenido {request.user.nombre_completo}, aquí podrás consultar reportes y métricas.',
        'rol': 'gerencia'
    })


@login_required
def home_general(request):
    return render(request, 'home.html', {
        'titulo': 'Inicio General',
        'mensaje': f'Hola {request.user.nombre_completo}, bienvenido al sistema.',
        'rol': 'general'
    })


# --- LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')