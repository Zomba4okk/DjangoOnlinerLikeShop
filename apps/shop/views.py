from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.views import APIView


from django_filters import rest_framework as rf_filters

from .filters import (
    CategoryFilterSet,
    ProductFilterSet,
)
from .models import (
    Category,
    Product,
    CartProductM2M,
)
from ..base.permissions import (
    IsReadOnlyPermission,
)
from .serializers import (
    CategorySerializer,
    ProductCountDeltaSerializer,
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


class CartProductView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = ProductCountDeltaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        cart = request.user.cart
        product = Product.objects.get(id=serializer.data['product_id'])
        product_count_deleta = serializer.data['count']

        if product in cart.products.all():
            cart_product_m2m = CartProductM2M.objects \
                .get(cart=cart, product=product)

            if product_count_deleta < 0 and \
                    cart_product_m2m.product_count < abs(product_count_deleta):
                return Response(status=HTTP_400_BAD_REQUEST)

            cart_product_m2m.product_count += product_count_deleta
            cart_product_m2m.delete() \
                if cart_product_m2m.product_count <= 0 \
                else cart_product_m2m.save()

            return Response(status=HTTP_204_NO_CONTENT)

        elif product_count_deleta > 0:
            CartProductM2M.objects.create(
                cart=cart, product=product, product_count=product_count_deleta
            )

            return Response(status=HTTP_204_NO_CONTENT)

        elif product_count_deleta < 0:
            return Response(status=HTTP_400_BAD_REQUEST)
