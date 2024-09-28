from django.db import models
from django.utils.translation import gettext_lazy as _
from clothes.models import Pantalon, Saco, Traje
from user.models import ClientPayer


class Payment(models.Model):
    
    payment_id= models.IntegerField(('Payment ID'), primary_key=True, editable=False)
    client = models.ForeignKey(ClientPayer, on_delete=models.CASCADE, null=True, blank=True)
    small_amount= models.DecimalField(('Small amount'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(('Total amount'), max_digits=10, decimal_places=2)
    status = models.CharField(('Payment status'), max_length=50)
    start_date = models.DateTimeField(_("Rental date"), auto_now_add=True)
    end_date = models.DateTimeField(_("Return date"), null=True, blank=True)

    # Relación ManyToMany con las prendas
    sacos = models.ManyToManyField(Saco, blank=True)  # Puede haber cero o más sacos
    pantalones = models.ManyToManyField(Pantalon, blank=True)  # Puede haber cero o más pantalones
    trajes = models.ManyToManyField(Traje, blank=True)  # Puede haber cero o más trajes


    def __str__(self):
        return f'{self.payment_id}'
    
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")