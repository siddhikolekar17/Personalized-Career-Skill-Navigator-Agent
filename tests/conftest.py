import pytest

from backend import database


@pytest.fixture
def tmp_db(tmp_path):
    path = str(tmp_path / "test.db")
    database.init_db(path)
    return path
