from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from product.filters import ProductsFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import NotFound
# Create your views here.

class ProductosViewSet(viewsets.ModelViewSet):

    serializer_class = ProductoSerializer
    queryset = Producto.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductsFilter

    def get_queryset(self):
    # Retornar solo los usuarios activos
        return super().get_queryset().filter(active=True)

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

    def update(self, request, *args, **kwargs):
        # Obtén la instancia actual
        instance = self.get_object()
        
        # Obtén los datos validados del request
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data

        # Extrae los datos necesarios
        categoria_id = validated_data.get("categoria")
        marca_id = validated_data.get("marca", None)
        efectivo = validated_data.get("efectivo")
        debito = validated_data.get("debito")
        credito = validated_data.get("credito")

        # Actualiza el precio en el modelo PrecioProducto si se proporcionan categoría y marca
        if categoria_id:
            try:
                PrecioProducto.actualizar_precio(
                    categoria_id=categoria_id,
                    marca_id=marca_id,
                    efectivo=efectivo,
                    debito=debito,
                    credito=credito,
                )
            except ValueError as e:
                # Lanza un error de validación si falla la lógica del modelo
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        # Actualiza los otros campos del producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Devuelve la respuesta con los datos actualizados
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save()

         # Eliminar el producto de los combos
        combos = Combo.objects.filter(productos=instance)
        for combo in combos:
            combo.productos.remove(instance)
            # Si el combo no tiene más productos, eliminarlo
            if not combo.productos.exists():
                combo.delete()

        return Response(
            {"detail": f"El producto con ID {instance.id} fue eliminado."},
            status=status.HTTP_200_OK,
        )
    
class ProductosAmountsViewSet(viewsets.ModelViewSet):
    serializer_class = PrecioProductoSerializer
    queryset = PrecioProducto.objects.all()

    def get_queryset(self):
        # Obtén los datos del cuerpo de la solicitud
        categoria = self.request.query_params.get('categoria', None)
        marca = self.request.query_params.get('marca', None)

        if not categoria:
            return PrecioProducto.objects.all()

        try:
            queryset = PrecioProducto.objects.get(categoria=categoria, marca=marca)
        except PrecioProducto.DoesNotExist:
            raise NotFound("No se encontraron productos con esos parámetros.")

        # Filtra los precios por marca si se proporciona
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Si el queryset es un solo objeto (no una lista), lo serializamos directamente
        if isinstance(queryset, PrecioProducto):
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)

        # Si el queryset es una lista y no hay resultados, devolvemos una lista vacía
        if not queryset.exists():
            return Response([], status=status.HTTP_200_OK)

        # Si hay resultados, serializamos y devolvemos la respuesta
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class CombosAmountsViewSet(viewsets.ModelViewSet):
    serializer_class = PrecioComboSerializer
    queryset = PrecioCombo.objects.all()

    def get_queryset(self):
        # Obtén los datos del cuerpo de la solicitud
        marca = self.request.query_params.get('marca', None)

        if not marca:
                return PrecioCombo.objects.all()

        try:
            queryset = PrecioCombo.objects.get(marca=marca)
        except PrecioCombo.DoesNotExist:
            raise NotFound("No se encontraron productos con esos parámetros.")

        # Filtra los precios por marca si se proporciona
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Si el queryset es un solo objeto (no una lista), lo serializamos directamente
        if isinstance(queryset, PrecioCombo):
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)

        # Si el queryset es una lista y no hay resultados, devolvemos una lista vacía
        if not queryset.exists():
            return Response([], status=status.HTTP_200_OK)

        # Si hay resultados, serializamos y devolvemos la respuesta
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CombosViewSet(viewsets.ModelViewSet):
    
        serializer_class = ComboSerializer
        queryset = Combo.objects.all()
        def get_queryset(self):
        # Retornar solo los usuarios activos
            return super().get_queryset().filter(active=True)

        def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Crear los productos
            combo = serializer.save()
            
            # Serializar y devolver la lista de productos creados
            response_data = ComboSerializer(combo).data
            return Response(response_data, status=status.HTTP_201_CREATED)

        def update(self, request, *args, **kwargs):
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Crear los productos
            combo = serializer.save()
            
            # Serializar y devolver la lista de productos creados
            response_data = ComboSerializer(combo).data
            return Response(response_data, status=status.HTTP_200_OK)
        
        def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            instance.active = False
            instance.save()
                    
            return Response(
                {"detail": f"El combo con ID {instance.id} fue eliminado."},
                status=status.HTTP_200_OK,
        )

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