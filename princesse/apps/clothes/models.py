from django.db import models

class Talle(models.Model):
    nombre = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Tela(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Color(models.Model):
    TIPO_PRENDA_CHOICES = [
        ('general', 'General'),
        ('vestido', 'Vestido'),
        ('saco', 'Saco'),
        ('pantalon', 'Pantalon'),
    ]

    nombre = models.CharField(max_length=50, unique=True)
    tipo_prenda = models.CharField(max_length=50, choices=TIPO_PRENDA_CHOICES, default='general')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_prenda_display()})"
class PrendaBase(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE, blank=True, null=True)
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.marca.nombre}, {self.color.nombre}, Talle: {self.talle.nombre}"
class Saco(PrendaBase):
    tipo = models.CharField(default="Saco", max_length=50)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"Saco: {super().__str__()}"

class Pantalon(PrendaBase):
    tipo = models.CharField(default="Pantalon", max_length=50)

    def __str__(self):
        return f"Pantalon: {super().__str__()}"

class Traje(models.Model):
    TIPO_TRAJE_CHOICES = [
        ('Ambo', 'Ambo'),
        ('Smoking', 'Smoking'),
    ]

    tipo_traje = models.CharField(max_length=50, choices=TIPO_TRAJE_CHOICES)
    saco = models.ForeignKey(Saco, on_delete=models.CASCADE)
    pantalon = models.ForeignKey(Pantalon, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo_traje}: {self.saco} y {self.pantalon}"