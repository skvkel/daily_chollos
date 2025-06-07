from daily_chollos.domain.entities.brand_entity import BrandEntity
from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp


class BrandService:

    def __init__(self,
                 brand_repository: BrandRepositoryImp) -> None:
        self._brand_repository = brand_repository

    async def get_all_ordered_brands(self) -> list[BrandEntity]:

        all_brands = await self._brand_repository.get_all_ordered_brands()

        return all_brands
