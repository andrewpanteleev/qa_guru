import json
import pytest
import requests
from jsonschema import validate
from schemas import post_users

BASE_URL = "https://reqres.in/api/users"


def test_schema_validate_from_file():
    """
    Тест на валидацию ответа POST-запроса к /api/users с использованием схемы из файла post_users.json.
    """
    response = requests.post(BASE_URL, data={"name": "AndreiP", "job": "Doctor"})
    body = response.json()
    assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    # Загружаем JSON-схему из файла post_users.json
    with open("post_users.json", "r") as file:
        schema = json.load(file)

    # Валидируем ответ по схеме
    validate(instance=body, schema=schema)


def test_schema_validate_from_variable():
    """
    Тест на валидацию ответа POST-запроса к /api/users с использованием схемы, определённой в переменной post_users.
    """
    response = requests.post(BASE_URL, data={"name": "AndreiP", "job": "Doctor"})
    body = response.json()
    assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    # Валидируем ответ по схеме из schemas.py
    validate(instance=body, schema=post_users)


def test_job_name_from_request_returns_in_response():
    """
    Тест проверяет, что значения полей name и job, отправленные в POST-запросе,
    присутствуют в ответе.
    """
    job = "AndreiP"
    name = "Doctor"
    response = requests.post(BASE_URL, json={"name": name, "job": job})
    body = response.json()
    assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    assert body["name"] == name, f"Expected name {name}, but got {body['name']}"
    assert body["job"] == job, f"Expected job {job}, but got {body['job']}"


def test_get_users_returns_unique_users():
    """
    Тест проверяет, что при запросе списка пользователей (с параметрами page и per_page)
    возвращаются уникальные ID.
    """
    response = requests.get(BASE_URL, params={"page": 2, "per_page": 4})
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    data = response.json()["data"]
    ids = [user["id"] for user in data]
    assert len(ids) == len(set(ids)), "Duplicate user IDs found in the response"


def test_get_single_user():
    """
    Проверяет, что GET /api/users/2 возвращает корректные данные пользователя.
    """
    response = requests.get("https://reqres.in/api/users/2")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    body = response.json()
    assert "data" in body, "Response does not contain 'data' key"
    data = body["data"]
    # Проверяем, что id равно 2 и email соответствует ожидаемому
    assert data["id"] == 2, f"Expected user id 2, but got {data['id']}"
    assert data["email"] == "janet.weaver@reqres.in", f"Expected email 'janet.weaver@reqres.in', but got {data['email']}"
    assert "first_name" in data and "last_name" in data and "avatar" in data, "Missing one of the required fields in user data"


def test_put_update_user_returns_updatedAt():
    """
    Проверяет, что PUT /api/users/2 возвращает обновлённые данные и содержит поле updatedAt.
    """
    payload = {"name": "AndreiP", "job": "President"}
    response = requests.put("https://reqres.in/api/users/2", json=payload)
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    body = response.json()
    # В ответе должно быть поле updatedAt, а также обновлённые name и job.
    assert "updatedAt" in body, "Response does not contain 'updatedAt' key"
    assert body["name"] == payload["name"], f"Expected name {payload['name']}, but got {body['name']}"
    assert body["job"] == payload["job"], f"Expected job {payload['job']}, but got {body['job']}"


def test_register_successful():
    """
    Проверяет, что POST /api/register с корректными данными возвращает id и token.
    """
    url = "https://reqres.in/api/register"
    payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    body = response.json()
    assert "id" in body, "Response does not contain 'id'"
    assert "token" in body, "Response does not contain 'token'"


def test_login_unsuccessful():
    """
    Проверяет, что POST /api/login без обязательного поля password возвращает ошибку 'Missing password'.
    """
    url = "https://reqres.in/api/login"
    payload = {"email": "ivan@petrov"}
    response = requests.post(url, json=payload)
    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
    body = response.json()
    assert "error" in body, "Response does not contain 'error' key"
    assert body["error"] == "Missing password", f"Expected error message 'Missing password', but got {body['error']}"