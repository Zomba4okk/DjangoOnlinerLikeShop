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


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    subcategories = django_filters.NumberFilter(
        field_name='id', method='descendants'
    )

    def descendants(self, queryset, name, value):
        return queryset.filter(**{name: value}) \
            .get_descendants(include_self=False)
