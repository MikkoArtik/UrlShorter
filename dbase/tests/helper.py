from random import randint, choices

from core.helper import generate_unique_link

ASCII_LIMITS = 41, 91


def generate_random_string(size=20):
    return ''.join([chr(randint(*ASCII_LIMITS)) for _ in range(size)])


def get_duplicate_records(generate_records: list):
    duplicate_records = []
    for item in choices(generate_records, k=len(generate_records) // 2):
        unique_url, expiration_days = generate_unique_link(), randint(100, 300)
        duplicate_records.append([item[0], unique_url, expiration_days])
    return duplicate_records
