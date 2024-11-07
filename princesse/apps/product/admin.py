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
    list_display = ('id', 'nombre', 'color', 'talle',)

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)
