from datetime import datetime, date
from payment.models import *
from rest_framework import serializers

from user.serializers import ClientPayerDetailSerializer
from product.serializers import CategoriaSerializer, ColorSerializer, ComboDetailSerializer, MarcaSerializer, PrecioComboSerializer, PrecioProductoSerializer, ProductSerializer, TalleSerializer

class PaymentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProduct
        fields = ['producto', 'cantidad']

class PaymentComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCombo
        fields = ['producto', 'cantidad']

class PaymentCustomProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomProduct
        fields = ['name', 'price', 'cantidad']
class PaymentSerializer(serializers.ModelSerializer):
    client = ClientPayerDetailSerializer()
    productos = ProductSerializer(many=True, required=False)
    combo = ComboDetailSerializer(many=True, required=False)

    class Meta:
        model = Payment
        fields = ['payment_id', 'payment_type', 'payment_date', 'client', 'small_amount_ok', 'small_amount', 'subtotal_amount', 'descuento', 'detail_amount',  
                  'total_amount', 'pick_up_date', 'return_date', 'test_date', 'price_type', 'description', 'status', 'productos', 'combo']

    def to_internal_value(self, data):
        # Validar y convertir las fechas antes de todo lo demás
        for date_field in ['pick_up_date', 'return_date', 'test_date']:
            
            if date_field in data:
                try:
                    # Convertir de DD/MM/YYYY a objeto `date`
                    if data[date_field]:
                        data[date_field] = datetime.strptime(data[date_field], "%d/%m/%Y").date()
                except ValueError:
                    raise serializers.ValidationError({
                        date_field: "Formato de fecha inválido. Use DD/MM/YYYY."
                    })

        # Llamar al método original para procesar el resto de los datos
        return super().to_internal_value(data)

    def validate(self, data):
        productos = data.get('productos', getattr(self.instance, 'productos', []))
        combo = data.get('combo', getattr(self.instance, 'combo', []))

        #Validar que haya al menos un producto o combo en creación o actualización
        if not productos and not combo:
            raise serializers.ValidationError("Debe haber al menos un producto o un combo.")

        #Validar las fechas siempre
        pick_up_date = data.get('pick_up_date') or getattr(self.instance, 'pick_up_date', None)
        return_date = data.get('return_date') or getattr(self.instance, 'return_date', None)

        if pick_up_date and return_date and pick_up_date > return_date:
            raise serializers.ValidationError("La fecha de retiro no puede ser posterior a la fecha de devolución.")

        return data


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['payment_type'] = instance.payment_type
        data['payment_date'] = instance.payment_date.strftime('%d/%m/%Y') if instance.payment_date else None
        data['pick_up_date'] = instance.pick_up_date.strftime('%d/%m/%Y') if instance.pick_up_date else None
        data['test_date'] = instance.test_date.strftime('%d/%m/%Y') if instance.test_date else None
        data['return_date'] = instance.return_date.strftime('%d/%m/%Y') if instance.return_date else None
        productos_representation = []
        for producto in instance.productos.all():
            payment_product = PaymentProduct.objects.filter(payment=instance, producto=producto).first()
            producto_data = {
                'id': producto.id,
                'categoria': CategoriaSerializer(producto.categoria).data,
                'marca': MarcaSerializer(producto.marca).data if producto.marca else None,
                'color': ColorSerializer(producto.color).data,
                'talle': TalleSerializer(producto.talle).data,
                'precio': PrecioProductoSerializer(producto.precio).data,
                'cantidad': payment_product.cantidad if payment_product else None
            }
            productos_representation.append(producto_data)
        data['productos'] = productos_representation
        data['productos'].extend(list(instance.custom_products.filter(is_active=True).values('name', 'color', 'talle', 'precio', 'cantidad')))
        combos_representation = []
        for combo in instance.combo.all():
            payment_combo = PaymentCombo.objects.filter(payment=instance, combo=combo).first()
            combo_data = {
                'id': combo.id,
                'type': combo.type,
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
                    'type': producto.type,
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
        # data['custom_product'] = instance.custom_products.all().values('name', 'color', 'talle', 'precio', 'cantidad')
        return data

class PaymentUpdateSerializer(serializers.ModelSerializer):
    productos = ProductSerializer(many=True, required=False)
    combo = ComboDetailSerializer(many=True, required=False)

    class Meta:
        model = Payment
        fields = ['payment_id', 'payment_type', 'payment_date', 'small_amount_ok', 'small_amount', 'subtotal_amount', 'descuento', 'detail_amount',  
                  'total_amount', 'pick_up_date', 'return_date', 'test_date', 'price_type', 'description', 'status', 'productos', 'combo']

    def to_internal_value(self, data):
        # Validar y convertir las fechas antes de todo lo demás
        for date_field in ['pick_up_date', 'return_date', 'test_date']:
            
            if date_field in data:
                try:
                    # Convertir de DD/MM/YYYY a objeto `date`
                    if data[date_field]:
                        data[date_field] = datetime.strptime(data[date_field], "%d/%m/%Y").date()
                except ValueError:
                    raise serializers.ValidationError({
                        date_field: "Formato de fecha inválido. Use DD/MM/YYYY."
                    })

        # Llamar al método original para procesar el resto de los datos
        return super().to_internal_value(data)

    def validate(self, data):
        productos = data.get('productos', getattr(self.instance, 'productos', []))
        combo = data.get('combo', getattr(self.instance, 'combo', []))

        #Validar que haya al menos un producto o combo en creación o actualización
        if not productos and not combo:
            raise serializers.ValidationError("Debe haber al menos un producto o un combo.")

        #Validar las fechas siempre
        pick_up_date = data.get('pick_up_date') or getattr(self.instance, 'pick_up_date', None)
        return_date = data.get('return_date') or getattr(self.instance, 'return_date', None)

        if pick_up_date and return_date and pick_up_date > return_date:
            raise serializers.ValidationError("La fecha de retiro no puede ser posterior a la fecha de devolución.")
        
        today = date.today()

        # Validar contra hoy SOLO si es creación o si cambió la fecha
        if not self.instance or (
            'pick_up_date' in data and pick_up_date != self.instance.pick_up_date
        ):
            if pick_up_date and pick_up_date < today:
                raise serializers.ValidationError("La fecha de retiro no puede ser anterior a hoy.")

        if not self.instance or (
            'return_date' in data and return_date != self.instance.return_date
        ):
            if return_date and return_date < today:
                raise serializers.ValidationError("La fecha de devolución no puede ser anterior a hoy.")

        return data


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['payment_type'] = instance.payment_type
        data['payment_date'] = instance.payment_date.strftime('%d/%m/%Y') if instance.payment_date else None
        data['pick_up_date'] = instance.pick_up_date.strftime('%d/%m/%Y') if instance.pick_up_date else None
        data['test_date'] = instance.test_date.strftime('%d/%m/%Y') if instance.test_date else None
        data['return_date'] = instance.return_date.strftime('%d/%m/%Y') if instance.return_date else None
        productos_representation = []
        for producto in instance.productos.all():
            payment_product = PaymentProduct.objects.filter(payment=instance, producto=producto).first()
            producto_data = {
                'id': producto.id,
                'categoria': CategoriaSerializer(producto.categoria).data,
                'marca': MarcaSerializer(producto.marca).data if producto.marca else None,
                'color': ColorSerializer(producto.color).data,
                'talle': TalleSerializer(producto.talle).data,
                'precio': PrecioProductoSerializer(producto.precio).data,
                'cantidad': payment_product.cantidad if payment_product else None
            }
            productos_representation.append(producto_data)
        data['productos'] = productos_representation
        data['productos'].extend(list(instance.custom_products.all().values('name', 'color', 'talle', 'precio', 'cantidad')))
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
        # data['custom_product'] = instance.custom_products.all().values('name', 'color', 'talle', 'precio', 'cantidad')
        return data

class PaymentProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProduct
        fields = "__all__"

class PaymentComboSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCombo
        fields = "__all__"