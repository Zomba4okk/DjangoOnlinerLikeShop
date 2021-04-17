from django.utils.html import (
    format_html,
)
from django.utils.safestring import (
    SafeText,
)


class ImageTagUtil:

    @staticmethod
    def get_image_tag(image_url: str,
                      width: str = "auto", height: str = "auto") -> SafeText:
        if width.isdigit():
            width += "px"
        if height.isdigit():
            height += "px"

        return format_html(
            f'<img src="{image_url}" width="{width}" height="{height}"/>'
        )
