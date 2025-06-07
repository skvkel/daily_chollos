import enum
from datetime import datetime

from pydantic import BaseModel, Field, condecimal


class GenreEnum(enum.Enum):
    TODOS = "TODOS"
    MAN = "HOMBRE"
    WOMAN = "MUJER"
    JUNIOR = "JUNIOR"
    NOT_SPECIFIED = "SIN ESPECIFICAR"


class SortEnum(enum.Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    DISCOUNT_ASC = "discount_asc"
    DISCOUNT_DESC = "discount_desc"


class ProductEntity(BaseModel):
    description: str
    platform: str
    genre: GenreEnum
    current_price: condecimal(max_digits=7, decimal_places=2)   # type: ignore[valid-type]
    first_price : condecimal(max_digits=7, decimal_places=2)   # type: ignore[valid-type]
    lower_price: condecimal(max_digits=7, decimal_places=2)   # type: ignore[valid-type]
    current_discount: int
    first_discount: int
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = None
    image: str
    brand: str
    color: str
    last_viewed: datetime
    link_url: str
