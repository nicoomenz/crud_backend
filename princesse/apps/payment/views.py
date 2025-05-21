import json
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from payment.models import *
from payment.serializers import PaymentProductSerializer, PaymentSerializer, PaymentComboSerializer, PaymentUpdateSerializer
from payment.services import PaymentService
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

class PaymentProductViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = PaymentProductSerializer

    @action(detail=True, methods=['get'], url_path='price')
    def get_price(self, request, pk=None):
        try:
            
            # Buscar si existe un precio registrado en algún PaymentProduct
            payment_products = PaymentProduct.objects.filter(payment=pk)
            
            if not payment_products.exists():
                return Response([], status=status.HTTP_200_OK)
            
            products = [
                {   
                    'payment': pp.payment.payment_id,
                    'producto_id': pp.producto.id,
                    'precio_efectivo': pp.precio_efectivo,
                    'precio_debito': pp.precio_debito,
                    'precio_credito': pp.precio_credito,
                    'cantidad': pp.cantidad
                }
                for pp in payment_products
            ]

            return Response(products, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], url_path='combo_price')
    def get_combo_price(self, request, pk=None):
        try:
            
            # Buscar si existe un precio registrado en algún PaymentProduct
            payment_combo = PaymentCombo.objects.filter(payment=pk)
            
            if not payment_combo.exists():
                return Response([], status=status.HTTP_200_OK)
            
            combo = [
                {   
                    'payment': pc.payment.payment_id,
                    'combo_id': pc.combo.id,
                    'precio_efectivo': pc.precio_efectivo,
                    'precio_debito': pc.precio_debito,
                    'precio_credito': pc.precio_credito,
                    'cantidad': pc.cantidad
                }
                for pc in payment_combo
            ]

            return Response(combo, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response(
                {"detail": f"El producto con ID {instance.producto.id} fue eliminado."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": f"El producto con ID {instance.producto.id} ya fue eliminado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class CustomProductViewSet(viewsets.ModelViewSet):
    queryset = CustomProduct.objects.all()
    serializer_class = PaymentComboSerializer
    def get_queryset(self):
        # Retornar solo los usuarios activos
            return super().get_queryset().filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response(
                {"detail": f"El producto con ID {instance.id} fue eliminado."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": f"El producto con ID {instance.id} ya fue eliminado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                            precio_efectivo = producto_data['precio'].efectivo
                            precio_debito = producto_data['precio'].debito
                            precio_credito = producto_data['precio'].credito
                            PaymentProduct.objects.create(payment=payment, producto=producto, cantidad=producto_data['cantidad'],
                                                        precio_efectivo=precio_efectivo,
                                                        precio_debito=precio_debito,
                                                        precio_credito=precio_credito)
                            
                            logger.info(f"Producto añadido al pago: {producto} (cantidad: {producto_data['cantidad']})")

                            Producto.objects.filter(id=producto.id).update(cantidad=F('cantidad') - producto_data['cantidad'])
                            logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")

                            payment.productos.add(producto)
                        else:
                            # Producto simple => CustomProduct
                            custom_product = CustomProduct.objects.create(
                                payment=payment,
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
                            precio_efectivo = combo_instance.precio.efectivo
                            precio_debito = combo_instance.precio.debito
                            precio_credito = combo_instance.precio.credito
                            payment.combo.add(combo_instance)
                            PaymentCombo.objects.create(payment=payment, combo=combo_instance, cantidad=combo['cantidad'],
                                                        precio_efectivo=precio_efectivo,
                                                        precio_debito=precio_debito,
                                                        precio_credito=precio_credito)
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
                                
                                Producto.objects.filter(id=producto.id).update(cantidad=F('cantidad') - combo['cantidad'])
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
        instance = self.get_object()
        serializer = PaymentUpdateSerializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)  # Validamos y convertimos aquí
            validated_data = serializer.validated_data  # Datos limpios y con fechas en formato date

            service = PaymentService(instance, validated_data)
            updated_instance = service.process_update()
            logger.info(f"se modificó el recibo {instance} correctamente")

            # Serializamos la instancia actualizada para la respuesta
            response_serializer = PaymentUpdateSerializer(updated_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error al crear el pago: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'DEVUELTO':
            
            #si tengo productos borro productos, si tengo customproductos tambien
            #si tengo combos borro combos
            # Eliminar los productos asociados al recibo
            if instance.productos.exists():
                for producto in instance.productos.all():
                    # Aumentar la cantidad del producto
                    
                    producto.cantidad += PaymentProduct.objects.filter(payment=instance, producto=producto).first().cantidad
                    producto.save()
                    
                    #poner el paymentproduct en inactive llamando a la clase PaymentProduct
                    PaymentProduct.objects.filter(payment=instance, producto=producto).update(is_active=False)
                    logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")

            
            if instance.custom_products.exists():
                for custom_product in instance.custom_products.all():
                    # Aumentar la cantidad del producto
                    CustomProduct.objects.filter(payment=instance, id=custom_product.id).update(is_active=False)
                    logger.info(f"Cantidad actualizada para producto {custom_product.id}: {custom_product.cantidad}")

            if instance.combo.exists():
                for combo in instance.combo.all():
                    # Aumentar la cantidad del producto
                    
                    for producto in combo.productos.all():
                        producto.cantidad += PaymentCombo.objects.filter(payment=instance, combo=combo).first().cantidad
                        producto.save()
                        logger.info(f"Cantidad actualizada para producto {producto.id}: {producto.cantidad}")
                    PaymentCombo.objects.filter(payment=instance, combo=combo).update(is_active=False)
        
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
        if not data['payment_id'] or data['payment_id'] == 0:
            data['payment_id'] = Payment.objects.all().last().payment_id
        # Generar el PDF
        pdf_buffer = generate_invoice_pdf(data)
        # Enviar el correo
        email = EmailMessage( subject=f"Recibo de Pago #{data['payment_id']}", body="Adjuntamos su recibo en formato PDF.", from_email="princesse.altacostura@gmail.com", to=[data['client']['email']],)
        email.attach(f"recibo_{data['payment_id']}.pdf", pdf_buffer.read(), "application/pdf")
        email.send()

        return Response({"success": True, "message": "Recibo enviado correctamente."})
    
    @action(detail=False, methods=['post'], url_path='download-receipt')
    def download_receipt(self, request):
        data = request.data
        if not data['payment_id'] or data['payment_id'] == 0:
            data['payment_id'] = Payment.objects.all().last().payment_id
        pdf_buffer = generate_invoice_pdf(data)
        # Asegúrate de que el contenido sea 'application/pdf'
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=recibo_{data["payment_id"]}.pdf'
        return response