from datetime import datetime, timedelta

import pytest

from lufa.database import DatabaseManager


class TestDatabaseManager:
    def test_is_initialised(self, empty_db: DatabaseManager):
        # ohne Initialisierung muss es false sein
        assert not empty_db.is_not_empty()

        empty_db.init_db()
        # Nach der initialisierung muss es true sein
        assert empty_db.is_not_empty()

    def test_db_now(self, empty_db: DatabaseManager):
        empty_db.init_db()
        assert datetime_valid(empty_db.get_db_now())
        db_now = datetime.fromisoformat(empty_db.get_db_now()) + timedelta(hours=1)
        delta = datetime.now() - db_now
        tdelta = timedelta(seconds=1)
        assert delta <= tdelta

    def test_reinitializing_on_existing_does_not_throw_exception(self, empty_db: DatabaseManager):
        empty_db.init_db()
        empty_db.init_db()

    @pytest.mark.sqlite3
    def test_min_sqlite_version(self, empty_db: DatabaseManager):
        cursor = empty_db.get_db_connection().cursor()
        cursor.execute("SELECT sqlite_version() AS version;")
        version = [int(c) for c in cursor.fetchone()["version"].split(".")]
        assert version[0] >= 3, version

    @pytest.mark.postgres
    def test_min_postgres_version(self, empty_db: DatabaseManager):
        cursor = empty_db.get_db_connection().cursor()
        cursor.execute("SELECT version() AS version;")
        version = [int(c) for c in cursor.fetchone()["version"].split(" ")[1].split(".")]

        assert version[0] > 9 or version[0] == 9 and version[1] >= 4, version


def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except Exception:
        return False
    return True
