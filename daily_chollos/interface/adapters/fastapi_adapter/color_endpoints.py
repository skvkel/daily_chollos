from fastapi import APIRouter
from starlette.requests import Request

from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp
from daily_chollos.service.color_service import ColorService

router = APIRouter(prefix="/color",
                   tags=['Color'])


@router.get('')
async def get_colors(request: Request,):

    color_service = ColorService(color_repository=ColorRepositoryImp())

    colors = await color_service.get_all_ordered_colors()

    return {
        "colors": colors,
    }