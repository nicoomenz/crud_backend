from product.models import *
from rest_framework import serializers

class TalleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Talle
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categoria
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Marca
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = '__all__'


class VarianteSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all())
    talle = serializers.PrimaryKeyRelatedField(queryset=Talle.objects.all())
    cantidad = serializers.IntegerField()

class ProductoSerializer(serializers.ModelSerializer):
    variantes = VarianteSerializer(many=True, write_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'categoria', 'marca', 'cantidad', 'tela', 'precio_efectivo', 'precio_debito', 'precio_credito', 'variantes']

    def create(self, validated_data):
        variantes_data = validated_data.pop('variantes')
        productos = []
        for variante_data in variantes_data:
            producto_data = {
                'nombre': variante_data['nombre'],
                'categoria': validated_data['categoria'],
                'marca': validated_data.get('marca'),
                'color': variante_data['color'],
                'talle': variante_data['talle'],
                'tela': validated_data.get('tela'),
                'precio_efectivo': validated_data['precio_efectivo'],
                'precio_debito': validated_data['precio_debito'],
                'precio_credito': validated_data['precio_credito'],
                'cantidad': variante_data['cantidad'],
            }
            producto = Producto.objects.create(**producto_data)
            productos.append(producto)
        return productos


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['nombre'] = instance.nombre
        data['categoria'] = instance.categoria.nombre
        data['marca'] = instance.marca.nombre if instance.marca else None
        data['color'] = instance.color.nombre
        data['talle'] = instance.talle.nombre
        data['tela'] = instance.tela.nombre if instance.tela else None
        data.pop('variantes', None)
        return data

class ComboSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Combo
        fields = '__all__'