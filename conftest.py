from http import HTTPStatus
import requests
import os
import dotenv
import pytest
import json
from faker import Faker
from app.models.reqres import Reqres

pytest_plugins = ['fixture_sessions']

def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="session", autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def app_url():
    dotenv.load_dotenv()
    return os.getenv("APP_URL")


@pytest.fixture
def users(env) -> dict:
    response = Reqres(env).get_users()
    assert response.status_code == HTTPStatus.OK
    return response.json()

@pytest.fixture
def port() -> int:
    return 8002
# preconditions - add users to database without users id
# scope="module" - this fixture for this module (page)
@pytest.fixture(scope="module")
def fill_test_data(app_url):
    with open("users.json") as f:
        test_data_users = json.load(f)
    api_users = []
    for user in test_data_users:
        response = requests.post(f"{app_url}/api/users/", json=user)
        api_users.append(response.json())
    user_ids = [user["id"] for user in api_users]
    yield user_ids  # test start here, fixture return user_ids
    # delete created users from database
    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")
@pytest.fixture
def new_user() -> dict:
    fake = Faker()
    new_user = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "avatar": fake.image_url()
    }
    return new_user


@pytest.fixture
def create_new_user(env) -> int:
    new_user = {
        "email": os.getenv("NEW_USER_EMAIL"),
        "first_name": os.getenv("NEW_USER_FIRST_NAME"),
        "last_name": os.getenv("NEW_USER_LAST_NAME"),
        "avatar": os.getenv("NEW_USER_AVATAR")
    }
    user = Reqres(env).create_user(new_user)
    assert user.status_code == HTTPStatus.CREATED
    return user.json()['id']