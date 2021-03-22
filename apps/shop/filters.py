import django_filters


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte'
    )
    max_price = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte'
    )
    category = django_filters.CharFilter(
        field_name='category', lookup_expr='name__exact'
    )
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
