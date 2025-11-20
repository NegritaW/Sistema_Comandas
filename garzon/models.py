from django.db import models
from django.conf import settings
from django.utils import timezone

class Categoria(models.Model):
    """
    Categorías de productos (Entradas, Fondos, Bebidas, Postres, etc.)
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Productos del menú
    """
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class ClienteExterno(models.Model):
    nombre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cliente_externo'
    
    def __str__(self):
        return self.nombre


class Comanda(models.Model):
    """
    Comandas principales - pueden ser de habitación o cliente externo
    """
    ESTADOS = (
        ('P', 'Pendiente'),      # Creada por garzón, aparece en cocina
        ('E', 'Enviada'),        # Enviada a cocina
        ('L', 'Lista'),          # Preparada y lista (cocina)
        ('A', 'Anulada'),        # Cancelada
    )
    
    numero_habitacion = models.PositiveIntegerField(null=True, blank=True)
    cliente_externo = models.ForeignKey(ClienteExterno, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notas específicas para cocina
    notas_cocina = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'comanda'
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'
        ordering = ['-created_at']

    def __str__(self):
        if self.cliente_externo:
            return f"Comanda Cliente {self.cliente_externo.nombre} - {self.get_estado_display()}"
        else:
            return f"Comanda Hab {self.numero_habitacion} - {self.get_estado_display()}"

    def origen_display(self):
        """Muestra el origen de forma legible"""
        if self.cliente_externo:
            return f"Cliente: {self.cliente_externo.nombre}"
        elif self.numero_habitacion:
            return f"Habitación: {self.numero_habitacion}"
        return "Origen no especificado"
    
    def tiempo_transcurrido(self):
        """Calcula tiempo desde creación (para cocina)"""
        return timezone.now() - self.created_at
    
    def total(self):
        """Calcula el total de la comanda"""
        return sum(item.subtotal() for item in self.items.all())


class ComandaItem(models.Model):
    """
    Items individuales de cada comanda
    Relaciona Producto con Comanda
    """
    comanda = models.ForeignKey(Comanda, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)  # Precio al momento del pedido
    notas = models.TextField(blank=True, null=True)  # Especificaciones del cliente
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comanda_item'
        verbose_name = 'Item de Comanda'
        verbose_name_plural = 'Items de Comanda'

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - Comanda {self.comanda.id}"