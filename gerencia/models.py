from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from garzon.models import Producto, Comanda, ComandaItem

class HistorialPrecio(models.Model):
    """
    Historial de cambios de precios de productos
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='historial_precios')
    precio_anterior = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Precio anterior en pesos chilenos (entero positivo)"
    )
    precio_nuevo = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Precio nuevo en pesos chilenos (entero positivo)"
    )
    razon_cambio = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'historial_precio'
        verbose_name = 'Historial de Precio'
        verbose_name_plural = 'Historial de Precios'
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.producto.nombre} - ${self.precio_anterior} → ${self.precio_nuevo}"

    def diferencia(self):
        return self.precio_nuevo - self.precio_anterior
    
    def porcentaje_cambio(self):
        if self.precio_anterior > 0:
            return ((self.precio_nuevo - self.precio_anterior) / self.precio_anterior) * 100
        return 0