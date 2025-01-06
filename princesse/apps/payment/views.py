import json
from django.shortcuts import render
from payment.models import *
from payment.serializers import PaymentSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

from django.http import JsonResponse
from django.core.mail import EmailMessage
from rest_framework.decorators import action

from payment.utils import generate_invoice_pdf
# Create your views here.

class PaymentsViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)  # Esto llama a `validate`
    #     return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], url_path='send-receipt-email')
    def send_receipt_email(self, request):
        # Obtener los datos del cuerpo de la solicitud
        data = request.data
        # Generar el PDF
        pdf_buffer = generate_invoice_pdf(data)

        # Enviar el correo
        email = EmailMessage( subject=f"Recibo de Pago #{data['payment_id']}", body="Adjuntamos su recibo en formato PDF.", from_email="nicoomenz@gmail.com", to=[data['client']['email']],)
        email.attach(f"recibo_{data['payment_id']}.pdf", pdf_buffer.read(), "application/pdf")
        email.send()

        return Response({"success": True, "message": "Recibo enviado correctamente."})
