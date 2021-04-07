from django.urls import (
    path,
    include,
)

from rest_framework import (
    routers,
)

from .views import (
    AdminCloseOrderView,
    CartProductsView,
    CategoryViewset,
    CartToOrderView,
    ClearCartView,
    OrderViewSet,
    ProductViewset,
)


app_prefix = 'shop/'
cart_prefix = 'users/current/cart/'
orders_prefix = 'shop/orders/'

router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
router.register('categories', CategoryViewset, 'category')

order_router = routers.DefaultRouter()
order_router.register('', OrderViewSet, 'order')

urlpatterns = [
    path(app_prefix + '', include(router.urls)),
    path(app_prefix + 'orders/<int:order_id>/close/', AdminCloseOrderView.as_view()),  # noqa

    path(cart_prefix + 'products/', CartProductsView.as_view()),
    path(cart_prefix + 'clear/', ClearCartView.as_view()),

    path(orders_prefix + 'make_from_cart/', CartToOrderView.as_view()),
    path(orders_prefix, include(order_router.urls)),
]
