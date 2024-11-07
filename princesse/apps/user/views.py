from django.shortcuts import render

from user.models import ClientPayer
from user.serializers import ClientPayerSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
# Create your views here.

class ClientPayerViewSet(viewsets.ModelViewSet):

    serializer_class = ClientPayerSerializer
    queryset = ClientPayer.objects.all()
        