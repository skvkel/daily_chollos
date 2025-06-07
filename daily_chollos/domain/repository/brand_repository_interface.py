from abc import (
    ABC,
    abstractmethod
)


class BrandRepository(ABC):

    @staticmethod
    @abstractmethod
    async def save_model(product_model) -> None:
        raise NotImplementedError
