from random import randint
import sqlite3
from sqlite3 import Connection

import pytest
from pytest import fixture

from dbase.dbase import load_dbase_script

from dbase.tests.helper import generate_random_string
from core.helper import generate_unique_url


@fixture(scope='function')
def create_dbase() -> Connection:
    dbase = sqlite3.connect(':memory:')
    sql_script = load_dbase_script()
    dbase.cursor().execute(sql_script)
    dbase.commit()
    return dbase


@pytest.fixture
def generate_records():
    records = []
    unique_short_urls = set()
    for i in range(1000):
        origin_url = generate_random_string()
        short_url = generate_unique_url()
        if short_url in unique_short_urls:
            continue

        unique_short_urls.add(short_url)

        expiration_days = randint(1, 30)
        records.append([origin_url, short_url, expiration_days])
    return records
