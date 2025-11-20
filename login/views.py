from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm


# --- Función que decide a qué "home" va cada rol ---
def redirect_by_role(user):
    """
    Redirige según el campo 'rol' del usuario
    """
    # Usar el campo 'rol' del modelo de usuario personalizado
    rol = (getattr(user, 'rol', '') or "").lower().strip()
    
    if rol == "garzon" or rol == "garzón":
        return 'garzon:garzon_home'
    elif rol == "cocina":
        return 'cocina:home_cocina'
    elif rol == "gerencia":
        return 'gerencia:panel_gerencia'
    elif user.is_superuser or rol == "admin":
        return 'admin:index'
    else:
        # Por defecto, redirigir a garzón
        return 'garzon:garzon_home'

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
                except Exception as e:
                    print(f"Error en redirección: {e}")
                    # Fallback a garzon si hay error
                    return redirect('garzon:garzon_home')
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
            return render(request, 'registro.html', {
                'form': RegistroForm(), 
                'registro_exitoso': True
            })
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


# --- LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')