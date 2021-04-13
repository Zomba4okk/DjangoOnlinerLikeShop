from django_filters.filters import (
    Filter,
)

from .fields import (
    MultipleValueField,
)


class MultipleValueFilter(Filter):
    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        kwargs.setdefault('lookup_expr', 'in')
        super().__init__(*args, field_class=field_class, **kwargs)
