import copy
from http import HTTPStatus

import pytest
import requests
from faker import Faker

from app.models.User import ListUserPaginationModel
from app.models.User import User
from app.models.reqres import Reqres

fake = Faker()

user_payload = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "avatar": fake.image_url()
}


@pytest.fixture(scope="function")
def create_user(env):
    response_post = Reqres(env).create_user(user_payload)
    user = User.model_validate(response_post.json())
    return user.id


@pytest.fixture
def users(env):
    response = Reqres(env).get_users()
    assert response.status_code == HTTPStatus.OK
    return ListUserPaginationModel.model_validate(response.json())


def test_users(env) -> None:
    response = Reqres(env).get_users()
    assert response.status_code == HTTPStatus.OK
    users_data = ListUserPaginationModel.model_validate(response.json())

    assert isinstance(users_data.items, list)
    assert len(users_data.items) > 0


def test_users_no_duplicates(users) -> None:
    users_ids = [user.id for user in users.items]
    assert len(users_ids) == len(set(users_ids))

class TestPagination:

    @pytest.mark.parametrize("size", [2, 4, 7])
    def test_pagination_size(self, env, size: int) -> None:
        response = Reqres(env).get_users(size=size)
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        assert len(data.items) == size


    @pytest.mark.parametrize("size", [1, 2, 3])
    def test_pagination_total_pages(self, env, users: ListUserPaginationModel, size: int) -> None:
        response = Reqres(env).get_users(size=size)
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        expected_pages = (users.total + size - 1) // size
        assert data.pages == expected_pages


    @pytest.mark.parametrize("page_one, page_two", [(1, 2)])
    @pytest.mark.parametrize("size", [5])
    def test_pagination_different_pages(self, env: str, page_one: int, page_two: int, size: int) -> None:

        response_page_1 = Reqres(env).get_users(page=page_one, size=size)
        response_page_2 = Reqres(env).get_users(page=page_two, size=size)

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
    def test_pagination_correct_pages(self, env: str, page: int, size: int) -> None:
        response = Reqres(env).get_users(page=page, size=size)
        assert response.status_code == HTTPStatus.OK

        data = ListUserPaginationModel.model_validate(response.json())
        expected_pages = (data.total + size - 1) // size
        assert data.pages == expected_pages, f"Ожидалось {expected_pages} страниц, получено {data.pages}"


    @pytest.mark.parametrize("size", [3, 5, 10])
    def test_pagination_response_fields(self, env: str, size: int) -> None:
        response = Reqres(env).get_users(size=size)
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
    def test_successful_creation(self, env):
        response_post = Reqres(env).create_user(user_payload)
        assert response_post.status_code == HTTPStatus.CREATED
        user = User.model_validate(response_post.json())
        response_get = Reqres(env).get_user(user.id)
        assert response_get.status_code == HTTPStatus.OK
        get_user = User.model_validate(response_get.json())
        assert user.id == get_user.id

    def test_invalid_email(self, env):
        copy_data = copy.deepcopy(user_payload)
        copy_data["email"] = "email"
        response_post = Reqres(env).create_user(copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_avatar(self, env):
        copy_data = copy.deepcopy(user_payload)
        copy_data["avatar"] = "avatar"
        response_post = Reqres(env).create_user(copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_first_name(self, env):
        copy_data = copy.deepcopy(user_payload)
        copy_data["first_name"] = 12345
        response_post = Reqres(env).create_user(copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_without_last_name(self, env):
        copy_data = copy.deepcopy(user_payload)
        copy_data.pop("last_name")
        response_post = Reqres(env).create_user(copy_data)
        assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


"""Тест на delete: удаление. Предусловия: созданный пользователь
404 422 ошибки на delete
404 на удаленного пользователя"""
class TestDeletionUser:
    def test_successful_removal(self, env, create_user):
        response_delete = Reqres(env).delete_user(create_user)
        assert response_delete.status_code == HTTPStatus.OK
        response_get = Reqres(env).get_user(create_user)
        assert response_get.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_invalid_user_id(self, env, user_id):
        response_delete = Reqres(env).delete_user(user_id)
        assert response_delete.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_double_removal(self, env, create_user):
        response_delete = Reqres(env).delete_user(create_user)
        assert response_delete.status_code == HTTPStatus.OK
        response_delete_2 = Reqres(env).delete_user(create_user)
        assert response_delete_2.status_code == HTTPStatus.NOT_FOUND

    def test_get_deleted_user(self, env, create_user):
        response_delete = Reqres(env).delete_user(create_user)
        assert response_delete.status_code == HTTPStatus.OK

        response_get = Reqres(env).get_user(create_user)
        assert response_get.status_code == HTTPStatus.NOT_FOUND


"""Тест на patch: изменение. Предусловия: созданный пользователь
404 422 ошибки на patch"""
class TestUpdatedUser:
    def test_successful_update(self, env, create_user):
        updated_first_name = {
            "first_name": "Hulio"
        }
        response_patch = Reqres(env).update_user(create_user, updated_first_name)
        assert response_patch.status_code == HTTPStatus.OK
        user = User.model_validate(response_patch.json())
        response_get = Reqres(env).get_user(user.id)
        user_get = User.model_validate(response_get.json())
        assert user_get.first_name == "Hulio"

    def test_invalid_email(self, env, create_user):
        updated_email = {
            "email": "email"
        }
        response_patch = Reqres(env).update_user(create_user, updated_email)
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_avatar(self, env, create_user):
        updated_avatar = {
            "avatar": "avatar"
        }
        response_patch = Reqres(env).update_user(create_user, updated_avatar)
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_invalid_user_id(self, env, user_id):
        response_patch = Reqres(env).update_user(user_id)
        assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

"""Get после создания, изменения"""
class TestGetUser:
    def test_get_after_creation(self, env, create_user):
        response_get = Reqres(env).get_user(create_user)
        assert response_get.status_code == HTTPStatus.OK
        user = User.model_validate(response_get.json())
        assert user.id == create_user

    def test_get_after_update(self, env, create_user):
        updated_data = {"first_name": "UpdatedName"}
        response_patch = Reqres(env).update_user(create_user, updated_data)
        assert response_patch.status_code == HTTPStatus.OK

        response_get = Reqres(env).get_user(create_user)
        assert response_get.status_code == HTTPStatus.OK
        user = User.model_validate(response_get.json())
        assert user.first_name == "UpdatedName"

"""Тест на 405 ошибку (метод не поддерживается)"""
class TestMethodNotAllowed:
    @pytest.mark.parametrize("method", ["put", "delete", "patch"])
    def test_method_not_allowed(self, env, method):
        request_func = getattr(Reqres(env), method)
        response = request_func("/api/users")
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


"""Полный жизненный цикл пользователя: создание → чтение → обновление → удаление"""
class TestUserFlow:
    def test_user_lifecycle(self, env):
        # Создание пользователя
        response_post = Reqres(env).create_user(user_payload)
        assert response_post.status_code == HTTPStatus.CREATED
        user = User.model_validate(response_post.json())

        # Чтение пользователя
        response_get = Reqres(env).get_user(user.id)
        assert response_get.status_code == HTTPStatus.OK

        # Обновление пользователя
        updated_data = {"first_name": "UpdatedName"}
        response_patch = Reqres(env).update_user(user.id, updated_data)
        assert response_patch.status_code == HTTPStatus.OK

        # Проверка обновления
        response_get_updated = Reqres(env).get_user(user.id)
        assert response_get_updated.status_code == HTTPStatus.OK
        updated_user = User.model_validate(response_get_updated.json())
        assert updated_user.first_name == "UpdatedName"

        # Удаление пользователя
        response_delete = Reqres(env).delete_user(user.id)
        assert response_delete.status_code == HTTPStatus.OK

        # Проверка удаления
        response_get_deleted = Reqres(env).get_user(user.id)
        assert response_get_deleted.status_code == HTTPStatus.NOT_FOUND