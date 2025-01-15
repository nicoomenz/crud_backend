import django_filters
from product.models import *

class ProductsFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter(field_name='categoria')
    marca = django_filters.CharFilter(field_name='marca')

    class Meta:
        model = Producto
        fields = []