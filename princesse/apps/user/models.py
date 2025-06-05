from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token

class User(AbstractUser):
    first_name = models.CharField(_('Nombre'), max_length=100)
    last_name = models.CharField(_('Apellido'), max_length=100)
    email = models.EmailField(_("Direccion de email"), max_length=254)
    phone = models.CharField(_('Telefono'), max_length=25)
    change_password = models.BooleanField(_("Cambiar password"), default=False)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        db_table = 'user'
    
    @property
    def required_change_password(self):
        self.change_password = True
        self.save()
    
    @classmethod
    def get_token_user(cls, username):
        user = cls.objects.get(username=username)
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    @classmethod
    def get_user_from_username(cls, email):
        user = cls.objects.get(email=email)
        return user

# Create your models here.
class ClientPayer(models.Model):
    IVA_CHOICES = (
        ('RESPONSABLE_INSCRIPTO', 'RESPONSABLE INSCRIPTO'),
        ('NO_RESPONSABLE', 'NO RESPONSABLE'),
        ('MONOTRIBUTISTA', 'MONOTRIBUTISTA'),
        ('EXENTO', 'EXENTO'),
        ('CONSUMIDOR_FINAL', 'CONSUMIDOR FINAL')
    )
    dni = models.CharField(_("DNI"), max_length=10, unique=True)
    cuit = models.CharField(_("CUIT"), max_length=15, blank=True, null=True)
    first_name = models.CharField(_('Nombre'), max_length=30)
    last_name = models.CharField(_('Apellido'), max_length=30)
    direccion = models.CharField(_('Direccion'), max_length=100, default="")
    email = models.EmailField(_("Direccion de email"), max_length=254, blank=True, null=True)
    phone = models.CharField(_('Telefono'), max_length=25, blank=True, null=True)
    iva = models.CharField(max_length=30, choices=IVA_CHOICES, default=IVA_CHOICES[0][0], blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.dni} - {self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = _("Client Payer")
        verbose_name_plural = _("Clients Payer")