from rest_framework import routers

from .views import (
    CategoryViewset,
    ProductViewset,
)

router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
router.register('categories', CategoryViewset, 'category')
