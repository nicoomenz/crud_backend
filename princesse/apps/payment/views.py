import json
from django.forms import ValidationError
from django.shortcuts import render
from payment.models import *
from payment.serializers import PaymentSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F
from django.core.mail import EmailMessage
from rest_framework.decorators import action
from django.http import FileResponse
from django.http import HttpResponse
from payment.utils import generate_invoice_pdf
# Create your views here.

import logging

logger = logging.getLogger(__name__)

class PaymentsViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    def get_queryset(self):
        # Retornar solo los usuarios activos
            return super().get_queryset().filter(is_active=True)
    
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            data = request.data
            try:
                
                payment_serializer = PaymentSerializer(data=data)
                if payment_serializer.is_valid():
                    data = payment_serializer.validated_data
                    # Extraer datos de cliente
                    
                    client_data = data.pop('client')
                    if client_data.get('id') == 0:
                        client_data.pop('id')
                    client, created = ClientPayer.objects.get_or_create(**client_data)
                    logger.info(f"Cliente {'creado' if created else 'encontrado'}: {client}")

                    # Crear el pago
                    productos_data = data.pop('productos', [])
                    combo_data = data.pop('combo', [])
                    payment = Payment.objects.create(client=client, **data)
                    logger.info(f"Pago creado con ID: {payment.payment_id}")
                    # Procesar productos
                    
                    for producto_data in productos_data:
                        if 'categoria' in producto_data:
                            logger.info(f"Procesando producto: {producto_data}")
                            categoria_data = producto_data.pop('categoria')
                            marca_data = producto_data.pop('marca')
                            color_data = producto_data.pop('color')
                            talle_data = producto_data.pop('talle')
                            categoria = Categoria.objects.get_or_create(id=categoria_data.id, defaults={'nombre': categoria_data.nombre})[0]
                            marca = Marca.objects.get_or_create(id=marca_data.id, defaults={'nombre': marca_data.nombre})[0] if marca_data else None
                            color = Color.objects.get_or_create(id=color_data.id, defaults={'nombre': color_data.nombre})[0]
                            talle = Talle.objects.get_or_create(nombre=talle_data)[0]
                            
                            producto = Producto.objects.get(categoria=categoria, marca=marca, color=color, talle=talle)
                            logger.info(f"Producto encontrado: {producto}")
                            if producto.cantidad < producto_data['cantidad']:
                                logger.error(f"No hay suficiente cantidad del producto")
                                raise ValidationError(f"No hay suficiente cantidad del producto: {producto.categoria.nombre}. Disponible: {producto.cantidad}, Solicitado: {producto_data['cantidad']}")
                                
                            # Actualizamos o creamos el PaymentProduct
                            
                            PaymentProduct.objects.create(payment=payment, producto=producto, cantidad=producto_data['cantidad'])
                            logger.info(f"Producto añadido al pago: {producto} (cantidad: {producto_data['cantidad']})")

                            Producto.objects.filter(id=producto.id).update(cantidad=F('cantidad') - producto_data['cantidad'])
                            logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")

                            payment.productos.add(producto)
                        else:
                            # Producto simple => CustomProduct
                            custom_product = CustomProduct.objects.create(
                                name=producto_data['name'],
                                color=producto_data.get('color'),
                                talle=producto_data.get('talle'),
                                precio=producto_data.get('precio', 0),
                                cantidad=producto_data.get('cantidad', 1)
                            )
                            payment.custom_products.add(custom_product)
                            logger.info(f"CustomProduct creado para Payment {payment.payment_id}")
                        
                    
                    # Procesar combos
                    combo_data = request.data.get("combo", [])
                    if combo_data and isinstance(combo_data, list):
                        for combo in combo_data:
                            combo_id = combo["id"]
                            combo_instance = Combo.objects.get(id=combo_id)
                            payment.combo.add(combo_instance)
                            PaymentCombo.objects.create(payment=payment, combo=combo_instance, cantidad=combo['cantidad'])
                            logger.info(f"Combo añadido al pago: {combo_instance}")
                            productos = combo.get("productos", [])
                            # Restar cantidades de los productos dentro del combo
                            for producto_data in productos:
                                
                                categoria_data = producto_data.get('categoria')
                                marca_data = producto_data.get('marca')
                                color_data = producto_data.get('color')
                                talle_data = producto_data.get('talle')

                                categoria = Categoria.objects.get_or_create(id=categoria_data['id'], defaults={'nombre': categoria_data['nombre']})[0]
                                marca = Marca.objects.get_or_create(id=marca_data['id'], defaults={'nombre': marca_data['nombre']})[0] if marca_data else None
                                color = Color.objects.get_or_create(id=color_data['id'], defaults={'nombre': color_data['nombre']})[0]
                                talle = Talle.objects.get_or_create(nombre=talle_data['nombre'])[0]
                                producto = Producto.objects.get(categoria=categoria, marca=marca, color=color, talle=talle)
                                logger.info(f"Producto encontrado: {producto}")
                                if producto.cantidad < combo['cantidad']:
                                    logger.error(f"No hay suficiente cantidad del producto")
                                    raise ValidationError(f"No hay suficiente cantidad del producto: {producto.categoria.nombre}. Disponible: {producto.cantidad}, Solicitado: {combo['cantidad']}")
                                
                                # Actualizamos o creamos el PaymentProduct
                                PaymentProduct.objects.create(payment=payment, producto=producto, cantidad=combo['cantidad'])
                                logger.info(f"Producto añadido al pago: {producto} (cantidad: {combo['cantidad']})")
                                producto.cantidad -= combo['cantidad']
                                producto.save()
                                logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")

                    serializer = self.get_serializer(payment)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"Error al validar el pago: {payment_serializer.errors}")
                    return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error al crear el pago: {str(e)}", exc_info=True)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            data = request.data
            try:
                
                payment_serializer = PaymentSerializer(data=data)
                if payment_serializer.is_valid():
                    instance = self.get_object()
                    validated_data = payment_serializer.validated_data
                    previous_status = instance.status
                
                    # Actualizamos los campos simples
                    instance.payment_date = validated_data.get('payment_date', instance.payment_date)
                    instance.small_amount_ok = validated_data.get('small_amount_ok', instance.small_amount_ok)
                    instance.small_amount = validated_data.get('small_amount', instance.small_amount)
                    instance.subtotal_amount = validated_data.get('subtotal_amount', instance.subtotal_amount)
                    instance.descuento = validated_data.get('descuento', instance.descuento)
                    instance.detail_amount = validated_data.get('detail_amount', instance.detail_amount)
                    instance.total_amount = validated_data.get('total_amount', instance.total_amount)
                    instance.pick_up_date = validated_data.get('pick_up_date', instance.pick_up_date)
                    instance.return_date = validated_data.get('return_date', instance.return_date)
                    instance.price_type = validated_data.get('price_type', instance.price_type)
                    instance.description = validated_data.get('description', instance.description)
                    instance.status = validated_data.get('status', instance.status)
                    
                    client_data = validated_data.pop('client')
                    # Buscar el cliente existente
                    try:
                        client = ClientPayer.objects.get(id=client_data['id'])
                    except ClientPayer.DoesNotExist:
                        raise ValueError("El cliente con el ID proporcionado no existe")

                    # Actualizar solo si los datos han cambiado
                    for key, value in client_data.items():
                        if getattr(client, key) != value:
                            setattr(client, key, value)

                    client.save()
                    instance.client = client
                    logger.info(f"Cliente modificado: {client}")
                    # Actualizamos los productos
                    productos_data = validated_data.pop('productos', [])
                    for producto_data in productos_data:
                        if 'categoria' in producto_data:
                            logger.info(f"Procesando producto: {producto_data}")
                            categoria_data = producto_data.pop('categoria')
                            marca_data = producto_data.pop('marca')
                            color_data = producto_data.pop('color')
                            talle_data = producto_data.pop('talle')

                            categoria = Categoria.objects.update_or_create(id=categoria_data.id, defaults={'nombre': categoria_data.nombre})[0]
                            marca = Marca.objects.update_or_create(id=marca_data.id, defaults={'nombre': marca_data.nombre})[0] if marca_data else None
                            color = Color.objects.update_or_create(id=color_data.id, defaults={'nombre': color_data.nombre})[0]
                            talle = Talle.objects.update_or_create(nombre=talle_data)[0]

                            producto = Producto.objects.get(categoria=categoria, marca=marca, color=color, talle=talle)

                            # Si el estado cambió a "DEVUELTO", revertimos la cantidad
                            if previous_status != 'DEVUELTO' and instance.status == 'DEVUELTO':
                                check_cantidad = PaymentProduct.objects.get(payment=instance, producto=producto)
                                if check_cantidad:
                                    # Añadir la cantidad de productos devueltos
                                    Producto.objects.filter(id=producto.id).update(cantidad=F('cantidad') + check_cantidad.cantidad)
                                    logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")
                                    check_cantidad.delete()  # Eliminar el registro de la relación de productos con el pago
                                logger.info(f"Cantidad de producto devuelta: {producto.categoria.nombre}, nueva cantidad: {producto.cantidad}")
                            else:
                                if producto.cantidad < producto_data['cantidad']:
                                    logger.error(f"No hay suficiente cantidad del producto")
                                    raise ValidationError(f"No hay suficiente cantidad del producto: {producto.categoria.nombre}. Disponible: {producto.cantidad}, Solicitado: {producto_data['cantidad']}")
                                
                                # Actualizamos o creamos el PaymentProduct
                                check_cantidad = PaymentProduct.objects.get(payment=instance, producto=producto).cantidad
                                
                                if producto_data['cantidad'] != check_cantidad:
                                    PaymentProduct.objects.update(payment=instance, producto=producto, cantidad=producto_data['cantidad'])
                                    logger.info(f"Se actualizó la cantidad de pedidos al producto")
                                    Producto.objects.filter(id=producto.id).update(cantidad=F('cantidad') - producto_data['cantidad'])
                                    logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")
                                
                                producto.save()

                        else:
                            # Producto simple => CustomProduct
                            custom_product = CustomProduct.objects.update(
                                name=producto_data['name'],
                                color=producto_data.get('color'),
                                talle=producto_data.get('talle'),
                                precio=producto_data.get('precio', 0),
                                cantidad=producto_data.get('cantidad', 1)
                            )
                            instance.custom_products.add(custom_product)
                            logger.info(f"CustomProduct modificado para Payment {instance.payment_id}")
                

                    # Procesar combos
                    combo_data = validated_data.get('combo', [])
                    if combo_data and isinstance(combo_data, list):
                        for combo in combo_data:
                            combo_id = combo["id"]
                            combo_instance = Combo.objects.get(id=combo_id)
                            instance.combo.add(combo_instance)
                            logger.info(f"Combo añadido al pago: {combo_instance}")
                            productos = combo.get("productos", [])
                            # Restar cantidades de los productos dentro del combo
                            for producto_data in productos:
                                
                                categoria_data = producto_data.get('categoria')
                                marca_data = producto_data.get('marca')
                                color_data = producto_data.get('color')
                                talle_data = producto_data.get('talle')
                                categoria = Categoria.objects.get_or_create(id=categoria_data['id'], defaults={'nombre': categoria_data['nombre']})[0]
                                marca = Marca.objects.get_or_create(id=marca_data['id'], defaults={'nombre': marca_data['nombre']})[0] if marca_data else None
                                color = Color.objects.get_or_create(id=color_data['id'], defaults={'nombre': color_data['nombre']})[0]
                                talle = Talle.objects.get_or_create(nombre=talle_data['nombre'])[0]
                                producto = Producto.objects.get(categoria=categoria, marca=marca, color=color, talle=talle)
                                logger.info(f"Producto encontrado: {producto}")


                                # Si el estado cambió a "DEVUELTO", revertimos la cantidad
                                if previous_status != 'DEVUELTO' and instance.status == 'DEVUELTO':
                                    check_cantidad = PaymentProduct.objects.get(payment=instance, producto=producto)
                                    if check_cantidad:
                                        # Añadir la cantidad de productos devueltos
                                        producto.cantidad += check_cantidad.cantidad
                                        producto.save()
                                        check_cantidad.delete()  # Eliminar el registro de la relación de productos con el pago
                                    logger.info(f"Cantidad de producto devuelta: {producto.categoria.nombre}, nueva cantidad: {producto.cantidad}")
                                else:
                                    if producto.cantidad < combo['cantidad']:
                                        logger.error(f"No hay suficiente cantidad del producto")
                                        raise ValidationError(f"No hay suficiente cantidad del producto: {producto.categoria.nombre}. Disponible: {producto.cantidad}, Solicitado: {combo['cantidad']}")
                                    
                                    # Actualizamos o creamos el PaymentProduct
                                    check_cantidad = PaymentProduct.objects.get(payment=instance, producto=producto).cantidad
                                    
                                    if combo['cantidad'] != check_cantidad:
                                        PaymentProduct.objects.update(payment=instance, producto=producto, cantidad=combo['cantidad'])
                                        logger.info(f"Se actualizó la cantidad de pedidos al producto")
                                        producto.cantidad -= combo['cantidad']
                                    
                                    producto.save()

                    # Guardamos el objeto Payment actualizado
                    instance.save()
                    logger.info(f"Recibo modificado: {instance}")
                    serializer = self.get_serializer(instance)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"Error al validar el pago: {payment_serializer.errors}")
                    return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error al crear el pago: {str(e)}", exc_info=True)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
                
        return Response(
            {"detail": f"El recibo con ID {instance.payment_id} fue eliminado."},
            status=status.HTTP_200_OK,
        ) 
        
    @action(detail=False, methods=['post'], url_path='send-receipt-email')
    def send_receipt_email(self, request):
        # Obtener los datos del cuerpo de la solicitud
        data = request.data
        # Generar el PDF
        pdf_buffer = generate_invoice_pdf(data)
        # Enviar el correo
        email = EmailMessage( subject=f"Recibo de Pago #{data['payment_id']}", body="Adjuntamos su recibo en formato PDF.", from_email="conico.company@gmail.com", to=[data['client']['email']],)
        email.attach(f"recibo_{data['payment_id']}.pdf", pdf_buffer.read(), "application/pdf")
        email.send()

        return Response({"success": True, "message": "Recibo enviado correctamente."})
    
    @action(detail=False, methods=['post'], url_path='download-receipt')
    def download_receipt(self, request):
        data = request.data
        pdf_buffer = generate_invoice_pdf(data)

        # Asegúrate de que el contenido sea 'application/pdf'
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=recibo_{data["payment_id"]}.pdf'
        return response


    
