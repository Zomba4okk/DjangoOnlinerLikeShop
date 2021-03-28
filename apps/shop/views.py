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
    OrderProductM2M,
    Order,
)
from ..base.permissions import (
    IsReadOnlyPermission,
)
from .serializers import (
    CategorySerializer,
    CartProductCountSerializer,
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
        '''
        Accepts `{"product": <product id>, "product_count": <int >= 0>}` JSON,
        gets current user's cart.

        if relation cart-product exists:
            if product_count > 0:
                set cart.product_count = product_count
            if product_count == 0:
                delete relation cart-product
        else:
            if product_count > 0:
                create cart-product relation, set it's product_count
        '''

        serializer = CartProductCountSerializer(data=request.data)
        if not serializer.is_valid():
            print('invalid')
            return Response(status=HTTP_400_BAD_REQUEST)

        cart = request.user.cart
        new_product_count = serializer.validated_data['product_count']

        try:
            cart_product_m2m = CartProductM2M.objects.get(
                product=serializer.validated_data.get('product'),
                cart=cart
            )
            if new_product_count > 0:
                cart_product_m2m.product_count = new_product_count
                cart_product_m2m.save()
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                cart_product_m2m.delete()
                return Response(status=HTTP_204_NO_CONTENT)

        except CartProductM2M.DoesNotExist:
            if new_product_count > 0:
                CartProductM2M(
                    **{'cart': cart, **serializer.validated_data}
                ).save()

            return Response(status=HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        return Response(
            CartProductCountSerializer(
                CartProductM2M.objects.filter(cart=request.user.cart),
                many=True
            ).data
        )


class CatrToOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        cart = request.user.cart
        cart_product_m2ms = CartProductM2M.objects.filter(cart=cart)
        if cart_product_m2ms.exists():
            order = Order(user=request.user)
            order.save()

            order_product_m2ms = tuple(
                OrderProductM2M(
                    order=order,
                    product=cart_product_m2m.product,
                    product_count=cart_product_m2m.product_count
                )
                for cart_product_m2m
                in cart_product_m2ms
            )
            OrderProductM2M.objects.bulk_create(order_product_m2ms)

            cart_product_m2ms.delete()

            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
