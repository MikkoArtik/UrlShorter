import random
from datetime import datetime, timedelta


ALL_SYMBOL_IDS = set([x for x in range(48, 58)] + [x for x in range(97, 123)])
GOOD_SYMBOLS = [chr(x) for x in ALL_SYMBOL_IDS]

UNIQUE_LINK_SIZE = 5


def generate_unique_url() -> str:
    return ''.join(random.choices(GOOD_SYMBOLS, k=UNIQUE_LINK_SIZE))


def is_valid_link(registration_datetime: datetime,
                  expiration_days: int) -> bool:
    end_datetime = registration_datetime + timedelta(days=expiration_days)
    return end_datetime < datetime.now()
