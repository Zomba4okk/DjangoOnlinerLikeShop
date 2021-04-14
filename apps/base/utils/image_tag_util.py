from django.utils.html import (
    format_html,
)
from django.utils.safestring import (
    SafeText,
)


class ImageTagUtil:

    @staticmethod
    def get_image_tag(image_url: str) -> SafeText:
        return format_html(f'<img src="{image_url}"/>')
