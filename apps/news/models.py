from django.db import models

from tinymce import (
    HTMLField,
)

from apps.user.models import (
    User,
)


class News(models.Model):
    class Meta:
        verbose_name_plural = 'news'

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    content = HTMLField()
    main_image = models.ImageField(upload_to='news_images/')


class NewsImage(models.Model):
    news = models.ForeignKey(to=News, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_images/')


class EditingHistoryEntry(models.Model):
    news = models.ForeignKey(to=News, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    editor = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
