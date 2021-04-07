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


router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
router.register('categories', CategoryViewset, 'category')
router.register('orders', OrderViewSet, 'order')


urlpatterns = [
    path('orders/make_from_cart/', CartToOrderView.as_view()),
    path('orders/<int:order_id>/close/', AdminCloseOrderView.as_view()),

    path('cart/products/', CartProductsView.as_view()),
    path('cart/clear/', ClearCartView.as_view()),

    path('', include(router.urls)),
]
