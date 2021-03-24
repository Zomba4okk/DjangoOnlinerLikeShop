from rest_framework import viewsets

from django_filters import rest_framework as rf_filters

from .filters import (
    CategoryFilter,
    ProductFilter,
)
from .models import (
    Category,
    Product,
)
from ..base.permissions import (
    IsReadOnly,
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
)
from ..user.permissions import (
    IsAdmin,
    IsModerator,
)


class ProductViewset(viewsets.ModelViewSet):
    permission_classes = (IsReadOnly | IsAdmin | IsModerator,)
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CategoryViewset(viewsets.ModelViewSet):
    permission_classes = (IsReadOnly | IsAdmin | IsModerator,)
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = CategoryFilter

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
