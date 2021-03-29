from django.urls import (
    path,
    include,
)

from rest_framework import routers

from .views import (
    CartProductView,
    CategoryViewset,
    CatrToOrderView,
    OrderViewSet,
    ProductViewset,
)


router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
router.register('categories', CategoryViewset, 'category')

urlpatterns = [
    path('', include(router.urls)),
]


cart_urls = [
    path('products/', CartProductView.as_view()),
]


order_router = routers.DefaultRouter()
order_router.register('', OrderViewSet, 'order')

order_urls = [
    path('make_from_cart/', CatrToOrderView.as_view()),
    path('', include(order_router.urls)),
]
