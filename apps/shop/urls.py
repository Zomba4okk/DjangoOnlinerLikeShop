from django.urls import (
    path,
    include,
)

from rest_framework import routers

from .views import (
    CartProductView,
    CategoryViewset,
    ProductViewset,
)


router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
router.register('categories', CategoryViewset, 'category')

urlpatterns = [
    path('', include(router.urls)),
]


cart_urls = [
    path('delta/', CartProductView.as_view()),
]
