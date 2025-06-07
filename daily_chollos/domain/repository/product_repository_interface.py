from abc import (
    ABC,
    abstractmethod
)


class ProductRepository(ABC):

    @staticmethod
    @abstractmethod
    async def save_model(product_model) -> None:
        raise NotImplementedError
