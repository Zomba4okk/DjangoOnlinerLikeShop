from django.contrib.admin.models import (
    LogEntry,
)

from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
)

from .models import (
    News,
    NewsImage,
)


class NewsImageSerializer(ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ('image',)


class LogEntrySerializer(ModelSerializer):
    class Meta:
        model = LogEntry
        fields = ('action_time', 'user', 'change_message')


class NewsDetailSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = (
            'news_id', 'title', 'description', 'main_image', 'images',
            'edit_logs'
        )

    news_id = IntegerField(source='id')
    images = NewsImageSerializer(many=True)
    edit_logs = LogEntrySerializer(many=True, read_only=True)


class NewsListSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = (
            'news_id', 'title', 'description', 'main_image',
        )

    news_id = IntegerField(source='id')
