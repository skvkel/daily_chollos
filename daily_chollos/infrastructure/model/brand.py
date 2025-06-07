from tortoise import (
    Model,
    fields
)
from tortoise.contrib.postgres.indexes import HashIndex


class BrandModel(Model):
    title = fields.TextField(primary_key=True)

    class Meta:
        table = "brand"
        indexes = [
            HashIndex(fields=("title",),
                      name="brand_index",),
        ]
