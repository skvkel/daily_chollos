from daily_chollos.domain.entities.color_entity import ColorEntity
from daily_chollos.domain.repository.color_repository_interface import ColorRepository
from daily_chollos.infrastructure.model.color import ColorModel
from daily_chollos.infrastructure.repository.base_repository import BaseRepository


class ColorRepositoryImp(ColorRepository, BaseRepository):

    def __init__(self):
        super().__init__(model=ColorModel)

    async def save_model(self, product_model) -> None:
        await product_model.save()

    async def get_all_ordered_colors(self) -> list[ColorEntity]:
        colors = await self.model.all().order_by('title')

        color_entities = [ColorEntity(title=color.title)
                          for color in colors]

        return color_entities
