from typing import cast

import pytest

from lufa.database import DatabaseManager
from lufa.provider import AppConfig, _create_database_manager


class TestCreateDatabaseManager:
    def test_should_create_empty_database(self, db_manager: DatabaseManager):
        assert db_manager is not None
        assert isinstance(db_manager, DatabaseManager)
        assert db_manager.is_not_empty()

    @pytest.mark.sqlite3
    def test_should_raise_exception_on_unknown_db_type(self):
        a = cast(AppConfig, {"DB_TYPE": "invalid"})

        with pytest.raises(ValueError, match=r"Unknown DB_TYPE \'INVALID\'"):
            _create_database_manager(a)
