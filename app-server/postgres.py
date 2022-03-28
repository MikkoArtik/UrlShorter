from typing import Union
from datetime import datetime

import psycopg2


class InvalidShortId(ValueError):
    pass


class PostgresDBase:
    def __init__(self, host: str, port: int, user: str, password: str,
                 dbase_name: str):
        self.host, self.port = host, port
        self.user, self.password = user, password
        self.dbase_name = dbase_name
        self.connection = self.create_connection()

    def create_connection(self):
        connection = psycopg2.connect(host=self.host, port=self.port,
                                      user=self.user, password=self.password,
                                      database=self.dbase_name)
        return connection

    def add_link(self, origin_link: str, days_count: int,
                 short_id: str) -> str:
        query = f'SELECT COUNT(1) FROM links WHERE link=\'{origin_link}\''
        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()
        is_exist_origin_link = True if record[0] else False

        if not is_exist_origin_link:
            query = f'SELECT COUNT(1) FROM links ' \
                    f'WHERE short_id=\'{short_id}\''
            cursor = self.connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            if record[0]:
                raise InvalidShortId

            query = 'INSERT INTO links (link, days_count, short_id) VALUES ' \
                    f'(\'{origin_link}\', {days_count}, \'{short_id}\')'
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            return short_id
        else:
            query = f'UPDATE links SET days_count={days_count}, ' \
                    f'is_active=true WHERE link=\'{origin_link}\' ' \
                    f'RETURNING short_id'
            cursor = self.connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            self.connection.commit()
            return record[0]

    def is_active_link(self, origin_link: str, short_id: str) -> bool:
        query = f'SELECT registration_date, days_count, is_active ' \
                f'FROM links ' \
                f'WHERE link=\'{origin_link}\' OR short_id=\'{short_id}\''
        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()
        if record is None:
            return False

        is_active = record[0]
        if not is_active:
            return False

        current_status = (datetime.now() - record[0]).days <= record[1]
        if current_status != is_active:
            query = f'UPDATE links SET is_active={current_status} ' \
                    f'WHERE link=\'{origin_link}\' OR short_id=\'{short_id}\''
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        return current_status

    def get_origin_link_by_short_id(self, short_id: str) -> Union[str, None]:
        is_active = self.is_active_link(origin_link='', short_id=short_id)
        if not is_active:
            return None

        query = f'SELECT link FROM links WHERE short_id=\'{short_id}\''
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchone()[0]
