from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import *
from user.models import ClientPayer


class Payment(models.Model):
    STATUS_CHOICES = (
        ('NO RETIRADO', 'NO RETIRADO'),
        ('RETIRADO', 'RETIRADO'),
        ('VENCIDO', 'VENCIDO'),
        ('PARCIAL', 'PARCIAL'),
        ('DEVUELTO', 'DEVUELTO'),
    )

    PRICE_TYPE_CHOICES = (
        ('efectivo', 'Efectivo'),
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
    )
    
    payment_id= models.AutoField(('ID'), primary_key=True, editable=False)
    payment_date= models.DateField(_("Fecha de recibo"), auto_now_add=True)
    client = models.ForeignKey(ClientPayer, on_delete=models.CASCADE, null=True, blank=True)
    small_amount_ok = models.BooleanField(('Seña pagada'), default=False)
    small_amount= models.DecimalField(('Seña'), max_digits=10, decimal_places=2)
    subtotal_amount = models.DecimalField(('Subtotal'), max_digits=10, decimal_places=2)
    detail_amount = models.DecimalField(('Detalle'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(('Monto total'), max_digits=10, decimal_places=2)
    pick_up_date = models.DateField(_("Fecha de retiro"), null=True, blank=True)
    return_date = models.DateField(_("Fecha de devolución"), null=True, blank=True)
    status = models.CharField(('Estado'), max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0], blank=True, null=True)
    description = models.CharField(_("Descripción"),max_length=50,blank=True, null=True)
    descuento = models.IntegerField(('Descuento'), default=0)

    price_type = models.CharField(('Tipo de precio'), max_length=10, choices=PRICE_TYPE_CHOICES, default=PRICE_TYPE_CHOICES[0][0])
    # Relación ManyToMany con las prendas
    productos = models.ManyToManyField(Producto, blank=True)  # Puede haber cero o más productos
    combo = models.ManyToManyField(Combo, blank=True)  # Puede haber cero o más trajes
    custom_products = models.ManyToManyField(
        CustomProduct, 
        related_name="payments", 
        blank=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.payment_id}'
    

class PaymentProduct(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

class PaymentCombo(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()