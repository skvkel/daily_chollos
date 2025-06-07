from daily_chollos.domain.entities.color_entity import ColorEntity
from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp


class ColorService:

    def __init__(self,
                 color_repository: ColorRepositoryImp) -> None:
        self._color_repository = color_repository

    async def get_all_ordered_colors(self) -> list[ColorEntity]:

        all_colors = await self._color_repository.get_all_ordered_colors()

        return all_colors
