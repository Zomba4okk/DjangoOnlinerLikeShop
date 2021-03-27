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
    ProductCountSerializer,
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


class CartProductSetCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = ProductCountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        cart = request.user.cart
        product = Product.objects.get(id=serializer.data['product_id'])
        new_product_count = serializer.data['product_count']

        if product not in cart.products.all():
            if new_product_count != 0:
                CartProductM2M.objects.create(
                    cart=cart,
                    product=product,
                    product_count=new_product_count
                )
                return Response(status=HTTP_204_NO_CONTENT)

            return Response(status=HTTP_400_BAD_REQUEST)

        else:
            cart_product_m2m = CartProductM2M.objects \
                .get(cart=cart, product=product)

            if new_product_count == 0:
                cart_product_m2m.delete()
            else:
                cart_product_m2m.product_count = new_product_count
                cart_product_m2m.save()

            return Response(status=HTTP_204_NO_CONTENT)
