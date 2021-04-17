from rest_framework.viewsets import (
    ModelViewSet
)

from django_filters import (
    rest_framework as rf_filters,
)

from .filters import (
    NewsSearchFilterSet,
)
from .models import (
    News,
)
from .serializers import (
    NewsDetailSerializer,
    NewsListSerializer,
)
from apps.base.permissions import (
    IsReadOnlyPermission,
)
from apps.base.mixins import (
    GetSerializerClassMixin,
)
from apps.user.permissions import (
    IsAdminPermission,
    IsModeratorPermission,
)


class NewsViewSet(GetSerializerClassMixin, ModelViewSet):
    permission_classes = (
        IsReadOnlyPermission | IsAdminPermission | IsModeratorPermission,
    )

    filter_backends = (rf_filters.DjangoFilterBackend,)
    filterset_class = NewsSearchFilterSet

    serializer_class = NewsDetailSerializer
    serializer_action_classes = {
        'list': NewsListSerializer,
    }

    queryset = News.objects.all()
