from django.urls import (
    path,
    include,
)

from rest_framework import routers

from .views import (
    CartProductView,
    CategoryViewset,
    CatrToOrderView,
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

order_urls = [
    path('make_from_cart/', CatrToOrderView.as_view())
]
