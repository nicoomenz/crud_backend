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

class Precio(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)  # Opcional
    efectivo = models.DecimalField("Precio Efectivo", default=0, max_digits=10, decimal_places=2)
    debito = models.DecimalField("Precio Débito", default=0, max_digits=10, decimal_places=2)
    credito = models.DecimalField("Precio Crédito", default=0, max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('categoria', 'marca')  # Asegura que no se repitan combinaciones
        verbose_name = "Precio"
        verbose_name_plural = "Precios"

    def __str__(self):
        if self.marca:
            return f"{self.categoria.nombre} - {self.marca.nombre} - Precios"
        return f"{self.categoria.nombre} - Precios"

class Producto(models.Model):

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE, blank=True, null=True)
    precio = models.ForeignKey(Precio, on_delete=models.CASCADE, related_name="productos")  # Referencia al modelo Precio

    cantidad = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.color.nombre} - {self.talle.nombre}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['categoria', 'marca', 'color', 'talle', 'tela'],
                name='unique_producto',
                condition=models.Q(tela__isnull=False)  # Restricción de unicidad solo cuando 'tela' no es null
            ),
            models.UniqueConstraint(
                fields=['categoria', 'marca', 'color', 'talle'],
                name='unique_producto_tela_null',
                condition=models.Q(tela__isnull=True)  # Restricción de unicidad cuando 'tela' es null
            )
        ]

class Combo(models.Model):

    nombre = models.CharField(max_length=50)
    productos = models.ManyToManyField(Producto, blank=True)

    def __str__(self):
        return self.nombre