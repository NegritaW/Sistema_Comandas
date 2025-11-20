from django.contrib import admin
from .models import Categoria, Producto, ClienteExterno, Comanda, ComandaItem

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'created_at']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre', 'descripcion']
    list_filter = ['created_at']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'precio', 'categoria', 'activo', 'created_at']
    list_display_links = ['id', 'nombre']
    list_filter = ['categoria', 'activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'activo']
    ordering = ['categoria', 'nombre']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion', 'precio', 'categoria', 'imagen_url')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ClienteExterno)
class ClienteExternoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'created_at']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


class ComandaItemInline(admin.TabularInline):
    model = ComandaItem
    extra = 0
    readonly_fields = ['subtotal', 'created_at']
    fields = ['producto', 'cantidad', 'precio_unitario', 'notas', 'subtotal', 'created_at']
    
    def subtotal(self, obj):
        return f"${obj.subtotal()}"
    subtotal.short_description = 'Subtotal'


@admin.register(Comanda)
class ComandaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'origen_display_admin', 
        'estado', 
        'total_display', 
        'created_by', 
        'created_at', 
        'updated_at'
    ]
    list_display_links = ['id', 'origen_display_admin']
    list_filter = ['estado', 'created_at', 'updated_at']
    search_fields = [
        'numero_habitacion', 
        'cliente_externo__nombre',
        'id'
    ]
    list_editable = ['estado']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_display']
    
    inlines = [ComandaItemInline]
    
    fieldsets = (
        ('Información de la Comanda', {
            'fields': (
                'origen_display_admin',
                'estado', 
                'notas_cocina'
            )
        }),
        ('Origen', {
            'fields': (
                'numero_habitacion', 
                'cliente_externo'
            ),
            'classes': ('collapse',)
        }),
        ('Usuario y Fechas', {
            'fields': (
                'created_by',
                'created_at', 
                'updated_at',
                'total_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def origen_display_admin(self, obj):
        return obj.origen_display()
    origen_display_admin.short_description = 'Origen'
    
    def total_display(self, obj):
        return f"${obj.total()}"
    total_display.short_description = 'Total'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente_externo', 'created_by'
        ).prefetch_related('items')


@admin.register(ComandaItem)
class ComandaItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'comanda_display', 
        'producto', 
        'cantidad', 
        'precio_unitario', 
        'subtotal_display',
        'created_at'
    ]
    list_display_links = ['id', 'comanda_display']
    list_filter = ['comanda__estado', 'created_at', 'comanda__numero_habitacion']
    search_fields = [
        'producto__nombre',
        'comanda__id',
        'comanda__numero_habitacion',
        'comanda__cliente_externo__nombre'
    ]
    list_editable = ['cantidad']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Item', {
            'fields': (
                'comanda_display',
                'producto',
                'cantidad',
                'precio_unitario',
                'notas'
            )
        }),
        ('Cálculos', {
            'fields': ('subtotal_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'subtotal_display', 'comanda_display']
    
    def comanda_display(self, obj):
        return f"Comanda #{obj.comanda.id} - {obj.comanda.origen_display()}"
    comanda_display.short_description = 'Comanda'
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal()}"
    subtotal_display.short_description = 'Subtotal'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'comanda', 'comanda__cliente_externo', 'producto'
        )