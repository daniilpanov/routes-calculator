import datetime

from fastapi import APIRouter

from backend.services.custom.get_rates import get_rates as _get_rates

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get("/")
def get_rates(dt_now: datetime.datetime | None = None):
    return _get_rates(dt_now)
