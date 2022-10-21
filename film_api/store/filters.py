from django_filters.rest_framework import FilterSet
from .models import Equipment


class EquipmentFilter(FilterSet):
    class Meta:
        model = Equipment
        fields = {
            'category_id': ['exact'],
            # 'unit_price': ['gt', 'lt']
        }
