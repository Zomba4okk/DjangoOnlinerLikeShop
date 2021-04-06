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
    HTTP_404_NOT_FOUND,
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
    CategorySerializer,
    OrderSerializer,
    ProductCountSerializer,
    ProductSerializer,
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

    def patch(self, request, *args, **kwargs):
        """
        Accepts `{"product_id": <<int>>, "product_count": <<int != 0>>}`
        """
        serializer = ProductCountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        product_count_delta = serializer.validated_data['product_count']
        if product_count_delta == 0:
            return Response(status=HTTP_400_BAD_REQUEST)

        ###########

        try:
            product = Product.objects.get(
                id=serializer.validated_data['product_id']
            )
        except Product.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

        ###########

        cart = request.user.cart
        try:
            cart_product_m2m = cart.product_relations.get(product=product)
            cart_product_m2m.product_count += product_count_delta

            if cart_product_m2m.product_count < 0:
                return Response(status=HTTP_400_BAD_REQUEST)

            elif cart_product_m2m.product_count > 0:
                cart_product_m2m.save(update_fields=('product_count',))

            elif cart_product_m2m.product_count == 0:
                cart_product_m2m.delete()

            return Response(status=HTTP_204_NO_CONTENT)

        except CartProductM2M.DoesNotExist:
            if product_count_delta > 0:
                cart.product_relations.create(
                    product=product, product_count=product_count_delta
                )
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                return Response(status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Returns `[{"product_id": <<int>>, "product_count": <<int > 0>>} * n]`
        """
        queryset = CartProductM2M.objects \
            .filter(cart=request.user.cart) \
            .select_related('product')
        return Response(ProductCountSerializer(queryset, many=True).data)


class CartToOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Creates a new Order belonging to the current User, with products and
        product counts copied from User's Cart; Clears User's Cart.
        """
        cart_product_m2ms = request.user.cart.product_relations \
            .select_related('product').all()
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

    def put(self, request, *args, **kwargs):
        """
        Clears current User's Cart
        """
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
    # serializer_action_classes = {
    #     'update': OrderProductCountSerializer,
    #     'partial_update': OrderProductCountSerializer,
    # }
    queryset = Order.objects.all()

    def get_queryset(self):
        return super().get_queryset() \
            .filter(user=self.request.user) \
            .prefetch_related('product_relations', 'products', 'user')

    def get_order_to_update(self):
        order = self.get_object()

        if order.status != ORDER_STATUS_INCOMPLETE:
            raise ValueError('Can only update INCOMPLETE orders')

        return order

    def update(self, request, *args, **kwargs):
        '''
        Accepts `[{"product": <product id>, "product_count": <int >= 0>} * n]`
        JSON.
        '''
        order = self.get_order_to_update()

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
        order = self.get_order_to_update()

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

    # serializer_class = UserOrdersSerializer
    queryset = User.objects.prefetch_related(
        'orders__products', 'orders__orderproductm2m_set'
    )
    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = UserFilterSet


class AdminOrderViewSet(RetrieveModelMixin,
                        GenericViewSet):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    # serializer_class = OrderWithUserSerializer
    queryset = Order.objects.prefetch_related(
        'user', 'orderproductm2m_set', 'products'
    )


class AdminCloseOrder(APIView):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    def patch(self, request, order_id, *arge, **kwargs):
        order = Order.objects.get(id=order_id)
        if order.status == ORDER_STATUS_PAID:
            order.status = ORDER_STATUS_CLOSED
            order.save()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
