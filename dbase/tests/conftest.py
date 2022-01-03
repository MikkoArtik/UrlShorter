from random import randint
import sqlite3
from sqlite3 import Connection

import pytest
from pytest import fixture

from dbase.dbase import load_dbase_script

from dbase.tests.helper import generate_random_string
from core.helper import generate_unique_link


@fixture(scope='session')
def create_dbase() -> Connection:
    dbase = sqlite3.connect(':memory:')
    sql_script = load_dbase_script()
    dbase.cursor().execute(sql_script)
    dbase.commit()
    return dbase


@pytest.fixture
def generate_records():
    records = []
    for i in range(1000):
        origin_url = generate_random_string()
        short_url = generate_unique_link()
        expiration_days = randint(1, 30)
        records.append([origin_url, short_url, expiration_days])
    return records
