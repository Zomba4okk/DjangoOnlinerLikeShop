from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)

from django_filters import rest_framework as rf_filters

from .filters import (
    ProductFilter,
)
from .models import (
    Product,
)
from .serializers import (
    ProductSerializer
)


class ProductViewset(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
