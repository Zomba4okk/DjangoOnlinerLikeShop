from django_filters import (
    FilterSet,
    NumberFilter,
    CharFilter,
)
from django.forms.fields import IntegerField, CharField

from apps.base.filters import (
    MultipleValueFilter,
)


class ProductFilterSet(FilterSet):
    min_price = NumberFilter(
        field_name='price', lookup_expr='gte'
    )
    max_price = NumberFilter(
        field_name='price', lookup_expr='lte'
    )
    name = CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    category = MultipleValueFilter(
        field_class=CharField, field_name='category', lookup_expr='id__in'
    )


class CategoryFilterSet(FilterSet):
    name = CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    ancestor = NumberFilter(
        field_name='id', method='filter_descendants'
    )

    @staticmethod
    def filter_descendants(queryset, name, value):
        return queryset.filter(**{name: value}) \
            .get_descendants(include_self=False)


class UserFilterSet(FilterSet):
    user = MultipleValueFilter(
        field_class=IntegerField, field_name='user'
    )
