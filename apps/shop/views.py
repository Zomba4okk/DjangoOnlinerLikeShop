from django.shortcuts import (
    get_object_or_404,
)

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
    ORDER_STATUS_PAID,
    ORDER_STATUS_CLOSED,
)
from .permissions import (
    CanChangeOrderPermission,
    IsOwnerPermission,
)
from .serializers import (
    CategorySerializer,
    OrderSerializer,
    ProductCountSerializer,
    ProductSerializer,
)
from .utils import (
    DeltaUtil,
)
from apps.base.permissions import (
    IsReadOnlyPermission,
)
from apps.base.mixins import (
    GetSerializerClassMixin,
)
from apps.user.models import (
    ACCOUNT_TYPE_STANDARD,
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


class CartProductsView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        """
        Accepts `{"product_id": <<int>>, "product_count": <<int != 0>>}`
        """
        serializer = ProductCountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            DeltaUtil.smart_delta(
                CartProductM2M,
                {
                    'cart': request.user.cart,
                    'product': get_object_or_404(
                        Product, id=serializer.validated_data['product_id']
                    )
                    # Product.objects.get(
                    #     id=serializer.validated_data['product_id']
                    # )
                },
                'product_count',
                serializer.validated_data['product_count']
            )
        except AttributeError:
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)

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
    permission_classes = (
        IsAuthenticated,
        IsReadOnlyPermission | (IsOwnerPermission & CanChangeOrderPermission),
    )

    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = UserFilterSet

    serializer_class = OrderSerializer
    serializer_action_classes = {
        'partial_update': ProductCountSerializer,
        'create': ProductCountSerializer,
    }
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        # instead of non-existant list object permission
        if self.request.user.account_type == ACCOUNT_TYPE_STANDARD:
            queryset = queryset.filter(user=self.request.user)

        queryset = queryset.prefetch_related(
            'product_relations', 'products', 'user'
        )

        return queryset

    def partial_update(self, request, *args, **kwargs):
        """
        Accepts `{"product_id": <<int>>, "product_count": <<int != 0>>}`
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST)

        try:
            DeltaUtil.smart_delta(
                OrderProductM2M,
                {
                    'order': self.get_object(),
                    'product': get_object_or_404(
                        Product, id=serializer.validated_data['product_id']
                    )
                    # Product.objects.get(
                    #     id=serializer.validated_data['product_id']
                    # )
                },
                'product_count',
                serializer.validated_data['product_count']
            )
        except AttributeError:
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)


class AdminCloseOrderView(APIView):
    permission_classes = (IsModeratorPermission | IsAdminPermission,)

    def patch(self, request, order_id, *arge, **kwargs):
        order = Order.objects.get(id=order_id)
        if order.status == ORDER_STATUS_PAID:
            order.status = ORDER_STATUS_CLOSED
            order.save(update_fields=('status',))
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
