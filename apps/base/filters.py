from django_filters.filters import (
    MultipleChoiceFilter,
)

from .fields import (
    MultipleField,
)


class MultipleFilter(MultipleChoiceFilter):
    field_class = MultipleField
