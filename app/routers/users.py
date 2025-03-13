from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi_pagination import Page
from pydantic import ValidationError

from app.database import users
from app.database.users import get_users_paginated
from app.models.User import User, UserCreate, UserUpdate

router = APIRouter(prefix="/api/users")


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail='Invalid user id')
    user = users.get_user(user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    return user


@router.get("", status_code=HTTPStatus.OK)
def get_users() -> Page[User]:
    if not users:
        raise HTTPException(status_code=404, detail="Users not found")
    return get_users_paginated()


@router.post("", status_code=HTTPStatus.CREATED)
def create_user(user: User) -> User:
    try:
        UserCreate.model_validate(user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    return users.create_user(user)


@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User) -> User:
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    try:
        updated_user = UserUpdate.model_validate(user.model_dump())
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors())

    return users.update_user(user_id, updated_user)


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user id")
    user = users.get_user(user_id)  # Предполагаем, что есть метод поиска пользователя
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    users.delete_user(user_id)
    return {"message": "User deleted"}