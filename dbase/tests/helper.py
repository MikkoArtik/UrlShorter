from random import randint, choices

from core.helper import generate_unique_url

ASCII_LIMITS = 41, 91


def generate_random_string(size=20):
    return ''.join([chr(randint(*ASCII_LIMITS)) for _ in range(size)])


def get_duplicate_records(generate_records: list):
    unique_short_urls = set((x[1] for x in generate_records))
    duplicate_records = []
    for item in choices(generate_records, k=len(generate_records) // 2):
        short_url, expiration_days = generate_unique_url(), randint(100, 300)
        if short_url in unique_short_urls:
            continue
        unique_short_urls.add(short_url)

        duplicate_records.append([item[0], short_url, expiration_days])
    return duplicate_records
