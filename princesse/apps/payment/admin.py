from django.contrib import admin
from django.db import models
from payment.models import *
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'pick_up_date', 'return_date', 'client', 'small_amount', 'total_amount')
    search_fields = ('payment_id', 'client__first_name', )  # Búsqueda
    list_filter = ('pick_up_date', 'return_date')  # Filtros en el admin

@admin.register(PaymentProduct)
class PaymentProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'producto', 'cantidad')


@admin.register(PaymentCombo)
class PaymentComboAdmin(admin.ModelAdmin):
    list_display = ('payment', 'combo', 'cantidad')