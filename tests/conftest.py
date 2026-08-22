import os
import tempfile

import pytest

import database.db as db_module


@pytest.fixture
def temp_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    monkeypatch.setattr(db_module, "DB_PATH", path)
    db_module.init_db()

    yield path

    os.remove(path)


@pytest.fixture
def app(temp_db):
    import app as app_module

    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    yield app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
