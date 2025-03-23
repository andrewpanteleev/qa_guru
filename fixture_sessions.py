import pytest

from app.utils.base_session import BaseSession
from config import Server


@pytest.fixture(scope='session')
def reqresin(env):
    with BaseSession(base_url=Server(env).reqres) as session:
        yield session