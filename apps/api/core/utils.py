import arrow
import string
import random


def format_datetime(datetime):
    dt = arrow.get(datetime).shift(hours=3)
    return dt.format("MMM D, YYYY H:mm")


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
