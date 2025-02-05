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
    # Предполагается, что fastapi-pagination возвращает total, items, page, size, pages
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
    Проверяем, что данные, полученные для разных страниц, различаются.
    """
    response_page = requests.get(f"{app_url}/api/users/", params={"page": page, "size": size})
    response_next_page = requests.get(f"{app_url}/api/users/", params={"page": page + 1, "size": size})
    assert response_page.status_code == HTTPStatus.OK
    assert response_next_page.status_code == HTTPStatus.OK
    items_page = response_page.json().get("items", [])
    items_next_page = response_next_page.json().get("items", [])
    # Если данных достаточно, наборы должны отличаться.
    assert items_page != items_next_page, "Data on consecutive pages should differ"
