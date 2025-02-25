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
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)  # Opcional
    efectivo = models.DecimalField("Precio Efectivo", default=0, max_digits=10, decimal_places=2)
    debito = models.DecimalField("Precio Débito", default=0, max_digits=10, decimal_places=2)
    credito = models.DecimalField("Precio Crédito", default=0, max_digits=10, decimal_places=2)

    class Meta:
        abstract = True
        unique_together = ('marca',)  # Asegura que no se repitan combinaciones de marca en hijos si es relevante

    def __str__(self):
        if self.marca:
            return f"{self.marca.nombre} - Precios"
        return "Precios"

    # Método para actualizar precios
    @classmethod
    def actualizar_precio(cls, marca_id=None, efectivo=None, debito=None, credito=None):
        try:
            precio_instance = cls.objects.get(marca_id=marca_id)
            
            if efectivo is not None:
                precio_instance.efectivo = efectivo
            if debito is not None:
                precio_instance.debito = debito
            if credito is not None:
                precio_instance.credito = credito
            
            precio_instance.save()
            return precio_instance
        except cls.DoesNotExist:
            raise ValueError("No se encontró un precio para la marca especificada.")
    
    @classmethod
    def obtener_precio_por_marca(cls, marca_id=None):
        """
        Método de clase para obtener los precios por marca
        """
        if marca_id:
            return cls.objects.filter(marca_id=marca_id)
        return cls.objects.all()

class PrecioProducto(Precio):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('categoria', 'marca')  # Combina categoría y marca

    def __str__(self):
        if self.marca:
            return f"{self.categoria.nombre} - {self.marca.nombre} - Precios"
        return f"{self.categoria.nombre} - Precios"

    @classmethod
    def actualizar_precio(cls, categoria_id, marca_id=None, efectivo=None, debito=None, credito=None):
        try:
            precio_instance = cls.objects.get(categoria_id=categoria_id, marca_id=marca_id)
            
            if efectivo is not None:
                precio_instance.efectivo = efectivo
            if debito is not None:
                precio_instance.debito = debito
            if credito is not None:
                precio_instance.credito = credito
            
            precio_instance.save()
            return precio_instance
        except cls.DoesNotExist:
            raise ValueError("No se encontró un precio para la categoría y marca especificadas.")
    
    @classmethod
    def obtener_precio_por_categoria_y_marca(cls, categoria_id, marca_id=None):
        """
        Método de clase para obtener los precios por categoría y marca
        """
        if marca_id:
            return cls.objects.filter(categoria_id=categoria_id, marca_id=marca_id)
        return cls.objects.filter(categoria_id=categoria_id)

class PrecioCombo(Precio):
    class Meta:
        unique_together = ('marca',)  # Solo valida por marca

    def __str__(self):
        if self.marca:
            return f"Combo - {self.marca.nombre} - Precios"
        return "Combo - Precios"

    @classmethod
    def actualizar_precio(cls, marca_id=None, efectivo=None, debito=None, credito=None):
        try:
            precio_instance = cls.objects.get(marca_id=marca_id)
            
            if efectivo is not None:
                precio_instance.efectivo = efectivo
            if debito is not None:
                precio_instance.debito = debito
            if credito is not None:
                precio_instance.credito = credito
            
            precio_instance.save()
            return precio_instance
        except cls.DoesNotExist:
            raise ValueError("No se encontró un precio para la marca especificada.")

    @classmethod
    def obtener_precio_por_marca(cls, marca_id=None):
        """
        Método de clase para obtener los precios por marca
        """
        if marca_id:
            return cls.objects.filter(marca_id=marca_id)
        return cls.objects.all()

class Producto(models.Model):

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE, blank=True, null=True)
    precio = models.ForeignKey(PrecioProducto, on_delete=models.CASCADE, related_name="productos")  # Referencia al modelo Precio

    cantidad = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    
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

class CustomProduct(models.Model):
    name = models.CharField(_("Descripción"), max_length=100)
    color = models.CharField(_("Color"), max_length=100)
    talle = models.CharField(_("Talle"), max_length=100)
    precio = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2, default=0)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return self.name  

class Combo(models.Model):

    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, blank=True)
    precio = models.ForeignKey(PrecioCombo, on_delete=models.CASCADE, related_name="combos")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.marca.nombre} - {self.color.nombre} - {self.talle.nombre}"
    