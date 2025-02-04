from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Модель данных пользователя
class UserData(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str

# Модель данных поддержки
class SupportData(BaseModel):
    url: str
    text: str

# Модель объединённого ответа с данными пользователя и информацией о поддержке
class UserResponse(BaseModel):
    data: UserData
    support: SupportData

# In-memory хранилище пользователей
db = {}

# POST-эндпоинт для создания пользователя.
# Клиент должен передать все поля, включая id.
@app.post("/api/users", response_model=UserData, summary="Создание нового пользователя")
def create_user(user: UserData):
    if user.id in db:
        raise HTTPException(status_code=400, detail="User already exists")
    db[user.id] = user.dict()
    return user.dict()

@app.get("/api/users", response_model=List[UserData], summary="Получение списка пользователей")
def get_users():
    return list(db.values())

@app.get("/api/users/{user_id}", response_model=UserData, summary="Получение информации о пользователе по ID")
def get_user(user_id: int):
    user = db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=UserData, summary="Обновление информации о пользователе")
def update_user(user_id: int, updated_user: UserData):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    # Здесь id обновлять не будем: сервер ожидает, что id не изменяется.
    updated_data = updated_user.dict()
    updated_data["id"] = user_id
    db[user_id] = updated_data
    return updated_data

@app.delete("/api/users/{user_id}", response_model=dict, summary="Удаление пользователя")
def delete_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    del db[user_id]
    return {"detail": "User deleted"}

@app.get("/api/users/{user_id}/detailed", response_model=UserResponse,
         summary="Получение информации о пользователе с данными поддержки")
def get_user_detailed(user_id: int):
    user = db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    support_data = SupportData(
        url="https://reqres.in/#support-heading",
        text="To keep ReqRes free, contributions towards server costs are appreciated!"
    )
    return UserResponse(data=user, support=support_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
