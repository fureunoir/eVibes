import re

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def validate_category_image_dimensions(image):
    max_width = 99999
    max_height = 99999

    if image:
        width, height = get_image_dimensions(image.file)

        if width > max_width or height > max_height:
            raise ValidationError("Image dimensions (width, height) should be at most 300x500 pixels.")


def validate_phone_number(value, **kwargs):
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            'Invalid phone number format. The number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )
