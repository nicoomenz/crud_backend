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

class PrimaryKeyOrNameRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.get('id', data.get('nombre'))
        
        try:
            return self.get_queryset().get(pk=data)
        except (TypeError, ValueError, self.get_queryset().model.DoesNotExist):
            return self.get_queryset().get(nombre=data)

class PrimaryKeyforPrecio(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            # Extraemos los IDs o nombres de categoría y marca
            categoria = data.get('categoria')
            marca = data.get('marca')
            
            if not categoria or not marca:
                raise serializers.ValidationError("Se requieren 'categoria' y 'marca'.")

            # Buscar por IDs primero
            queryset = self.get_queryset()
            try:
                return queryset.get(categoria_id=categoria['id'], marca_id=marca['id'])
            except queryset.model.DoesNotExist:
                # Si no hay IDs, intentamos con los nombres
                try:
                    return queryset.get(
                        categoria__nombre=categoria,
                        marca__nombre=marca
                    )
                except queryset.model.DoesNotExist:
                    raise serializers.ValidationError(
                        "No se encontró un precio para la categoría y marca especificadas."
                    )

        # Si no es un dict, asumimos que es un PK
        return super().to_internal_value(data)


        
class TallesVariantSerializer(serializers.ModelSerializer):
    nombre = PrimaryKeyOrNameRelatedField(queryset=Talle.objects.all())
    cantidad = serializers.IntegerField()
    class Meta:
        model = Talle
        fields = '__all__'

class PrecioSerializer(serializers.ModelSerializer):
    categoria = PrimaryKeyOrNameRelatedField(queryset=Categoria.objects.all())
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    class Meta:
        model = Precio
        fields = ['id', 'categoria', 'marca', 'efectivo', 'debito', 'credito']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
        data['categoria'] = CategoriaSerializer(instance.categoria).data
        data['marca'] = MarcaSerializer(instance.marca).data if instance.marca else None
        return data

    

class VarianteSerializer(serializers.Serializer):
    color = PrimaryKeyOrNameRelatedField(queryset=Color.objects.all())
    talles = TallesVariantSerializer(many=True)
    

class ProductDetailSerializer(serializers.Serializer):
    categoria = PrimaryKeyOrNameRelatedField(queryset=Categoria.objects.all())
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    color = PrimaryKeyOrNameRelatedField(queryset=Color.objects.all(), allow_null=True)
    talle = PrimaryKeyOrNameRelatedField(queryset=Talle.objects.all())
    precio = PrimaryKeyforPrecio(queryset=Precio.objects.all(), required=False)
    cantidad = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ['categoria', 'marca', 'color', 'talle', 'tela', 'cantidad','precio']
class ProductoSerializer(serializers.ModelSerializer):
    variantes = VarianteSerializer(many=True, write_only=True, required=False)
    categoria = PrimaryKeyOrNameRelatedField(queryset=Categoria.objects.all())
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    efectivo = serializers.IntegerField(write_only=True)
    debito = serializers.IntegerField(write_only=True)
    credito = serializers.IntegerField(write_only=True)
    precio = serializers.PrimaryKeyRelatedField(queryset=Precio.objects.all(), required=False)

    class Meta:
        model = Producto
        fields = ['id', 'categoria', 'marca', 'cantidad', 'tela', 'variantes', 'precio', 'efectivo', 'debito', 'credito']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.fields['variantes'].required = True
        else:
            self.fields['variantes'].required = False
    
    def create(self, validated_data):
        variantes_data = validated_data.pop('variantes', [])
        categoria = validated_data['categoria']
        marca = validated_data.get('marca')

        # Obtener los precios
        efectivo = validated_data.get('efectivo')
        debito = validated_data.get('debito')
        credito = validated_data.get('credito')

        if not (efectivo and debito and credito):
            raise serializers.ValidationError("Faltan los precios requeridos: 'efectivo', 'debito', 'credito'.")
        
        # Crear un nuevo registro en el modelo Precio
        precio, created = Precio.objects.update_or_create(
            categoria=categoria,
            marca=marca,
            defaults={
                'efectivo': efectivo,
                'debito': debito,
                'credito': credito,
            }
        )

        validated_data['precio'] = precio  # Asignar el precio al validated_data
    
        productos = []
        for variante_data in variantes_data:
            for talle_data in variante_data['talles']:
                producto_data = {
                    'categoria': categoria,
                    'marca': marca,
                    'color': variante_data['color'],
                    'talle': talle_data['nombre'],
                    'tela': validated_data.get('tela'),
                    'precio': precio,  # Asignar el registro Precio recién creado
                    'cantidad': talle_data['cantidad'],
                }
                producto = Producto.objects.create(**producto_data)
                productos.append(producto)

        return productos

    def update(self, instance, validated_data):

        categoria_id = validated_data.get("categoria")
        marca_id = validated_data.get("marca", None)
        efectivo = validated_data.get("efectivo")
        debito = validated_data.get("debito")
        credito = validated_data.get("credito")
         # Actualizar como en el ejemplo anterior
        validated_data.pop('variantes', None)
        

        # Delegar la lógica de actualización al modelo Precio
        if categoria_id:
            try:

                Precio.actualizar_precio(
                    categoria_id=categoria_id,
                    marca_id=marca_id,
                    efectivo=efectivo,
                    debito=debito,
                    credito=credito,
                )
            except ValueError as e:
                raise serializers.ValidationError({"error": str(e)})
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
        data['categoria'] = CategoriaSerializer(instance.categoria).data
        data['marca'] = MarcaSerializer(instance.marca).data if instance.marca else None
        data['color'] = ColorSerializer(instance.color).data
        data['talle'] = TalleSerializer(instance.talle).data
        data['tela'] = instance.tela if instance.tela else None
        data['precio'] = PrecioSerializer(instance.precio).data 
        data.pop('variantes', None)
        return data

class VarianteCompactaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    color = ColorSerializer()
    talles = serializers.SerializerMethodField()

    def get_talles(self, obj):
        talles = obj['talles']
        return [
            {   
                "talle": TalleSerializer(talle['nombre']).data,
                "cantidad": talle['cantidad']
            }
            for talle in talles
        ]

class ProductoCompactoSerializer(serializers.Serializer):
    categoria = CategoriaSerializer()
    marca = MarcaSerializer(allow_null=True)
    variantes = serializers.SerializerMethodField()
    precio = PrecioSerializer()
    tela = serializers.CharField(allow_null=True)

    def get_variantes(self, obj):
        productos = obj['productos']
        variantes = {}
        
        for producto in productos:
            id = producto['id']
            color = producto['producto'].color
            if color not in variantes:
                variantes[color] = {'id': id, 'color': color, 'talles': []}
            variantes[color]['talles'].append({
                'nombre': producto['producto'].talle,
                'cantidad': producto['producto'].cantidad,
                
            })

        return VarianteCompactaSerializer(variantes.values(), many=True).data
class ComboSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Combo
        fields = '__all__'