from django.shortcuts import render

from user.models import ClientPayer
from user.serializers import ClientPayerSerializer

# Create your views here.

class ClientPayerViewSet():

    serializer_class = ClientPayerSerializer
    queryset = ClientPayer.objects.all()