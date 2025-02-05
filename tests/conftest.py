import os
import dotenv
import pytest
import requests
from http import HTTPStatus


@pytest.fixture(autouse=True)
def envs():
    # Загружаем переменные окружения
    dotenv.load_dotenv()


@pytest.fixture
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


@pytest.fixture
def port():
    return 8002