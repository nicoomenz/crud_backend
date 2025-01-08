from datetime import datetime
from payment.models import *
from rest_framework import serializers

from user.serializers import ClientPayerDetailSerializer, ClientPayerSerializer
from product.serializers import CategoriaSerializer, ColorSerializer, ComboSerializer, MarcaSerializer, PrecioSerializer, ProductoSerializer, ProductDetailSerializer, TalleSerializer

class PaymentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProduct
        fields = ['producto', 'cantidad']
class PaymentSerializer(serializers.ModelSerializer):
    client = ClientPayerDetailSerializer()
    productos = ProductDetailSerializer(many=True, required=False)
    combo = ComboSerializer(many=True, required=False)

    class Meta:
        model = Payment
        fields = ['payment_id','payment_date', 'client', 'small_amount_ok', 'small_amount', 'subtotal_amount', 'descuento', 'detail_amount',  
                  'total_amount', 'pick_up_date', 'return_date', 'price_type', 'description', 'status', 'productos', 'combo']

    def to_internal_value(self, data):
        # Validar y convertir las fechas antes de todo lo demás
        for date_field in ['pick_up_date', 'return_date']:
            if date_field in data:
                try:
                    # Convertir de DD/MM/YYYY a objeto `date`
                    data[date_field] = datetime.strptime(data[date_field], "%d/%m/%Y").date()
                except ValueError:
                    raise serializers.ValidationError({
                        date_field: "Formato de fecha inválido. Use DD/MM/YYYY."
                    })

        # Llamar al método original para procesar el resto de los datos
        return super().to_internal_value(data)
    
    def validate(self, data):
        # Validar que haya al menos un producto o combo
        productos = data.get('productos', [])
        combo = data.get('combo', [])
        if not productos and not combo:
            raise serializers.ValidationError("Debe haber al menos un producto o un combo.")

        # Validar las fechas
        pick_up_date = data.get('pick_up_date')
        return_date = data.get('return_date')

        if pick_up_date and return_date and pick_up_date > return_date:
            raise serializers.ValidationError("La fecha de retiro no puede ser posterior a la fecha de devolución.")
        
        return data

    # def update(self, instance, validated_data):
    #     # Actualizamos los campos simples
    #     instance.payment_date = validated_data.get('payment_date', instance.payment_date)
    #     instance.small_amount_ok = validated_data.get('small_amount_ok', instance.small_amount_ok)
    #     instance.small_amount = validated_data.get('small_amount', instance.small_amount)
    #     instance.subtotal_amount = validated_data.get('subtotal_amount', instance.subtotal_amount)
    #     instance.descuento = validated_data.get('descuento', instance.descuento)
    #     instance.detail_amount = validated_data.get('detail_amount', instance.detail_amount)
    #     instance.total_amount = validated_data.get('total_amount', instance.total_amount)
    #     instance.pick_up_date = validated_data.get('pick_up_date', instance.pick_up_date)
    #     instance.return_date = validated_data.get('return_date', instance.return_date)
    #     instance.price_type = validated_data.get('price_type', instance.price_type)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.status = validated_data.get('status', instance.status)

    #     client_data = validated_data.pop('client')
    #     # Buscar el cliente existente
    #     try:
    #         client = ClientPayer.objects.get(id=client_data['id'])
    #     except ClientPayer.DoesNotExist:
    #         raise ValueError("El cliente con el ID proporcionado no existe")

    #     # Actualizar solo si los datos han cambiado
    #     for key, value in client_data.items():
    #         if getattr(client, key) != value:
    #             setattr(client, key, value)

    #     client.save()
    #     instance.client = client

    #     # Actualizamos los productos
    #     productos_data = validated_data.pop('productos', [])
    #     for producto_data in productos_data:
    #         categoria_data = producto_data.pop('categoria')
    #         marca_data = producto_data.pop('marca')
    #         color_data = producto_data.pop('color')
    #         talle_data = producto_data.pop('talle')
    #         categoria = Categoria.objects.update_or_create(id=categoria_data.id, defaults={'nombre': categoria_data.nombre})[0]
    #         marca = Marca.objects.update_or_create(id=marca_data.id, defaults={'nombre': marca_data.nombre})[0] if marca_data else None
    #         color = Color.objects.update_or_create(id=color_data.id, defaults={'nombre': color_data.nombre})[0]
    #         talle = Talle.objects.update_or_create(nombre=talle_data)[0]

    #         producto = Producto.objects.get(categoria=categoria, marca=marca, color=color, talle=talle)

    #         # Actualiza o crea el PaymentProduct
    #         PaymentProduct.objects.update(payment=instance, producto=producto, cantidad=producto_data['cantidad'])

    #         # Restar la cantidad de productos disponibles
    #         producto.cantidad -= producto_data['cantidad']
    #         producto.save()

    #     # Actualizar los combos (si existen)
    #     combo_data = validated_data.pop('combo', [])
    #     for combo in combo_data:
    #         combo_instance = Combo.objects.get(**combo)
    #         instance.combo.add(combo_instance)

    #     # Guardamos el objeto Payment actualizado
    #     instance.save()
    #     return instance
 
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['payment_date'] = instance.payment_date.strftime('%d/%m/%Y') if instance.payment_date else None
        data['pick_up_date'] = instance.pick_up_date.strftime('%d/%m/%Y') if instance.pick_up_date else None
        data['return_date'] = instance.return_date.strftime('%d/%m/%Y') if instance.return_date else None
        productos_representation = []
        for producto in instance.productos.all():
            payment_product = PaymentProduct.objects.filter(payment=instance, producto=producto).first()
            producto_data = {
                'categoria': CategoriaSerializer(producto.categoria).data,
                'marca': MarcaSerializer(producto.marca).data if producto.marca else None,
                'color': ColorSerializer(producto.color).data,
                'talle': TalleSerializer(producto.talle).data,
                'precio': PrecioSerializer(producto.precio).data,
                'cantidad': payment_product.cantidad if payment_product else None
            }
            productos_representation.append(producto_data)
        data['productos'] = productos_representation
        return data