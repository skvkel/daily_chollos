import decimal
from datetime import (
    datetime,
    time,
    date
)
from zoneinfo import ZoneInfo

from tortoise.functions import Max

from daily_chollos.domain.entities.product import (
    ProductEntity,
    GenreEnum,
    SortEnum
)
from daily_chollos.domain.repository.product_repository_interface import ProductRepository
from daily_chollos.infrastructure.model.product import ProductModel
from daily_chollos.infrastructure.repository.base_repository import BaseRepository


class ProductRepositoryImp(ProductRepository, BaseRepository):

    def __init__(self):
        super().__init__(model=ProductModel)

    @staticmethod
    def get_common_info(page: int,
                        page_size: int,) -> tuple[date, datetime, int]:

        today = datetime.now(ZoneInfo("Europe/Madrid")).date()
        start = datetime.combine(today, time.min)
        offset = (page - 1) * page_size

        return today, start, offset

    async def save_model(self,
                         product_model) -> None:
        await product_model.save()

    async def get_max_price(self) -> int:
        today, _, _ = self.get_common_info(page=2, page_size=0)

        max_price = await (
            self.model.all()
            .filter(last_viewed__gte=today)
            .annotate(max_price=Max("current_price"))
            .values("max_price")
        )
        max_value = max_price[0]['max_price'] if max_price else None

        return max_value

    async def filter_products(
        self,
        page: int,
        page_size: int,
        min_price: float = None,
        max_price: float = None,
        min_discount: int = None,
        brands: list[str] = None,
        colors: list[str] = None,
        sale_today: bool = False,
        new_today: bool = False,
        genres: list[GenreEnum] | None = None,
        sort: SortEnum | None = None,
    ) -> tuple[int, list[ProductEntity]]:

        # Control max page_size and page number
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        # Get available products
        filters = {
            "last_viewed__gte": datetime.now(ZoneInfo("Europe/Madrid")).date()
        }

        if min_price is not None and isinstance(min_price, (int, float)) and min_price >= 0:
            filters["current_price__gte"] = min_price + 1
        if max_price is not None and isinstance(max_price, (int, float)) and max_price >= 0:
            filters["current_price__lte"] = max_price + 1
        if min_discount is not None:
            filters["current_discount__lte"] = min_discount*-1
        if brands:
            filters["brand__title__in"] = brands
        if colors:
            filters["color__title__in"] = colors
        if genres and GenreEnum.TODOS.value not in genres:
            filters["genre__in"] = genres
        if sale_today:
            filters["updated_at__gte"] = datetime.now(ZoneInfo("Europe/Madrid")).date()
        if new_today:
            filters["created_at__gte"] = datetime.now(ZoneInfo("Europe/Madrid")).date()

        match sort:
            case SortEnum.PRICE_ASC:
                sort_by = "current_price"
                type_sort = "asc"
            case SortEnum.PRICE_DESC:
                sort_by = "current_price"
                type_sort = "desc"
            case SortEnum.DISCOUNT_ASC:
                sort_by = "current_discount"
                type_sort = "asc"
            case SortEnum.DISCOUNT_DESC:
                sort_by = "current_discount"
                # Because discount is negative and this should be inverted
                type_sort = "asc"
            case _:
                sort_by = "created_at"
                # Because discount is negative and this should be inverted
                type_sort = "desc"

        order_field = f"-{sort_by}" if type_sort == "desc" else sort_by

        query = (
            self.model.filter(**filters)
            .order_by(order_field)
            .prefetch_related('brand', 'color')
        )

        total = await query.count()
        offset = (page - 1) * page_size
        products = await query.offset(offset).limit(page_size)

        product_entities = []
        for product_model in products:
            entity_data = product_model.__dict__.copy()
            if 'current_price' in entity_data and isinstance(entity_data['current_price'],
                                                             decimal.Decimal):
                entity_data['current_price'] = float(entity_data['current_price'])

            if hasattr(product_model, 'brand') and product_model.brand:
                entity_data['brand'] = product_model.brand.title
            if hasattr(product_model, 'color') and product_model.color:
                entity_data['color'] = product_model.color.title

            product_entities.append(ProductEntity(**entity_data))

        return total, product_entities
