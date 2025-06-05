from django.contrib import admin
from django.db import models
from user.models import *
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
@admin.register(ClientPayer)
class ClientPayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'dni', 'first_name', 'last_name', 'phone')