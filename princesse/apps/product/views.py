from django.shortcuts import render
from product.models import *
from product.serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    
    @action(detail=False, methods=['get'])
    def agrupados(self, request):
        productos = Producto.objects.prefetch_related('talle', 'color', 'categoria', 'marca', 'tela')
        
        # Agrupa los productos por categorías, colores y talles
        agrupados = {}
        for producto in productos:
            key = (producto.categoria, producto.marca)
            if key not in agrupados:
                agrupados[key] = {
                    'productos': [],
                    'precio': producto.precio,
                    'tela': producto.tela,
                }
            agrupados[key]['productos'].append({
            'id': producto.id,
            'producto': producto
        })

        # Serializa la respuesta
        data = [
            ProductoCompactoSerializer({
                'categoria': key[0],
                'marca': key[1],
                'productos': value['productos'],
                'precio': value['precio'],
                'tela': value['tela'],
            }).data
            for key, value in agrupados.items()
        ]
        return Response(data, status=status.HTTP_200_OK)

class ProductosAmountsViewSet(viewsets.ModelViewSet):
    serializer_class = PrecioSerializer
    queryset =  Precio.objects.all()

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
        