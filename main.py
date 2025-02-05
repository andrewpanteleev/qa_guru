import json
import uvicorn
from http import HTTPStatus
from models.User import User
from models.AppStatus import AppStatus
from fastapi import FastAPI, HTTPException
from fastapi_pagination import Page, paginate, add_pagination

app = FastAPI()
add_pagination(app)  # Подключаем пагинацию

# Загрузка пользователей из файла в память
users: list[User] = []


@app.get("/status", status_code=HTTPStatus.OK, summary="Проверка доступности сервиса")
def status() -> AppStatus:
    return AppStatus(users=bool(users))


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK, summary="Получение пользователя по ID")
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    if user_id > len(users):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return users[user_id - 1]


@app.get("/api/users/", response_model=Page[User], summary="Получение списка пользователей с пагинацией")
def get_users() -> Page[User]:
    return paginate(users)


if __name__ == "__main__":
    # Загрузка пользователей из файла
    with open("users.json") as f:
        users = json.load(f)
    # Валидация данных из файла
    for user in users:
        User.model_validate(user)
    print("Users loaded")
    uvicorn.run(app, host="localhost", port=8002)