from datetime import datetime
from zoneinfo import ZoneInfo

from daily_chollos.domain.entities.product import ProductEntity, GenreEnum, SortEnum
from daily_chollos.infrastructure.model.product import ProductModel
from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp
from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp
from daily_chollos.infrastructure.repository.product_repository import ProductRepositoryImp


class ProductService:

    def __init__(self,
                 product_repository: ProductRepositoryImp,
                 color_repository: ColorRepositoryImp,
                 brand_repository: BrandRepositoryImp) -> None:
        self._repository = product_repository
        self._brand_repository = brand_repository
        self._color_repository = color_repository

    async def filter_products(self,
                              page: int,
                              page_size: int,
                              min_price: float,
                              max_price: float,
                              min_discount: int,
                              brands: list[str],
                              colors: list[str],
                              sale_today: bool,
                              new_today: bool,
                              genres: list[GenreEnum] | None,
                              sort: SortEnum | None) -> tuple[int, list[ProductEntity]]:

        total, products = await self._repository.filter_products(
            page=page,
            page_size=page_size,
            min_price=min_price,
            max_price=max_price,
            min_discount=min_discount,
            brands=brands,
            colors=colors,
            genres=genres,
            sort=sort,
            sale_today=sale_today,
            new_today=new_today
        )

        return total, products

    async def get_max_price(self) -> int:

        max_price = await self._repository.get_max_price()

        return max_price

    async def store_products(self,
                             product_entities: list[ProductEntity]):

        for product_entity in product_entities:
            try:
                if not (product_in_db := await self._repository.get_or_none(
                        description=product_entity.description
                )):
                    color_obj, created = await self._color_repository.get_or_create(
                        title=product_entity.color
                    )

                    brand_obj, created = await self._brand_repository.get_or_create(
                        title=product_entity.brand
                    )

                    product_data = product_entity.model_dump()

                    product_data["color"] = color_obj
                    product_data["brand"] = brand_obj

                    await self._repository.create(**product_data)
                else:
                    await self.update_product(
                        product_in_db=product_in_db,
                        current_product=product_entity
                    )

            except Exception as err:
                print(f"Error con {product_entity.description}: {err}")

    async def update_product(self,
                             product_in_db: ProductModel,
                             current_product: ProductEntity):
        modified = False
        # Update last_viewed today
        product_in_db.last_viewed = datetime.now(ZoneInfo("Europe/Madrid"))

        if current_product.link_url == product_in_db.link_url:
            if current_product.current_price < product_in_db.current_price:
                # Change the current price
                product_in_db.current_price = current_product.current_price
                # Change the lower price
                product_in_db.lower_price = product_in_db.current_price
                modified = True

            # Minor because minor means a higher discount
            if current_product.current_discount < product_in_db.first_discount:
                product_in_db.current_discount = current_product.current_discount
                modified = True

        if modified:
            product_in_db.updated_at = datetime.now(ZoneInfo("Europe/Madrid"))
            product_in_db.link_url = current_product.link_url
            await self._repository.save_model(product_in_db)
        else:
            await self._repository.save_model(product_in_db)

    async def count_products(self) -> int:

        count = await self._repository.count()

        return count