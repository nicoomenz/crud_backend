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

class PrimaryKeyforPrecioCombo(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            # Extraemos los IDs o nombres de categoría y marca
            marca = data.get('marca')
            
            if not marca:
                raise serializers.ValidationError("Se requiere 'marca'.")

            # Buscar por IDs primero
            queryset = self.get_queryset()
            try:
                return queryset.get(marca_id=marca['id'])
            except queryset.model.DoesNotExist:
                # Si no hay IDs, intentamos con los nombres
                try:
                    return queryset.get(
                        marca__nombre=marca
                    )
                except queryset.model.DoesNotExist:
                    raise serializers.ValidationError(
                        "No se encontró un precio la marca especificada."
                    )

        # Si no es un dict, asumimos que es un PK
        return super().to_internal_value(data)


        
class TallesVariantSerializer(serializers.ModelSerializer):
    nombre = PrimaryKeyOrNameRelatedField(queryset=Talle.objects.all())
    cantidad = serializers.IntegerField()
    class Meta:
        model = Talle
        fields = '__all__'

class PrecioProductoSerializer(serializers.ModelSerializer):
    categoria = PrimaryKeyOrNameRelatedField(queryset=Categoria.objects.all())
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    class Meta:
        model = PrecioProducto
        fields = ['id', 'categoria', 'marca', 'efectivo', 'debito', 'credito']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
        data['categoria'] = CategoriaSerializer(instance.categoria).data
        data['marca'] = MarcaSerializer(instance.marca).data if instance.marca else None
        return data

class PrecioComboSerializer(serializers.ModelSerializer):
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    class Meta:
        model = PrecioProducto
        fields = ['id','marca', 'efectivo', 'debito', 'credito'] 
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
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
    precio = PrimaryKeyforPrecio(queryset=PrecioProducto.objects.all(), required=False)
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
    precio = serializers.PrimaryKeyRelatedField(queryset=PrecioProducto.objects.all(), required=False)

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
        precio, created = PrecioProducto.objects.update_or_create(
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
                # Buscar si el producto ya existe
                existing_producto = Producto.objects.filter(
                    categoria=categoria,
                    marca=marca,
                    color=variante_data['color'],
                    talle=talle_data['nombre'],
                    precio=precio
                ).first()  # Traemos el primer resultado, si existe

                if existing_producto:
                    # Si existe el producto, lo activamos
                    existing_producto.active = True
                    existing_producto.cantidad = talle_data['cantidad']
                    existing_producto.save()
                    productos.append(existing_producto)
                else:
                    # Si no existe, lo creamos
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
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
        data['categoria'] = CategoriaSerializer(instance.categoria).data
        data['marca'] = MarcaSerializer(instance.marca).data if instance.marca else None
        data['color'] = ColorSerializer(instance.color).data
        data['talle'] = TalleSerializer(instance.talle).data
        data['tela'] = instance.tela if instance.tela else None
        data['precio'] = PrecioProductoSerializer(instance.precio).data 
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
    precio = PrecioProductoSerializer()
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

class ComboDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    color = PrimaryKeyOrNameRelatedField(queryset=Color.objects.all(), allow_null=True)
    talle = PrimaryKeyOrNameRelatedField(queryset=Talle.objects.all(), allow_null=True)
    productos = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    precio = PrimaryKeyforPrecioCombo(queryset=PrecioCombo.objects.all(), required=False)
    cantidad = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ['id', 'marca', 'productos', 'color', 'talle', 'tela', 'precio', 'cantidad']

class ComboSerializer(serializers.ModelSerializer):
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    color = PrimaryKeyOrNameRelatedField(queryset=Color.objects.all(), allow_null=True)
    talle = PrimaryKeyOrNameRelatedField(queryset=Talle.objects.all(), allow_null=True)
    productos = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    efectivo = serializers.IntegerField(write_only=True)
    debito = serializers.IntegerField(write_only=True)
    credito = serializers.IntegerField(write_only=True)
    precio = serializers.PrimaryKeyRelatedField(queryset=PrecioCombo.objects.all(), required=False)
    
    class Meta:
        model = Combo
        fields = '__all__'
    
    def validate(self, attrs):
        # Validar precios
        if not all(key in attrs for key in ['efectivo', 'debito', 'credito']):
            raise serializers.ValidationError("Faltan los precios requeridos: 'efectivo', 'debito', 'credito'.")
        return attrs

    def create(self, validated_data):
        marca = validated_data.get('marca')
        color = validated_data.get('color')
        talle = validated_data.get('talle')
        efectivo = validated_data.pop('efectivo')
        debito = validated_data.pop('debito')
        credito = validated_data.pop('credito')
        productos_data = validated_data.pop('productos', [])
        
        # Crear un nuevo registro en el modelo Precio
        precio, _ = PrecioCombo.objects.update_or_create(
            marca=marca,
            defaults={
                'efectivo': efectivo,
                'debito': debito,
                'credito': credito,
            }
        )

        validated_data['precio'] = precio  # Asignar el precio al validated_data

        combo = Combo.objects.filter(
        marca=marca,
        color=color,
        talle=talle,
        ).first()

        if combo:
            # Si el Combo existe y está desactivado, lo reactivamos
            if not combo.active:
                combo.active = True
                combo.save()
            combo.productos.clear()
        else:
            # Si no existe, lo creamos
            combo = Combo.objects.create(**validated_data)

        # Asignamos los productos relacionados
        for producto_data in productos_data:
            producto_id = producto_data.get("id")
            combo.productos.add(producto_id)

        return combo

    def update(self, instance, validated_data):
        marca = validated_data.get('marca')
        efectivo = validated_data.pop('efectivo')
        debito = validated_data.pop('debito')
        credito = validated_data.pop('credito')
        productos_data = validated_data.pop('productos', [])
        
        # Crear un nuevo registro en el modelo Precio
        precio, _ = PrecioCombo.objects.update_or_create(
            marca=marca,
            defaults={
                'efectivo': efectivo,
                'debito': debito,
                'credito': credito,
            }
        )

        validated_data['precio'] = precio  # Asignar el precio al validated_data

        instance.productos.clear()  # Limpiar los productos existentes antes de agregar los nuevos
        for producto_data in productos_data:
            producto_id = producto_data.get("id")
            instance.productos.add(producto_id)
        
        # Guardar el objeto Combo actualizado
        instance.save()
        
        return instance
    
    def to_representation(self, instance):
        # Obtener la representación original del Combo
        representation = super().to_representation(instance)
        
        # Añadir productos a la representación
        productos = instance.productos.all()  # Obtiene los productos relacionados
        productos_rep = ProductoSerializer(productos, many=True).data  # Serializa los productos
        
        # Añadir los productos serializados a la representación
        representation['productos'] = productos_rep

        # La marca ya está serializada como instancia completa en el serializer
        # Lo mismo para el precio
        
        representation['marca'] = MarcaSerializer(instance.marca).data
        representation['color'] = ColorSerializer(instance.color).data
        representation['talle'] = TalleSerializer(instance.talle).data
        representation['precio'] = PrecioComboSerializer(instance.precio).data
        
        return representation



class PrecioComboSerializer(serializers.ModelSerializer):
    marca = PrimaryKeyOrNameRelatedField(queryset=Marca.objects.all(), allow_null=True)
    class Meta:
        model = PrecioCombo
        fields = ['id', 'marca', 'efectivo', 'debito', 'credito']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Aquí se asegura que todos los campos sean serializados correctamente
        data['marca'] = MarcaSerializer(instance.marca).data if instance.marca else None
        return data