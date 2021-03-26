from rest_framework import viewsets

from django_filters import rest_framework as rf_filters

from .filters import (
    CategoryFilterSet,
    ProductFilterSet,
)
from .models import (
    Category,
    Product,
)
from ..base.permissions import (
    IsReadOnlyPermission,
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
)
from ..user.permissions import (
    IsAdminPermission,
    IsModeratorPermission,
)


class ProductViewset(viewsets.ModelViewSet):
    permission_classes = (
        IsReadOnlyPermission | IsAdminPermission | IsModeratorPermission,
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = ProductFilterSet

    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CategoryViewset(viewsets.ModelViewSet):
    permission_classes = (
        IsReadOnlyPermission | IsAdminPermission | IsModeratorPermission,
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = CategoryFilterSet

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
