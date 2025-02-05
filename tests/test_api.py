import pytest
import requests
from http import HTTPStatus
from models.User import User

def test_users(app_url):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    users_list = response.json()
    # В ответе от fastapi-pagination ожидается, что список пользователей находится в поле "items".
    items = users_list.get("items", [])
    # Проходим по всем элементам и проверяем их соответствие модели User через pydantic
    for user in items:
        User.model_validate(user)

def test_users_no_duplicates(users):
    # Фикстура "users" уже получает данные (ответ GET /api/users/) и возвращает JSON-объект.
    items = users.get("items", [])
    # Извлекаем идентификаторы пользователей
    ids = [user["id"] for user in items]
    # Проверяем, что все идентификаторы уникальны (то есть нет дублирующихся записей)
    assert len(ids) == len(set(ids))

@pytest.mark.parametrize("user_id", [1, 6, 12])
def test_user(app_url, user_id):
    # Отправляем GET-запрос для получения конкретного пользователя по ID
    response = requests.get(f"{app_url}/api/users/{user_id}")
    # Проверяем, что сервер вернул статус 200 OK
    assert response.status_code == HTTPStatus.OK
    user = response.json()
    # Проверяем, что данные пользователя соответствуют модели User (валидируются через pydantic)
    User.model_validate(user)

@pytest.mark.parametrize("user_id", [13])
def test_user_nonexistent_values(app_url, user_id):
    # Если запрашивается пользователь, которого нет (например, ID больше количества пользователей),
    # сервер должен вернуть статус 404 NOT FOUND.
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.parametrize("user_id", [-1, 0, 'text'])
def test_user_invalid_values(app_url, user_id):
    # Здесь мы проверяем, что передаются недопустимые значения для user_id.
    # Например, отрицательные, ноль или строка вместо целого числа.
    # Ожидается, что сервер вернет статус UNPROCESSABLE_ENTITY (422) для таких значений.
    response = requests.get(f"{app_url}/api/users/{user_id}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
