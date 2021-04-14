from django.contrib import admin

from .models import (
    EditingHistoryEntry,
    News,
    NewsImage,
)
from apps.base.utils import (
    ImageTagUtil,
)


class EditingHistoryEntryInline(admin.TabularInline):
    model = EditingHistoryEntry
    readonly_fields = ('date_time', 'editor')
    extra = 0

    def has_add_permission(*args, **kwargs) -> bool:
        return False

    def has_delete_permission(*args, **kwargs) -> bool:
        return False

    def has_change_permission(*args, **kwargs) -> bool:
        return False


class NewsImageInline(admin.StackedInline):
    model = NewsImage
    fields = ('image', 'image_tag',)
    readonly_fields = ('image_tag',)
    extra = 1

    def image_tag(self, obj):
        return ImageTagUtil.get_image_tag(obj.image.url)


class NewsAdmin(admin.ModelAdmin):
    model = News
    fields = ('title', 'description', 'content', 'main_image',
              'main_image_tag')
    readonly_fields = ('main_image_tag',)
    inlines = (
        NewsImageInline,
        EditingHistoryEntryInline
    )

    def main_image_tag(self, obj):
        return ImageTagUtil.get_image_tag(obj.main_image.url)


admin.site.register(News, NewsAdmin)
