from django.contrib import admin
from django.db import models
from payment.models import *
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'pick_up_date', 'return_date', 'client', 'small_amount', 'total_amount')

@admin.register(PaymentProduct)
class PaymentProductAdmin(admin.ModelAdmin):
    list_display = ('payment', 'producto', 'cantidad')