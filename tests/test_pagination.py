import os
import math
import requests
from http import HTTPStatus
import pytest


@pytest.fixture
def total_users(app_url):
    """Фикстура, которая возвращает общее количество пользователей через GET-запрос."""
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    return data.get("total", len(data.get("items", [])))

def test_pagination_object_count(app_url):
    """Проверяем, что при запросе с size=5 возвращается 5 объектов."""
    size = 5
    response = requests.get(f"{app_url}/api/users/", params={"page": 1, "size": size})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert "items" in body
    assert len(body["items"]) == size

@pytest.mark.parametrize("size", [3, 5, 7])
def test_pagination_total_pages(app_url, size):
    """
    Вычисляем ожидаемое количество страниц исходя из общего числа пользователей (без хардкода)
    и проверяем, что поле pages в ответе соответствует этому значению.
    """
    response = requests.get(f"{app_url}/api/users/", params={"page": 1, "size": size})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    # Ожидаемое количество страниц рассчитывается динамически
    expected_pages = math.ceil(total_users / size)
    # Поле 'pages' должно быть в ответе, если pagination настроен соответствующим образом
    assert body.get("pages") == expected_pages, f"Expected {expected_pages} pages, got {body.get('pages')}"
    # Также проверяем, что на странице количество элементов равно size (если данных достаточно)
    # Если на первой странице меньше данных, можно проверять, что длина либо равна size, либо меньше
    assert len(body["items"]) <= size

@pytest.mark.parametrize("page, size", [(1, 4), (2, 4)])
def test_pagination_different_pages(app_url, page, size):
    """
    Проверяем, что для разных страниц возвращаются отличающиеся наборы пользователей.
    Если наборы идентификаторов (как множества) совпадают, значит страницы содержат одни и те же данные,
    даже если порядок различается – это считается дефектом.
    """
    response_page1 = requests.get(f"{app_url}/api/users/", params={"page": page, "size": size})
    response_page2 = requests.get(f"{app_url}/api/users/", params={"page": page + 1, "size": size})
    assert response_page1.status_code == HTTPStatus.OK
    assert response_page2.status_code == HTTPStatus.OK
    items_page1 = response_page1.json().get("items", [])
    items_page2 = response_page2.json().get("items", [])

    # Извлекаем множества идентификаторов пользователей для каждой страницы
    set_page1 = {item["id"] for item in items_page1}
    set_page2 = {item["id"] for item in items_page2}

    # Если множества совпадают, это означает, что страницы содержат идентичные данные (даже если порядок разный)
    assert set_page1 != set_page2, "Pages contain identical items (even if sorted differently)"