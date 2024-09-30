from user.models import *
from rest_framework import serializers

class ClientPayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientPayer
        fields = '__all__'