from datetime import datetime

from unittest.mock import patch, Mock

import pytest

from dbase.dbase import is_dbase, get_datetime
from dbase.dbase import Dbase
from dbase.tests.helper import get_duplicate_records


@pytest.mark.parametrize('path, expected',
                         [('/some/path/file.txt', False),
                          ('/some/path/file.db', True)])
def test_is_dbase(path, expected):
    assert is_dbase(path) is expected


@pytest.mark.parametrize('line, expected', [
    ('2021-05-31 15:00:08', datetime(2021, 5, 31, 15, 0, 8)),
    ('2022-08-09 23:24:25', datetime(2022,8, 9, 23, 24, 25))
])
def test_get_datetime(line, expected):
    assert get_datetime(line) == expected


class TestDbase:
    @patch('os.path.exists')
    def test_not_exist_path(self, os_mock: Mock):
        os_mock.return_value = False
        try:
            Dbase('/some/path')
            has_error = False
        except OSError:
            has_error = True
        assert has_error is True

    @patch('os.path.exists')
    def test_is_not_dbase_file(self, os_mock: Mock):
        os_mock.return_value = True
        try:
            Dbase('/some/path/file.txt')
            has_error = False
        except OSError:
            has_error = True
        assert has_error is True

    @pytest.mark.parametrize('is_path_exist, is_dbase_file, is_good_initial',
                             [(True, True, True), (False, True, False),
                              (True, False, False)])
    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_initial_dbase(self, os_mock: Mock, is_dbase_mock: Mock,
                           connect_mock: Mock,
                           is_path_exist, is_dbase_file, is_good_initial):
        os_mock.return_value = is_path_exist
        is_dbase_mock.return_value = is_dbase_file
        try:
            dbase_obj = Dbase('some/path')

            connect_mock.assert_called_with('some/path')
            dbase_obj.connection.cursor.assert_called_once()
            is_initial = True
        except OSError:
            connect_mock.assert_not_called()
            is_initial = False

        assert is_initial is is_good_initial

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_set_valid_status(self, os_mock: Mock, is_dbase_mock: Mock,
                               connect_mock: Mock,
                               create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')
        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()
            query = f'SELECT is_active FROM urls ' \
                    f'WHERE origin_url=\'{origin_url}\' AND ' \
                    f'short_url=\'{short_url}\';'
            dbase_obj.cursor.execute(query)

            is_active = dbase_obj.cursor.fetchone()[0]
            assert is_active == 1

            dbase_obj.set_valid_status(short_url, False)
            dbase_obj.connection.rollback()
            query = f'SELECT is_active FROM urls ' \
                    f'WHERE origin_url=\'{origin_url}\' AND ' \
                    f'short_url=\'{short_url}\';'
            dbase_obj.cursor.execute(query)

            is_active = dbase_obj.cursor.fetchone()[0]
            assert is_active == 0

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_get_short_url(self, os_mock: Mock, is_dbase_mock: Mock,
                           connect_mock: Mock,
                           create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')
        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            assert dbase_obj.get_short_url(origin_url) == short_url

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_is_exist_short_url(self, os_mock: Mock, is_dbase_mock: Mock,
                                connect_mock: Mock,
                                create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')
        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            assert dbase_obj.is_exist_short_url(short_url) is True

            query = f'DELETE FROM urls WHERE short_url=\'{short_url}\''
            dbase_obj.cursor.execute(query)
            dbase_obj.connection.commit()

            assert dbase_obj.is_exist_short_url(short_url) is False

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_is_exist_origin_url(self, os_mock: Mock, is_dbase_mock: Mock,
                                 connect_mock: Mock,
                                 create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')
        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            assert dbase_obj.is_exist_origin_url(origin_url) is True

            query = f'DELETE FROM urls WHERE origin_url=\'{origin_url}\''
            dbase_obj.cursor.execute(query)
            dbase_obj.connection.commit()

            assert dbase_obj.is_exist_origin_url(origin_url) is False

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_get_origin_url(self, os_mock: Mock, is_dbase_mock: Mock,
                               connect_mock: Mock,
                               create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')
        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            assert origin_url == dbase_obj.get_origin_url(short_url)

            dbase_obj.set_valid_status(short_url, False)
            assert dbase_obj.get_origin_url(short_url) is None

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_insert_origin_url(self, os_mock: Mock, is_dbase_mock: Mock,
                               connect_mock: Mock,
                               create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')

        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)

            dbase_obj.connection.rollback()

            query = f'SELECT COUNT(1), is_active FROM urls ' \
                    f'WHERE origin_url=\'{origin_url}\' AND ' \
                    f'short_url=\'{short_url}\';'
            dbase_obj.cursor.execute(query)

            record_count, is_active = dbase_obj.cursor.fetchone()
            assert record_count == 1
            assert is_active == 1

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_update_origin_url(self, os_mock: Mock, is_dbase_mock: Mock,
                               connect_mock: Mock,
                               create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')

        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)

        duplicate_records = get_duplicate_records(generate_records)
        for origin_url, short_url, expiration_days in duplicate_records:
            dbase_obj.update_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            query = f'SELECT COUNT(1), expiration_days, short_url, is_active ' \
                    f'FROM urls WHERE origin_url=\'{origin_url}\';'
            dbase_obj.cursor.execute(query)

            rec_count, days_db, short_url_db, is_active = dbase_obj.cursor.fetchone()
            assert rec_count == 1
            assert days_db == expiration_days
            assert short_url_db == short_url
            assert is_active == 1

    @patch('sqlite3.connect')
    @patch('dbase.dbase.is_dbase')
    @patch('os.path.exists')
    def test_get_url_info(self, os_mock: Mock, is_dbase_mock: Mock,
                          connect_mock: Mock,
                          create_dbase, generate_records):
        os_mock.return_value = True
        is_dbase_mock.return_value = True
        connect_mock.return_value = create_dbase

        dbase_obj = Dbase('/some/path')

        for origin_url, short_url, expiration_days in generate_records:
            dbase_obj.insert_origin_url(origin_url, expiration_days, short_url)

        duplicate_records = get_duplicate_records(generate_records)
        for origin_url, short_url, expiration_days in duplicate_records:
            dbase_obj.update_origin_url(origin_url, expiration_days, short_url)
            dbase_obj.connection.rollback()

            record = dbase_obj.get_url_info(origin_url)
            db_short_url, _, db_exp_days, db_is_active = record
            assert short_url == db_short_url
            assert db_exp_days == expiration_days
            assert db_is_active == 1
