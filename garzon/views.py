from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def garzon_home(request):
    habitaciones = range(1, 41)  # 1 a 40
    return render(request, 'home_garzon.html', {
        'habitaciones': habitaciones
    })