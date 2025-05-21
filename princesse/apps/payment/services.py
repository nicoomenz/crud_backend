# mi_app/services/payment_service.py

from payment.models import PaymentCombo, PaymentProduct
from product.models import Combo, CustomProduct, Producto
from rest_framework.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.db import transaction

import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, instance, data):
        self.instance = instance
        self.data = data
        self.old_products = list(instance.productos.all())
        self.old_custom_products = list(instance.custom_products.all())
        self.old_combo = list(instance.combo.all())
        self.old_status = instance.status
        self.new_products_data = data.get("productos")
        self.new_combo_data = data.get("combo")
        self.new_status = data.get("status", self.old_status)

    def process_update(self):
        with transaction.atomic():
            products_changed = self._products_changed()
            combo_changed = self._combos_changed()
            status_changed = self._status_changed()

            if (
                self.old_status == "DEVUELTO" and
                (products_changed or combo_changed)
            ):
                raise ValidationError("No se puede cambiar los productos en un estado devuelto. Primero cambiar el estado a NO RETIRADO")

            if products_changed:
                self._handle_product_change()
                logger.info(f"Cambiaron los productos del recibo {self.instance}")
            
            if combo_changed:
                self._handle_combo_change()
                logger.info(f"Cambiaron los combos del recibo {self.instance}")

            if status_changed:
                self._handle_status_change()
                logger.info(f"Cambio de estado del recibo {self.instance}")

            return self._save_instance()

    def _products_changed(self):
        """Devuelve True si los productos realmente cambiaron."""
        if self.new_products_data is None:
            return False
        
        payments_products = list(PaymentProduct.objects.filter(payment=self.instance, is_active=True))
        custom_products = list(self.instance.custom_products.filter(payment=self.instance, is_active=True))
        
        # Unir las dos listas
        current_products = payments_products + custom_products

        # Si la cantidad de productos cambió, ya está
        if len(current_products) != len(self.new_products_data):
            return True

        list_producto = []
        list_custom = []

        for producto in self.new_products_data:
            if producto.get('categoria') is not None:
                
                p = Producto.objects.filter(categoria=producto['categoria'].id, marca=producto['marca'].id, color=producto['color'].id, talle=producto['talle'].id, active=True).first()
                list_producto.append({
                    "producto": p,
                    "cantidad": int(producto["cantidad"])
                })
            else:
                list_custom.append(producto)
        
        # Comparar productos estándar
        for item in list_producto:
            producto = item["producto"]
            cantidad = item["cantidad"]
            match = next(
                (pp for pp in payments_products if pp.producto == producto and pp.cantidad == cantidad),
                None
            )
            if not match:
                return True
        
        # Comparar custom products
        
        custom_products_serialized = [model_to_dict(cp) for cp in custom_products]

        normalized_customs = []

        for c in custom_products_serialized:
            item = {
                'name': c['name'],
                'color': c['color'],
                'talle': c['talle'],
                'cantidad': c['cantidad'],
                'precio': float(c['precio']),
            }
            normalized_customs.append(item)

        for new_custom in list_custom:
            if new_custom not in normalized_customs:
                return True
            
        return False
    
    def _create_product(self):
        for prod_data in self.new_products_data:
            if prod_data.get('categoria') is not None:
                producto = Producto.objects.filter(categoria=prod_data['categoria'].id, marca=prod_data['marca'].id, color=prod_data['color'].id, talle=prod_data['talle'].id).first()
                cantidad = prod_data.get('cantidad', 1)

                if cantidad > producto.cantidad:
                    raise ValidationError(f"No hay suficiente stock para el producto {producto.categoria} {producto.marca} {producto.color} {producto.talle}. Stock disponible: {producto.cantidad}, cantidad solicitada: {cantidad}")
                
                payment_product, created = PaymentProduct.objects.get_or_create(
                    payment=self.instance,
                    producto=producto,
                    defaults={
                        "cantidad": cantidad,
                        "precio_efectivo": prod_data.get("efectivo"),
                        "precio_debito": prod_data.get("debito"),
                        "precio_credito": prod_data.get("credito"),
                        "is_active": True
                    }
                )

                if not created:
                    payment_product.cantidad = cantidad
                    payment_product.is_active = True
                    payment_product.save()


                
                producto.cantidad -= cantidad
                producto.save()
                self.instance.productos.add(producto)

            else:

                custom_product, created = CustomProduct.objects.get_or_create(
                    payment=self.instance,
                    name=prod_data.get("name"),
                    color=prod_data.get("color"),
                    talle=prod_data.get("talle"),
                    defaults={
                        "cantidad": prod_data.get("cantidad"),
                        "precio": prod_data.get("precio"),
                        "is_active": True
                    }
                )
                if not created:
                    custom_product.cantidad = prod_data.get('cantidad')
                    custom_product.precio = prod_data.get("precio")
                    custom_product.is_active = True
                    custom_product.save()

                self.instance.custom_products.add(custom_product)
    
    def _handle_product_change(self):

        old_payment_products = PaymentProduct.objects.filter(payment=self.instance.payment_id, is_active=True)
        old_custom_products = CustomProduct.objects.filter(payment=self.instance.payment_id, is_active=True)

        for payment_product in old_payment_products:
            payment_product.producto.cantidad += payment_product.cantidad
            payment_product.producto.save()
        
        old_payment_products.update(is_active=False)
        #borrar todos los productos
        for product in self.old_products:
            self.instance.productos.remove(product)

        old_custom_products.update(is_active=False)

        self._create_product()
        
    
    def _combos_changed(self):
        """Devuelve True si los combos realmente cambiaron."""
        
        if self.new_combo_data is None:
            return False
        payments_combos = list(PaymentCombo.objects.filter(payment=self.instance, is_active=True))

        if len(payments_combos) != len(self.new_combo_data):
            return True
        # Comparar combos
        for combo in self.new_combo_data:
            match = next(
                (pc for pc in payments_combos if pc.combo.id == combo['id'] and pc.cantidad == combo["cantidad"]),
                None
            )
            if not match:
                return True
        return False

    def _create_combo(self):
        for combo_data in self.new_combo_data:
            cantidad = combo_data.get("cantidad")

            # verificar si la cantidad solicitada es mayor al stock por producto del combo
            for producto in combo_data.get("productos"):
                producto = Producto.objects.filter(categoria=producto['categoria']['id'], marca=producto['marca']['id'], color=producto['color']['id'], talle=producto['talle']['id']).first()
                if cantidad > producto.cantidad:
                    raise ValidationError(f"No hay suficiente stock para el producto {producto.categoria} {producto.marca} {producto.color} {producto.talle}. Stock disponible: {producto.cantidad}, cantidad solicitada: {cantidad}")
            
            combo = Combo.objects.filter(id=combo_data['id']).first()
            payment_combo, created = PaymentCombo.objects.get_or_create(
                payment=self.instance,
                combo=combo,
                defaults={
                    "cantidad": cantidad,
                    "precio_efectivo": combo_data.get("precio").efectivo,
                    "precio_debito": combo_data.get("precio").debito,
                    "precio_credito": combo_data.get("precio").credito,
                    "is_active": True
                }
            )

            # Si el objeto ya existía, solo actualizás la cantidad y el is_active
            if not created:
                payment_combo.cantidad = cantidad
                payment_combo.is_active = True
                payment_combo.save()

            # Decrementar el stock de los productos del combo
            for producto in combo_data.get("productos"):
                producto = Producto.objects.filter(categoria=producto['categoria']['id'], marca=producto['marca']['id'], color=producto['color']['id'], talle=producto['talle']['id']).first()
                producto.cantidad -= cantidad
                producto.save()
            
            # Agregar el combo a la instancia de pago
            combo = Combo.objects.filter(id=combo_data['id']).first()
            self.instance.combo.add(combo)


    def _handle_combo_change(self):
        old_payment_combos = PaymentCombo.objects.filter(payment=self.instance.payment_id, is_active=True)
        # Devolver el stock de los productos por combo
        for payment_combo in old_payment_combos:
            for producto in payment_combo.combo.productos.all():
                producto.cantidad += payment_combo.cantidad
                producto.save()
            payment_combo.save()

        old_payment_combos.update(is_active=False)

        #borrar todos los combos
        for combo in self.old_combo:
            self.instance.combo.remove(combo)

        self._create_combo()
                

    def _status_changed(self):
        return self.new_status != self.old_status

    def _handle_status_change(self):
        
        if self.new_status == "DEVUELTO" and self.old_status != "DEVUELTO":
            old_payment_products = PaymentProduct.objects.filter(payment=self.instance.payment_id, is_active=True)

            for payment_product in old_payment_products:
                payment_product.producto.cantidad += payment_product.cantidad
                payment_product.producto.save()
            
            old_payment_combos = PaymentCombo.objects.filter(payment=self.instance.payment_id, is_active=True)
            # Devolver el stock de los productos por combo
            for payment_combo in old_payment_combos:
                for producto in payment_combo.combo.productos.all():
                    producto.cantidad += payment_combo.cantidad
                    producto.save()
                payment_combo.save()
            logger.info(f"Recibo devuelto {self.instance}")

        if self.new_status != "DEVUELTO" and self.old_status == "DEVUELTO":

            old_payment_products = PaymentProduct.objects.filter(payment=self.instance.payment_id, is_active=True)

            
            for payment_product in old_payment_products:
                cantidad = payment_product.cantidad
                if cantidad > payment_product.producto.cantidad:
                    raise ValidationError(f"No hay suficiente stock para el producto {producto.categoria} {producto.marca} {producto.color} {producto.talle}. Stock disponible: {producto.cantidad}, cantidad solicitada: {cantidad}")
                payment_product.producto.cantidad -= payment_product.cantidad
                payment_product.producto.save()
            
            old_payment_combos = PaymentCombo.objects.filter(payment=self.instance.payment_id, is_active=True)
            # Devolver el stock de los productos por combo
            for payment_combo in old_payment_combos:
                for producto in payment_combo.combo.productos.all():
                    cantidad = payment_combo.cantidad
                    if cantidad > producto.cantidad:
                        raise ValidationError(f"No hay suficiente stock para el producto {producto.categoria} {producto.marca} {producto.color} {producto.talle}. Stock disponible: {producto.cantidad}, cantidad solicitada: {cantidad}")
                    producto.cantidad -= payment_combo.cantidad
                    producto.save()
                payment_combo.save()
                
            logger.info(f"Recibo devuelto {self.instance}")
            logger.info(f"el recibo {self.instance} volvió a estar disponible")
            

    def _save_instance(self):
        self.data.pop('productos', None)
        self.data.pop('custom_products', None)
        self.data.pop('combo', None)

        # Setear campos normales
        for attr, value in self.data.items():
            setattr(self.instance, attr, value)

        
        self.instance.save()
        logger.info(f"Se creó o modifico el recibo {self.instance}")

        return self.instance
