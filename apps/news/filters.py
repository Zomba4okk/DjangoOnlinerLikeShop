from django.db.models import (
    Q,
)

from django_filters import (
    FilterSet,
)
from django_filters.filters import (
    CharFilter,
)


class NewsSearchFilterSet(FilterSet):
    search = CharFilter(
        method='perform_search'
    )

    @staticmethod
    def perform_search(queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
