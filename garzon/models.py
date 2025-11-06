from django.db import models
from django.conf import settings

class ClienteExterno(models.Model):
    nombre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Comanda(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('E', 'Enviada'),
    )
    numero_habitacion = models.PositiveIntegerField(null=True, blank=True)
    cliente_externo = models.ForeignKey(ClienteExterno, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.cliente_externo:
            return f"Comanda Cliente {self.cliente_externo.nombre} - {self.get_estado_display()}"
        else:
            return f"Comanda Hab {self.numero_habitacion} - {self.get_estado_display()}"


class ComandaItem(models.Model):
    comanda = models.ForeignKey(Comanda, related_name='items', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    ingredientes = models.TextField(blank=True, null=True)
    imagen = models.CharField(max_length=500, blank=True, null=True)  # url relativa en static o externa

    def subtotal(self):
        return self.precio * self.cantidad

    def __str__(self):
        return f"{self.nombre} x{self.cantidad} ({self.comanda})"