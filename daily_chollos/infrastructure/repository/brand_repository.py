from daily_chollos.domain.entities.brand_entity import BrandEntity
from daily_chollos.domain.repository.brand_repository_interface import BrandRepository
from daily_chollos.infrastructure.model.brand import BrandModel
from daily_chollos.infrastructure.repository.base_repository import BaseRepository


class BrandRepositoryImp(BrandRepository, BaseRepository):

    def __init__(self):
        super().__init__(model=BrandModel)

    async def save_model(self, product_model) -> None:
        await product_model.save()

    async def get_all_ordered_brands(self) -> list[BrandEntity]:
        brands = await self.model.all().order_by('title')

        brand_entities = [BrandEntity(title=color.title)
                          for color in brands]

        return brand_entities
