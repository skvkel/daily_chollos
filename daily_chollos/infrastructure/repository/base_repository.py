from typing import (
    TypeVar,
    Generic
)
from tortoise.models import Model
from tortoise.queryset import QuerySetSingle

T = TypeVar('T', bound=Model)


class BaseRepository(Generic[T]):

    def __init__(self, model: type[T]):
        self._model = model()

    @property
    def model(self) -> type[T]:
        return self._model

    async def get_all(self) -> list[T]:
        return await self._model.all()

    async def get_by_id(self,
                        row_id: int) -> dict | None:
        return await self._model.get_or_none(id=row_id).values()

    async def get_or_none(self,
                          **kwargs) -> T | None:
        return await self._model.get_or_none(**kwargs)

    async def get_or_create(self, title: str) -> tuple:
        obj = await self.model.filter(title=title).first()

        if not obj:
            obj = await self.model.create(title=title)
            return obj, True

        return obj, False

    async def exists(self,
                     **kwargs) -> bool:
        return await self._model.exists(**kwargs)

    async def create(self,
                     **kwargs) -> T:
        return await self._model.create(**kwargs)

    async def update(self,
                     row_id: int, **kwargs) -> QuerySetSingle[T | None]:
        instance = await self._model.get_or_none(id=row_id)

        if instance:
            await instance.update_from_dict(kwargs).save()

        return instance

    async def delete(self,
                     row_id: int) -> None:
        instance = await self._model.get_or_none(id=row_id)

        if instance:
            await instance.delete()

    async def count(self) -> int:
        return await self._model.all().count()
