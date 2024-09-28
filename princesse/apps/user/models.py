from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class ClientPayer(models.Model):
    IVA_CHOICES = (
        ('RESPONSABLEINSCRIPTO', 'RESPONSABLE INSCRIPTO'),
        ('NORESPONSABLE', 'NO RESPONSABLE'),
        ('MONOTRIBUTISTA', 'MONOTRIBUTISTA'),
        ('EXENTO', 'EXENTO'),
        ('CONSUMIDORFINAL', 'CONSUMIDOR FINAL')
    )
    dni = models.CharField(_("DNI"), max_length=50)
    cuit = models.CharField(_("CUIT"), max_length=50)
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellido'), max_length=100)
    phone = models.CharField(_('Telefono'), max_length=25, blank=True, null=True)
    iva = models.CharField(max_length=30, choices=IVA_CHOICES, default=IVA_CHOICES[0][0])
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.dni} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = _("Client Payer")
        verbose_name_plural = _("Clients Payer")