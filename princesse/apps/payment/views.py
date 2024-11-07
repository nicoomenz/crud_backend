from django.shortcuts import render
from payment.models import *
from payment.serializers import PaymentSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
# Create your views here.

class PaymentsViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
        