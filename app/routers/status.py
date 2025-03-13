from http import HTTPStatus

from fastapi import APIRouter

from app.database.engine import check_availability
from app.models.AppStatus import AppStatus

router = APIRouter()


@router.get("/status", response_model=AppStatus)
def status() -> AppStatus:
    return AppStatus(database=check_availability())