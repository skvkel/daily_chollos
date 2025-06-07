from fastapi import APIRouter
from starlette.requests import Request

from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp
from daily_chollos.service.brand_service import BrandService

router = APIRouter(prefix="/brand",
                   tags=['Brand'])

@router.get('')
async def get_brands(request: Request,):

    brand_service = BrandService(brand_repository=BrandRepositoryImp())

    brands = await brand_service.get_all_ordered_brands()

    return {
        "brands": brands,
    }