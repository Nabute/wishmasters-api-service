import re
import phonenumbers
from rest_framework import serializers

from django.utils.translation import gettext as _


def validate_phone_number(phone_number, region="ET"):
    """Validates a phone number and provides detailed error messages."""
    try:
        parsed_number = phonenumbers.parse(phone_number, region)
        if not phonenumbers.is_valid_number(parsed_number):
            raise serializers.ValidationError(
                _("Invalid phone number format."))
        elif not phonenumbers.is_possible_number(parsed_number):
            raise serializers.ValidationError(
                _("Phone number is not possible for the specified region."))
        else:
            return True
    except phonenumbers.NumberParseException as e:
        raise serializers.ValidationError(
            _(f"Error parsing phone number: {e}"))


def validate_email(email):
    """Validates an email address."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if not re.match(email_regex, email):
        raise serializers.ValidationError(_("Invalid email address"))
