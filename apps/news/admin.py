from django.contrib import admin
from django.utils.html import (
    format_html,
)

from .models import (
    EditingHistoryEntry,
    News,
    NewsImage,
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
        return format_html('<img src="{url}"/>',
                           url=obj.image.url)


class NewsAdmin(admin.ModelAdmin):
    model = News
    inlines = (
        NewsImageInline,
        EditingHistoryEntryInline
    )


admin.site.register(News, NewsAdmin)
