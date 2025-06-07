from abc import (
    ABC,
    abstractmethod
)


class ColorRepository(ABC):

    @staticmethod
    @abstractmethod
    async def save_model(product_model) -> None:
        raise NotImplementedError
