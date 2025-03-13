import copy
from http import HTTPStatus

import pytest
import requests
from faker import Faker

from app.models.User import ListUserPaginationModel
from app.models.User import User

fake = Faker()

user_payload = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
}


@pytest.fixture(scope="function")
def create_user(app_url):
    response_post = requests.post(f"{app_url}/api/users", json=user_payload)
    user = User.model_validate(response_post.json())
    return user.id


@pytest.fixture
def users(app_url):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    return ListUserPaginationModel.model_validate(response.json())


def test_users(app_url) -> None:
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    users_data = ListUserPaginationModel.model_validate(response.json())

    assert isinstance(users_data.items, list)
    assert len(users_data.items) > 0


def test_users_no_duplicates(users) -> None:
    users_ids = [user.id for user in users.items]
    assert len(users_ids) == len(set(users_ids))

class TestPagination:

    @pytest.mark.parametrize("size", [2, 4, 7])
    def test_pagination_size(self, app_url, size: int) -> None:
        response = requests.get(f"{app_url}/api/users?size={size}")
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        assert len(data.items) == size


    @pytest.mark.parametrize("size", [1, 2, 3])
    def test_pagination_total_pages(self, app_url, users: ListUserPaginationModel, size: int) -> None:
        response = requests.get(f"{app_url}/api/users?size={size}")
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        expected_pages = (users.total + size - 1) // size
        assert data.pages == expected_pages


    @pytest.mark.parametrize("page_one, page_two", [(1, 2)])
    @pytest.mark.parametrize("size", [5])
    def test_pagination_different_pages(self, app_url: str, page_one: int, page_two: int, size: int) -> None:

        response_page_1 = requests.get(f"{app_url}/api/users?page={page_one}&size={size}")
        response_page_2 = requests.get(f"{app_url}/api/users?page={page_two}&size={size}")

        assert response_page_1.status_code == HTTPStatus.OK
        assert response_page_2.status_code == HTTPStatus.OK

        data_page_1 = ListUserPaginationModel.model_validate(response_page_1.json())
        data_page_2 = ListUserPaginationModel.model_validate(response_page_2.json())

        ids_page_1 = {user.id for user in data_page_1.items}
        ids_page_2 = {user.id for user in data_page_2.items}

        assert ids_page_1, "Список пользователей на странице 1 пуст!"
        assert ids_page_2, "Список пользователей на странице 2 пуст!"
        assert ids_page_1.isdisjoint(ids_page_2), "Данные на страницах не должны пересекаться!"

        assert len(data_page_1.items) == size, f"Ожидалось {size} объектов на странице 1, получено {len(data_page_1.items)}"
        assert len(data_page_2.items) <= size, f"Ожидалось не более {size} объектов на странице 2, получено {len(data_page_2.items)}"


    @pytest.mark.parametrize("page, size", [(1, 2), (1, 5), (2, 3)])
    def test_pagination_correct_pages(self, app_url: str, page: int, size: int) -> None:
        response = requests.get(f"{app_url}/api/users?page={page}&size={size}")
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        expected_pages = (data.total + size - 1) // size
        assert data.pages == expected_pages, f"Ожидалось {expected_pages} страниц, получено {data.pages}"


    @pytest.mark.parametrize("size", [3, 5, 10])
    def test_pagination_response_fields(self, app_url: str, size: int) -> None:
        response = requests.get(f"{app_url}/api/users?size={size}")
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        assert isinstance(data.page, int)
        assert isinstance(data.size, int)
        assert isinstance(data.total, int)
        assert isinstance(data.pages, int)
        assert isinstance(data.items, list)


"""Тест на post: создание. Предусловия: подготовленные тестовые данные
Валидность тестовых данных (email, url)
Отправить модель без поля на создание"""
class TestCreationUser:
    def test_successful_creation(self, app_url):
        response_post = requests.post(f"{app_url}/api/users", json=user_payload)
        assert response_post.status_code == HTTPStatus.CREATED
        user = User.model_validate(response_post.json())
        response_get = requests.get(f"{app_url}/api/users/{user.id}")
        assert response_get.status_code == HTTPStatus.OK
        get_user = User.model_validate(response_get.json())
        assert user.id == get_user.id

    def test_invalid_email(self, app_url):
        copy_data = copy.deepcopy(user_payload)
        copy_data["email"] = "email"
        response_post = requests.post(f"{app_url}/api/users", json=copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_avatar(self, app_url):
        copy_data = copy.deepcopy(user_payload)
        copy_data["avatar"] = "avatar"
        response_post = requests.post(f"{app_url}/api/users", json=copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_first_name(self, app_url):
        copy_data = copy.deepcopy(user_payload)
        copy_data["first_name"] = 12345
        response_post = requests.post(f"{app_url}/api/users", json=copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_without_last_name(self, app_url):
        copy_data = copy.deepcopy(user_payload)
        copy_data.pop("last_name")
        response_post = requests.post(f"{app_url}/api/users", json=copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


"""Тест на delete: удаление. Предусловия: созданный пользователь
404 422 ошибки на delete
404 на удаленного пользователя"""
class TestDeletionUser:
    def test_successful_removal(self, app_url, create_user):
        response_delete = requests.delete(f"{app_url}/api/users/{create_user}")
        assert response_delete.status_code == HTTPStatus.OK
        response_get = requests.get(f"{app_url}/api/users/{create_user}")
        assert response_get.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_invalid_user_id(self, app_url, user_id):
        response_delete = requests.delete(f"{app_url}/api/users/{user_id}")
        assert response_delete.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_double_removal(self, app_url, create_user):
        response_delete = requests.delete(f"{app_url}/api/users/{create_user}")
        assert response_delete.status_code == HTTPStatus.OK
        response_delete_2 = requests.delete(f"{app_url}/api/users/{create_user}")
        assert response_delete_2.status_code == HTTPStatus.NOT_FOUND

    def test_get_deleted_user(self, app_url, create_user):
        response_delete = requests.delete(f"{app_url}/api/users/{create_user}")
        assert response_delete.status_code == HTTPStatus.OK

        response_get = requests.get(f"{app_url}/api/users/{create_user}")
        assert response_get.status_code == HTTPStatus.NOT_FOUND


"""Тест на patch: изменение. Предусловия: созданный пользователь
404 422 ошибки на patch"""
class TestUpdatedUser:
    def test_successful_update(self, app_url, create_user):
        updated_first_name = {
            "first_name": "Hulio"
        }
        response_patch = requests.patch(f"{app_url}/api/users/{create_user}", json=updated_first_name)
        assert response_patch.status_code == HTTPStatus.OK
        user = User.model_validate(response_patch.json())
        response_get = requests.get(f"{app_url}/api/users/{user.id}")
        user_get = User.model_validate(response_get.json())
        assert user_get.first_name == "Hulio"

    def test_invalid_email(self, app_url, create_user):
        updated_email = {
            "email": "email"
        }
        response_patch = requests.patch(f"{app_url}/api/users/{create_user}", json=updated_email)
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_avatar(self, app_url, create_user):
        updated_avatar = {
            "avatar": "avatar"
        }
        response_patch = requests.patch(f"{app_url}/api/users/{create_user}", json=updated_avatar)
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_invalid_user_id(self, app_url, user_id):
        response_patch = requests.patch(f"{app_url}/api/users/{user_id}")
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

"""Get после создания, изменения"""
class TestGetUser:
    def test_get_after_creation(self, app_url, create_user):
        response_get = requests.get(f"{app_url}/api/users/{create_user}")
        assert response_get.status_code == HTTPStatus.OK
        user = User.model_validate(response_get.json())
        assert user.id == create_user

    def test_get_after_update(self, app_url, create_user):
        updated_data = {"first_name": "UpdatedName"}
        response_patch = requests.patch(f"{app_url}/api/users/{create_user}", json=updated_data)
        assert response_patch.status_code == HTTPStatus.OK

        response_get = requests.get(f"{app_url}/api/users/{create_user}")
        assert response_get.status_code == HTTPStatus.OK
        user = User.model_validate(response_get.json())
        assert user.first_name == "UpdatedName"

"""Тест на 405 ошибку (метод не поддерживается)"""
class TestMethodNotAllowed:
    @pytest.mark.parametrize("method", ["put", "delete", "patch"])
    def test_method_not_allowed(self, app_url, method):
        request_func = getattr(requests, method)
        response = request_func(f"{app_url}/api/users")
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


"""Полный жизненный цикл пользователя: создание → чтение → обновление → удаление"""
class TestUserFlow:
    def test_user_lifecycle(self, app_url):
        # Создание пользователя
        response_post = requests.post(f"{app_url}/api/users", json=user_payload)
        assert response_post.status_code == HTTPStatus.CREATED
        user = User.model_validate(response_post.json())

        # Чтение пользователя
        response_get = requests.get(f"{app_url}/api/users/{user.id}")
        assert response_get.status_code == HTTPStatus.OK

        # Обновление пользователя
        updated_data = {"first_name": "UpdatedName"}
        response_patch = requests.patch(f"{app_url}/api/users/{user.id}", json=updated_data)
        assert response_patch.status_code == HTTPStatus.OK

        # Проверка обновления
        response_get_updated = requests.get(f"{app_url}/api/users/{user.id}")
        assert response_get_updated.status_code == HTTPStatus.OK
        updated_user = User.model_validate(response_get_updated.json())
        assert updated_user.first_name == "UpdatedName"

        # Удаление пользователя
        response_delete = requests.delete(f"{app_url}/api/users/{user.id}")
        assert response_delete.status_code == HTTPStatus.OK

        # Проверка удаления
        response_get_deleted = requests.get(f"{app_url}/api/users/{user.id}")
        assert response_get_deleted.status_code == HTTPStatus.NOT_FOUND