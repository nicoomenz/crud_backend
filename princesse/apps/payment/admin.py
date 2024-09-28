from django.contrib import admin
from django.db import models
from clothes.models import *
# Register your models here.

@admin.register(Talle)
class TalleAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Tela)
class TelaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_prenda')

@admin.register(Saco)
class SacoAdmin(admin.ModelAdmin):
    list_display = ('tipo',)

@admin.register(Pantalon)
class PantalonAdmin(admin.ModelAdmin):
    list_display = ('tipo',)
