import re

from django.core.exceptions import ValidationError


def validate_phone_number(value):
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')  # The regex pattern to match valid phone numbers
    if not phone_regex.match(value):
        raise ValidationError(
            'Invalid phone number format. The number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )
