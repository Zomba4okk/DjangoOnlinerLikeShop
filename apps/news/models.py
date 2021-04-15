from django.contrib.admin.models import (
    LogEntry,
)
from django.contrib.contenttypes.fields import (
    GenericRelation,
)
from django.db import (
    models,
)

from tinymce import (
    HTMLField,
)


class News(models.Model):
    class Meta:
        verbose_name_plural = 'news'

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    content = HTMLField()
    main_image = models.ImageField(
        upload_to='news_images/', null=True, blank=True
    )
    edit_logs = GenericRelation(LogEntry)

    def __str__(self):
        return f'News article: {self.title}'


class NewsImage(models.Model):
    news = models.ForeignKey(
        to=News, on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='news_images/')
