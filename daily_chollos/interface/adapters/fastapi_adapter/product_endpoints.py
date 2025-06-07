from dependency_injector.wiring import (
    inject,
    Provide
)
from fastapi import (
    APIRouter,
    Query,
    Depends
)
from starlette.requests import Request

from daily_chollos.domain.entities.product import SortEnum
from daily_chollos.infrastructure.di_container import Container
from daily_chollos.service.product_service import ProductService

router = APIRouter(prefix="/products",
                   tags=['Products'])


@router.get('/count')
@inject
async def get_total_count_products(
    product_service: ProductService = Depends(Provide[Container.product_service]),
):

    count = await product_service.count_products()

    return {
        "count": count,
    }


@router.get('/max_price')
@inject
async def get_max_price(
    product_service: ProductService = Depends(Provide[Container.product_service]),
):

    max_price = await product_service.get_max_price()

    return {
        "max_price": max_price,
    }


@router.get('')
@inject
async def filter_products(
        request: Request,
        product_service: ProductService = Depends(Provide[Container.product_service]),
        min_price: float | None = Query(None, ge=0, description="Min price"),
        max_price: float | None = Query(None, ge=0, description="Max price"),
        min_discount: int | None = Query(None, ge=1, le=100, description="Min discount (%)"),
        brands: str | None = Query(None, description="Brands separated by comma (max 10)"),
        colors: str | None = Query(None, description="Colors separated by comma (max 10)"),
        genres: str = Query(None, description="Genres separated by comma (max 3)"),
        sort: SortEnum = Query(None, description="Sort by"),
        sale_today: bool = Query(False, description="Filter by sale today"),
        new_today: bool = Query(False, description="Filter by new today"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(25, ge=1, le=50, description="Items amount per page")
):

    genres_list = []
    if genres:
        genres_list = [genre.strip() for genre in genres.split(',') if genre.strip()][:4]

    brands_list = []
    if brands:
        brands_list = [brand.strip() for brand in brands.split(',') if brand.strip()][:10]

    colors_list = []
    if colors:
        colors_list = [color.strip() for color in colors.split(',') if color.strip()][:10]

    count, products = await product_service.filter_products(
        page=page,
        page_size=page_size,
        min_price=min_price,
        max_price=max_price,
        min_discount=min_discount,
        brands=brands_list,
        colors=colors_list,
        genres=genres_list,
        sort=sort,
        sale_today=sale_today,
        new_today=new_today
    )

    return {
        "products": products,
        "total": count,
        "page": page,
        "page_size": page_size,
        "pages": (count // page_size) + (1 if count % page_size else 0)
    }