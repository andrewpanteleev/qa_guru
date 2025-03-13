import dotenv
from fastapi_pagination import add_pagination

from utils.generate_users import generate_users

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from routers import status, users
from app.database.engine import create_db_and_tables, clear_db

app = FastAPI()
add_pagination(app)
app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    create_db_and_tables()
    clear_db()
    generate_users(20)
    uvicorn.run(app, host="localhost", port=8002)