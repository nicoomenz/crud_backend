import django_filters
from django.db.models import Q
from user.models import *

class ClientsFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_search')

    class Meta:
        model = ClientPayer
        fields = []

    def filter_by_search(self, queryset, name, value):
        """
        Filtra por nombre (first_name) o apellido (last_name).
        El valor de búsqueda puede coincidir parcialmente (icontains).
        """
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(dni__icontains=value)
        )