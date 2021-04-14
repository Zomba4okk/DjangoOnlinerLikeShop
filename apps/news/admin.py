from django.contrib import admin

from .models import (
    News,
    NewsImage,
)
from apps.base.utils import (
    ImageTagUtil,
)


class NewsImageInline(admin.StackedInline):
    model = NewsImage
    fields = ('image', 'image_tag',)
    readonly_fields = ('image_tag',)
    extra = 1

    def image_tag(self, obj):
        return ImageTagUtil.get_image_tag(obj.image.url, "500", "300")


class NewsAdmin(admin.ModelAdmin):
    model = News
    fields = ('title', 'description', 'content', 'main_image',
              'main_image_tag')
    readonly_fields = ('main_image_tag',)
    inlines = (
        NewsImageInline,
    )

    def main_image_tag(self, obj):
        return ImageTagUtil.get_image_tag(obj.main_image.url)


admin.site.register(News, NewsAdmin)
