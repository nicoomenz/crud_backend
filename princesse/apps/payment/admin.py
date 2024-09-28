from django.contrib import admin
from django.db import models
from payment.models import *
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'small_amount', 'total_amount', 'start_date', 'end_date')
