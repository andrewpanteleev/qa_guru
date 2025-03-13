import pytest
import requests


def check_service(app_url):
    try:
        response = requests.get(f"{app_url}/status")
        response.raise_for_status()
    except requests.RequestException:
        pytest.exit("Сервис недоступен. Тесты не будут выполнены.")


def test_status(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.status_code == 200
    assert "users" in response.json()
    assert isinstance(response.json()["users"], bool)