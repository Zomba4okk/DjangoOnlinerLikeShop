from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
)
from rest_framework.mixins import (
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
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
    UserFilterSet,
)
from .models import (
    CartProductM2M,
    Category,
    Order,
    OrderProductM2M,
    Product,
    ORDER_STATUS_INCOMPLETE,
    ORDER_STATUS_PAID,
    ORDER_STATUS_CLOSED,
)
from .serializers import (
    CartProductCountSerializer,
    CategorySerializer,
    OrderProductCountSerializer,
    OrderSerializer,
    OrderWithUserSerializer,
    ProductSerializer,
    UserOrdersSerializer,
)
from apps.base.permissions import (
    IsReadOnlyPermission,
)
from apps.base.mixins import (
    GetSerializerClassMixin,
)
from apps.user.models import (
    User,
)
from apps.user.permissions import (
    IsAdminPermission,
    IsModeratorPermission,
)


class ProductViewset(ModelViewSet):
    permission_classes = (
        IsReadOnlyPermission | IsAdminPermission | IsModeratorPermission,
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = ProductFilterSet

    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CategoryViewset(ModelViewSet):
    permission_classes = (
        IsReadOnlyPermission | IsAdminPermission | IsModeratorPermission,
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = CategoryFilterSet

    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CartProductView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        '''
        Accepts `[{"product": <product id>, "product_count": <int >= 0>} * n]`
        JSON.
        '''
        serializer = CartProductCountSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        cart = request.user.cart
        CartProductM2M.objects.filter(cart=cart).delete()

        cart_product_m2ms = (
            CartProductM2M(**cart_product_m2m_data, cart=cart)
            for cart_product_m2m_data
            in serializer.validated_data
            if cart_product_m2m_data.get('product_count') > 0
        )
        CartProductM2M.objects.bulk_create(cart_product_m2ms)

        return Response(status=HTTP_204_NO_CONTENT)

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
        queryset = CartProductM2M.objects \
            .filter(cart=request.user.cart) \
            .select_related('product')
        return Response(CartProductCountSerializer(queryset, many=True).data)


class CatrToOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):

        cart = request.user.cart
        cart_product_m2ms = CartProductM2M.objects \
            .filter(cart=cart) \
            .select_related('product')
        if cart_product_m2ms.exists():
            order = Order(user=request.user)
            order.save()

            order_product_m2ms = (
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


class ClearCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cart = request.user.cart
        cart.products.clear()
        return Response(status=HTTP_204_NO_CONTENT)


class OrderViewSet(ListModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   DestroyModelMixin,
                   GetSerializerClassMixin,
                   GenericViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = OrderSerializer
    serializer_action_classes = {
        'update': OrderProductCountSerializer,
        'partial_update': OrderProductCountSerializer,
    }
    queryset = Order.objects.all()

    def get_queryset(self):
        return super().get_queryset() \
            .filter(user=self.request.user) \
            .prefetch_related('orderproductm2m_set', 'products')

    def get_order_to_uptade(self):
        order = self.get_object()

        if order.status != ORDER_STATUS_INCOMPLETE:
            raise ValueError('Can only update INCOMPLETE orders')

        return order

    def update(self, request, *args, **kwargs):
        '''
        Accepts `[{"product": <product id>, "product_count": <int >= 0>} * n]`
        JSON.
        '''
        order = self.get_order_to_uptade()

        serializer = self.get_serializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        order.products.clear()

        order_product_m2ms = (
            OrderProductM2M(**order_product_m2m_data, order=order)
            for order_product_m2m_data
            in serializer.validated_data
            if order_product_m2m_data.get('product_count') > 0
        )
        OrderProductM2M.objects.bulk_create(order_product_m2ms)

        return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        '''
        Accepts `{"product": <product id>, "product_count": <int >= 0>}` JSON.
        '''
        order = self.get_order_to_uptade()

        serializer = self.get_serializer(data=request.data, many=False)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        new_product_count = serializer.validated_data['product_count']

        try:
            order_product_m2m = OrderProductM2M.objects.get(
                product=serializer.validated_data.get('product'),
                order=order
            )
            if new_product_count > 0:
                order_product_m2m.product_count = new_product_count
                order_product_m2m.save()
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                order_product_m2m.delete()
                return Response(status=HTTP_204_NO_CONTENT)

        except OrderProductM2M.DoesNotExist:
            if new_product_count > 0:
                OrderProductM2M(
                    **{'order': order, **serializer.validated_data}
                ).save()

            return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ORDER_STATUS_INCOMPLETE:
            self.perform_destroy(instance)
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)


class AdminUserOrderViewSet(ListModelMixin,
                            GenericViewSet):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    serializer_class = UserOrdersSerializer
    queryset = User.objects.prefetch_related(
        'orders__products', 'orders__orderproductm2m_set'
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = UserFilterSet


class AdminOrderViewSet(RetrieveModelMixin,
                        GenericViewSet):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    serializer_class = OrderWithUserSerializer
    queryset = Order.objects.prefetch_related(
        'user', 'orderproductm2m_set', 'products'
    )


class AdminCloseOrder(APIView):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    def get(self, request, order_id, *arge, **kwargs):
        order = Order.objects.get(id=order_id)
        if order.status == ORDER_STATUS_PAID:
            order.status = ORDER_STATUS_CLOSED
            order.save()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
