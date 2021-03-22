from rest_framework import viewsets

from django_filters import rest_framework as rf_filters

from .filters import (
    ProductFilter,
)
from .models import (
    Product,
)
from .permissions import (
    IsReadOnly,
)
from .serializers import (
    ProductSerializer
)


class ProductViewset(viewsets.ModelViewSet):
    permission_classes = (IsReadOnly,)
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
