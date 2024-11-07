from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import *
from user.models import ClientPayer


class Payment(models.Model):
    STATUS_CHOICES = (
        ('NO RETIRADO', 'NO RETIRADO'),
        ('RETIRADO', 'RETIRADO'),
        ('VENCIDO', 'VENCIDO'),
        ('DEVUELTO', 'DEVUELTO'),
    )
    
    payment_id= models.AutoField(('Payment ID'), primary_key=True, editable=False)
    client = models.ForeignKey(ClientPayer, on_delete=models.CASCADE, null=True, blank=True)
    small_amount_ok = models.BooleanField(default=False)
    small_amount= models.DecimalField(('Small amount'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(('Total amount'), max_digits=10, decimal_places=2)
    status = models.CharField(('Payment Status'), max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    start_date = models.DateTimeField(_("Rental date"), auto_now_add=True)
    end_date = models.DateTimeField(_("Return date"), null=True, blank=True)

    # Relación ManyToMany con las prendas
    productos = models.ManyToManyField(Producto, blank=True)  # Puede haber cero o más productos
    combo = models.ManyToManyField(Combo, blank=True)  # Puede haber cero o más trajes

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.payment_id}'