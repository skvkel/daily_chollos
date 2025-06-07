from datetime import datetime
from zoneinfo import ZoneInfo

from tortoise import (
    Model,
    fields
)
from tortoise.contrib.postgres.indexes import HashIndex

from daily_chollos.domain.entities.product import GenreEnum


class ProductModel(Model):
    description = fields.TextField(primary_key=True)
    platform = fields.TextField()
    genre = fields.CharEnumField(GenreEnum,
                                 index=True)
    current_price = fields.DecimalField(null=False,
                                        max_digits=7,
                                        decimal_places=2,)
    first_price = fields.DecimalField(null=False,
                                      max_digits=7,
                                      decimal_places=2,)
    lower_price = fields.DecimalField(null=True,
                                      max_digits=7,
                                      decimal_places=2,)
    first_discount  = fields.IntField(null=False,)
    current_discount = fields.IntField(null=False,)
    created_at = fields.DatetimeField(default=datetime.now(ZoneInfo("Europe/Madrid")))
    updated_at = fields.DatetimeField(default=None,
                                      null=True)
    image = fields.TextField()
    brand = fields.ForeignKeyField(model_name="daily_chollos.BrandModel",
                                   related_name="products",
                                   null=False,)
    color = fields.ForeignKeyField(model_name="daily_chollos.ColorModel",
                                   related_name="products",
                                   null=False,)
    last_viewed = fields.DatetimeField(default=datetime.now(ZoneInfo("Europe/Madrid")),
                                       index=True)

    link_url = fields.TextField(null=False)

    class Meta:
        table = "product"
        indexes = [
            HashIndex(fields=("description",),
                      name="platform_index",),
        ]
