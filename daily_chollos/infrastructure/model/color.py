from tortoise import (
    Model,
    fields
)
from tortoise.contrib.postgres.indexes import HashIndex


class ColorModel(Model):
    title = fields.TextField(primary_key=True)

    class Meta:
        table = "color"
        indexes = [
            HashIndex(fields=("title",),
                      name="color_index",),
        ]
