import pytest
import requests


BASE_URL = "http://127.0.0.1:8000/api/users"


@pytest.mark.parametrize("user_id, email, first_name, last_name, avatar", [
    (1, "newuser@mail.ru", "New", "User", "avatar1.png"),
    (2, "example@mail.com", "Example", "User", "avatar2.png"),
])
def test_create_user(user_id, email, first_name, last_name, avatar):
    """Тест на создание нового пользователя"""
    response = requests.post(BASE_URL, json={
        "id": user_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "avatar": avatar
    })

    assert response.status_code == 200, f"Expected 200, but got {response.status_code}"
    body = response.json()
    assert "id" in body, "Response body does not contain 'id' key"
    assert body["id"] == user_id
    assert body["email"] == email
    assert body["first_name"] == first_name
    assert body["last_name"] == last_name
    assert body["avatar"] == avatar


@pytest.mark.parametrize("user_id", [
    12345,  # Передаем несуществующий ID
    -1,  # Или отрицательное значение
])
def test_get_user_not_found(user_id):
    """Тест на попытку получить несуществующего пользователя"""
    response = requests.get(f"{BASE_URL}/{user_id}")
    assert response.status_code == 404, f"Expected 404, but got {response.status_code}"
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize("user_id, email, first_name, last_name, avatar", [
    (3, "updated@mail.com", "Updated", "User", "updated_avatar.png"),
])
def test_update_user(user_id, email, first_name, last_name, avatar):
    """Тест на обновление данных пользователя"""
    # Сначала создаем пользователя с заданным id
    create_response = requests.post(BASE_URL, json={
        "id": user_id,
        "email": "temp@mail.com",
        "first_name": "Temp",
        "last_name": "User",
        "avatar": "temp.png"
    })
    assert create_response.status_code == 200, "Failed to create test user"

    # Обновляем данные пользователя (id передаем в URL и в теле — не изменяем)
    update_response = requests.put(f"{BASE_URL}/{user_id}", json={
        "id": user_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "avatar": avatar
    })
    assert update_response.status_code == 200, f"Expected 200, but got {update_response.status_code}"
    body = update_response.json()
    assert body["email"] == email
    assert body["first_name"] == first_name
    assert body["last_name"] == last_name
    assert body["avatar"] == avatar


def test_delete_user():
    """Тест на удаление пользователя"""
    user_id = 4
    # Создаем пользователя с id 4
    create_response = requests.post(BASE_URL, json={
        "id": user_id,
        "email": "delete@mail.com",
        "first_name": "Delete",
        "last_name": "User",
        "avatar": "delete.png"
    })
    assert create_response.status_code == 200, "Failed to create test user"

    # Удаляем пользователя
    delete_response = requests.delete(f"{BASE_URL}/{user_id}")
    assert delete_response.status_code == 200, f"Expected 200, but got {delete_response.status_code}"
    assert delete_response.json()["detail"] == "User deleted"

    # Проверяем, что пользователь действительно удалён
    get_response = requests.get(f"{BASE_URL}/{user_id}")
    assert get_response.status_code == 404, f"Expected 404, but got {get_response.status_code}"

