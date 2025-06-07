from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse

from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp
from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp
from daily_chollos.infrastructure.repository.product_repository import ProductRepositoryImp
from daily_chollos.service.privatesportshop_service import PrivateSportShopService
from daily_chollos.service.product_service import ProductService
from daily_chollos.service.scrappers.private_sport_shop_scrapper import PrivateSportShopScrapper
from daily_chollos.interface.adapters.templates import templates

router = APIRouter(tags=['Home'])


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):

    return templates.TemplateResponse('index.html',
                                      {
                                        "request": request
                                      }
    )


@router.get('/execute_task')
async def execute_task(request: Request):
    private_sport_shop_scrapper = PrivateSportShopScrapper()
    private_sport_shop_service = PrivateSportShopService(
        scrapper=private_sport_shop_scrapper
    )
    product_service = ProductService(product_repository=ProductRepositoryImp(),
                                     brand_repository=BrandRepositoryImp(),
                                     color_repository=ColorRepositoryImp())

    await private_sport_shop_service.get_data_and_store(product_service)
