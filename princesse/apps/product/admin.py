from django.contrib import admin
from product.models import *
# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)

@admin.register(Talle)
class TalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)

@admin.register(Tela)
class TelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'marca', 'color', 'talle', 'cantidad')
    search_fields = ('categoria__nombre', 'marca__nombre')  # Búsqueda
    list_filter = ('categoria', 'marca')  # Filtros en el admin

@admin.register(PrecioProducto)
class PrecioProductoAdmin(admin.ModelAdmin):
    fields = ('categoria', 'marca', 'efectivo', 'debito', 'credito')  # Incluye todos los campos
    list_display = ('id', 'categoria', 'marca', 'efectivo', 'debito', 'credito')
    search_fields = ('categoria__nombre', 'marca__nombre')  # Búsqueda
    list_filter = ('categoria', 'marca')  # Filtros en el admin

@admin.register(PrecioCombo)
class PrecioComboAdmin(admin.ModelAdmin):
    list_display = ('id', 'marca', 'efectivo', 'debito', 'credito')

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('id', 'marca')

@admin.register(CustomProduct)
class CustomProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'name', 'color', 'talle', 'cantidad', 'precio')
