from django.shortcuts import render
from product.models import *
from product.serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
# Create your views here.

class ProductosViewSet(viewsets.ModelViewSet):

    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Crear los productos
        productos = serializer.save()
        
        # Serializar y devolver la lista de productos creados
        response_data = ProductoSerializer(productos, many=True).data
        return Response(response_data, status=status.HTTP_201_CREATED)

class CategoriasViewSet(viewsets.ModelViewSet):

    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()

class MarcasViewSet(viewsets.ModelViewSet):

    serializer_class = MarcaSerializer
    queryset = Marca.objects.all()

class ColoresViewSet(viewsets.ModelViewSet):
    
        serializer_class = ColorSerializer
        queryset = Color.objects.all()

class TallesViewSet(viewsets.ModelViewSet):
    
        serializer_class = TalleSerializer
        queryset = Talle.objects.all() 

class CombosViewSet(viewsets.ModelViewSet):
    
        serializer_class = ComboSerializer
        queryset = Combo.objects.all()
        