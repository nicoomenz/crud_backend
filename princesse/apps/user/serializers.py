from django.contrib.auth import authenticate
from user.models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone']

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')

        # Busca el usuario por nombre de usuario o correo electrónico
        user = User.objects.filter(username=username_or_email).first()
        if not user:
            user = User.objects.filter(email=username_or_email).first()

        # Autenticación del usuario
        if user and user.is_active and authenticate(username=user.username, password=password):
            return {
                "user": user,
                "username_or_email": username_or_email,
                "password": password
        }
        raise serializers.ValidationError('Incorrect Credentials Passed.')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','phone','email','collector','role','is_active']

    def update(self, instance, validated_data):
        """
        Update and return an existing user instance.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
    
class ClientPayerDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    dni = serializers.CharField(max_length=10)
    cuit = serializers.CharField(max_length=15, default="", required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    direccion = serializers.CharField(max_length=100, default="")
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(max_length=25, allow_blank=True, allow_null=True)
    iva = serializers.ChoiceField(choices=[
        ('RESPONSABLE_INSCRIPTO', 'RESPONSABLE INSCRIPTO'),
        ('NO_RESPONSABLE', 'NO RESPONSABLE'),
        ('MONOTRIBUTISTA', 'MONOTRIBUTISTA'),
        ('EXENTO', 'EXENTO'),
        ('CONSUMIDOR_FINAL', 'CONSUMIDOR FINAL')
    ], required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        client_id = validated_data.get('id')
        if client_id:
            try:
                instance = ClientPayer.objects.get(id=client_id)
                return instance
            except ClientPayer.DoesNotExist:
                pass
        return ClientPayer.objects.create(**validated_data)

class ClientPayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientPayer
        fields = '__all__'