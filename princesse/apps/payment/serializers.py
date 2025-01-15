from datetime import datetime
from payment.models import *
from rest_framework import serializers

from user.serializers import ClientPayerDetailSerializer, ClientPayerSerializer
from product.serializers import CategoriaSerializer, ColorSerializer, ComboDetailSerializer, ComboSerializer, MarcaSerializer, PrecioComboSerializer, PrecioProductoSerializer, ProductoSerializer, ProductDetailSerializer, TalleSerializer

class PaymentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProduct
        fields = ['producto', 'cantidad']

class PaymentComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCombo
        fields = ['producto', 'cantidad']
class PaymentSerializer(serializers.ModelSerializer):
    client = ClientPayerDetailSerializer()
    productos = ProductDetailSerializer(many=True, required=False)
    combo = ComboDetailSerializer(many=True, required=False)

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
                'precio': PrecioProductoSerializer(producto.precio).data,
                'cantidad': payment_product.cantidad if payment_product else None
            }
            productos_representation.append(producto_data)
        data['productos'] = productos_representation
        combos_representation = []
        for combo in instance.combo.all():
            payment_combo = PaymentCombo.objects.filter(payment=instance, combo=combo).first()
            combo_data = {
                'id': combo.id,
                'marca': MarcaSerializer(combo.marca).data if combo.marca else None,
                'color': ColorSerializer(combo.color).data,
                'talle': TalleSerializer(combo.talle).data,
                'precio': PrecioComboSerializer(combo.precio).data,
                'cantidad': payment_combo.cantidad if payment_combo else None
            }
            productos_data = []
            for producto in combo.productos.all():  # O la relación adecuada para obtener los productos del combo
                payment_product = PaymentProduct.objects.filter(payment=instance, producto=producto).first()
                producto_data = {
                    'categoria': CategoriaSerializer(producto.categoria).data,
                    'marca': MarcaSerializer(producto.marca).data if producto.marca else None,
                    'color': ColorSerializer(producto.color).data,
                    'talle': TalleSerializer(producto.talle).data,
                    'precio': PrecioProductoSerializer(producto.precio).data,
                    'cantidad': payment_product.cantidad if payment_product else None
                }
                productos_data.append(producto_data)
            
            # Añadimos los productos al combo_data
            combo_data['productos'] = productos_data
            combos_representation.append(combo_data)
        data['combo'] = combos_representation
        return data