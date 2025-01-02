from user.filter import ClientsFilter
from user.utils import get_output_data
from user.models import ClientPayer
from user.serializers import ClientPayerSerializer, LoginSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Usamos el LoginSerializer para validar y autenticar los datos
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            # El serializer ya retorna el usuario autenticado
            validated_data = serializer.validated_data
            
            # Creamos la sesión
            login(request, validated_data['user'])
            user_data = {
                "id": validated_data['user'].id,
                "username": validated_data['user'].username,
                "password": validated_data['password'],
                "email": validated_data['user'].email,
            }
            return Response(get_output_data(user_data), status=status.HTTP_200_OK)
        # Si el serializer no es válido, se devuelven los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    
    def post(self, request):
        try:
            logout(request)
            return Response({"detail": "Logout exitoso"})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ClientPayerViewSet(viewsets.ModelViewSet):

    serializer_class = ClientPayerSerializer
    queryset = ClientPayer.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientsFilter

    
