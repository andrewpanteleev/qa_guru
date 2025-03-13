import os
import dotenv
import pytest


@pytest.fixture(scope="session", autouse=True)
def app_url():
    dotenv.load_dotenv()
    return os.getenv("APP_URL")