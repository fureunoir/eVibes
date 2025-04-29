import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    phone_regex = re.compile(r"^\+?1?\d{9,15}$")  # The regex pattern to match valid phone numbers
    if not phone_regex.match(value):
        raise ValidationError(
            _(
                "invalid phone number format."
                ' the number must be entered in the format: "+999999999". up to 15 digits allowed.'
            )
        )


def is_valid_email(value):
    validator = EmailValidator()
    try:
        validator(value)
        return True
    except ValidationError:
        return False


def is_valid_phone_number(value):
    try:
        validate_phone_number(value)
        return True
    except ValidationError:
        return False
