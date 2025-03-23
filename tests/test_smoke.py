import pytest
import requests
from app.models.reqres import Reqres


def check_service(env):
    try:
        response = Reqres(env).get_status()
        response.raise_for_status()
    except requests.RequestException:
        pytest.exit("Сервис недоступен. Тесты не будут выполнены.")


def test_status(env):
    response = Reqres(env).get_status()
    assert response.status_code == 200
    assert "database" in response.json()
