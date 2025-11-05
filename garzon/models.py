from django.db import models
from django.conf import settings

class Comanda(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('E', 'Enviada'),
    )
    numero_habitacion = models.PositiveIntegerField()
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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