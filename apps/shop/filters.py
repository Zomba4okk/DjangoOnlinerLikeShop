from django_filters import (
    FilterSet,
    NumberFilter,
    CharFilter,
)

from ..base.filters import (
    MultipleFilter,
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
    category = MultipleFilter(
        field_name='category', lookup_expr='id__in'
    )


class CategoryFilterSet(FilterSet):
    name = CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    ancestor = NumberFilter(
        field_name='id', method='filter_descendants'
    )

    def filter_descendants(self, queryset, name, value):
        return queryset.filter(**{name: value}) \
            .get_descendants(include_self=False)
