from django.db import models
from django.utils.translation import gettext_lazy as _

class Categoria(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

class Talle(models.Model):
    nombre = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Tela(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Color(models.Model):

    nombre = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colores")

class Producto(models.Model):

    nombre = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE, blank=True, null=True)
    
    precio_efectivo = models.DecimalField(("Precio Efectivo"), default=0, max_digits=10, decimal_places=2)
    precio_debito = models.DecimalField(("Precio Debito"), default=0, max_digits=10, decimal_places=2)
    precio_credito = models.DecimalField(("Precio Credito"), default=0, max_digits=10, decimal_places=2)

    cantidad = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.nombre} - {self.color.nombre} - {self.talle.nombre}"

class Combo(models.Model):

    nombre = models.CharField(max_length=50)
    productos = models.ManyToManyField(Producto, blank=True)

    def __str__(self):
        return self.nombre