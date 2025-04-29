import re

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext_lazy as _


def validate_category_image_dimensions(image):
    max_width = 99999
    max_height = 99999

    if image:
        width, height = get_image_dimensions(image.file)

        if width > max_width or height > max_height:
            raise ValidationError(_(f"image dimensions should not exceed w{max_width} x h{max_height} pixels"))


def validate_phone_number(value, **kwargs):
    phone_regex = re.compile(r"^\+?1?\d{9,15}$")
    if not phone_regex.match(value):
        raise ValidationError(_("invalid phone number format"))
