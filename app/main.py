import logging
from contextlib import asynccontextmanager

import dotenv
from fastapi_pagination import add_pagination

from app.utils.generate_users import generate_users

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.routers import status, users
from app.database.engine import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.warning("On startup")
    create_db_and_tables()
    generate_users(20)
    yield

    logging.warning("On shutdown")

app = FastAPI(lifespan=lifespan)
add_pagination(app)
app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)