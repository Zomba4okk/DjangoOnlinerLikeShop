from rest_framework import routers

from .views import (
    ProductViewset,
)

router = routers.DefaultRouter()
router.register('products', ProductViewset, 'product')
