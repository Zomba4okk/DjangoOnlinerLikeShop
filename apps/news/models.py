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

    def __str__(self):
        return f'News article: {self.title}'


class NewsImage(models.Model):
    news = models.ForeignKey(
        to=News, on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='news_images/')


class EditingHistoryEntry(models.Model):
    class Meta:
        verbose_name_plural = 'editing history entries'

    news = models.ForeignKey(
        to=News, on_delete=models.CASCADE,
        related_name='editing_history_enteries'
    )
    date_time = models.DateTimeField()
    editor = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True,
        related_name='news_edits'
    )

    def __str__(self):
        return f'Edited by {self.editor.email} at ' + \
               f'{self.date_time.__format__("%H:%M %d.%m.%Y")}'
