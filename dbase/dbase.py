import os
from typing import Union, Tuple
from datetime import datetime
import sqlite3
from sqlite3 import Connection, Cursor
from sqlite3 import IntegrityError

import dotenv


DATETIME_FMT = '%Y-%m-%d %H:%M:%S'


def is_dbase(path: str) -> bool:
    extension = os.path.basename(path).split('.')[-1]
    if extension == 'db':
        return True
    return False


def get_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, DATETIME_FMT)


def load_dbase_script() -> str:
    dotenv.load_dotenv()
    file_path = os.getenv('SQL_SCRIPT')
    with open(file_path) as file_ctx:
        return '\n'.join(file_ctx.readlines())


class Dbase:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise OSError('Invalid file path')

        if not is_dbase(path):
            raise OSError('It\'s not dbase file')

        self.__connection = sqlite3.connect(path)
        self.__cursor = self.__connection.cursor()

    @property
    def connection(self) -> Connection:
        return self.__connection

    @property
    def cursor(self) -> Cursor:
        return self.__cursor

    def set_valid_status(self, short_url: str, is_valid=True):
        is_valid_num = int(is_valid)
        query = f'UPDATE urls SET is_active={is_valid_num} WHERE ' \
                f'short_url=\'{short_url}\';'
        self.cursor.execute(query)
        self.connection.commit()

    def get_origin_url(self, short_url: str) -> Union[str, None]:
        query = 'SELECT origin_url FROM urls ' \
                f'WHERE short_url=\'{short_url}\' AND is_active=1;'
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if not record:
            return
        return record[0]

    def get_short_url(self, origin_url: str) -> Union[str, None]:
        query = f'SELECT short_url FROM urls ' \
                f'WHERE origin_url=\'{origin_url}\';'
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if not record:
            return
        return record[0]

    def is_exist_short_url(self, short_url) -> bool:
        query = 'SELECT EXISTS(SELECT 1 FROM urls ' \
                f'WHERE short_url=\'{short_url}\');'
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        return True if record[0] else False

    def is_exist_origin_url(self, origin_url) -> bool:
        query = 'SELECT EXISTS(SELECT 1 FROM urls ' \
                f'WHERE origin_url=\'{origin_url}\');'
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        return True if record[0] else False

    def insert_origin_url(self, origin_url: str, expiration_days: int,
                          short_url: str):
        if self.is_exist_short_url(short_url):
            raise ValueError('short url is not unique')

        if self.is_exist_origin_url(origin_url):
            raise ValueError('origin url is exist')

        registration_datetime_str = datetime.now().strftime(DATETIME_FMT)
        query = 'INSERT INTO urls (origin_url, short_url, ' \
                'registration_date, expiration_days) VALUES (' \
                f'\'{origin_url}\',\'{short_url}\', ' \
                f'\'{registration_datetime_str}\', {expiration_days});'
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except IntegrityError:
            raise

    def update_origin_url(self, origin_url: str, expiration_days: int,
                          short_url: str):
        if self.is_exist_short_url(short_url):
            raise ValueError('short url is not unique')

        registration_datetime_str = datetime.now().strftime(DATETIME_FMT)
        query = 'UPDATE urls SET ' \
                f'registration_date=\'{registration_datetime_str}\', ' \
                f'expiration_days={expiration_days}, ' \
                f'short_url=\'{short_url}\', is_active=1 WHERE ' \
                f'origin_url=\'{origin_url}\';'
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except IntegrityError:
            pass

    def get_url_info(self,
                     origin_url: str) -> Union[Tuple[str, datetime, int, bool],
                                               None]:
        query = 'SELECT short_url, registration_date, ' \
                'expiration_days, is_active FROM urls ' \
                f'WHERE origin_url=\'{origin_url}\''
        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if not record:
            return

        registration_datetime = get_datetime(record[1])
        is_active = True if record[3] else False
        return record[0], registration_datetime, record[2], is_active
