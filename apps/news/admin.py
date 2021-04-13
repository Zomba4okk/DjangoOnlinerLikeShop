from django.contrib import admin

from .models import (  # noqa
    News,
    EditingHistoryEntry,
)


class NewsAdmin(admin.ModelAdmin):
    model = News


admin.site.register(News)
