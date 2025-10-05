"""
Reusable validators
"""
import re
from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """
    Validate phone number format (international format with country code)
    Example: +1234567890
    """
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            'Phone number must be entered in the format: "+999999999". '
            'Up to 15 digits allowed.'
        )

