import os

from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": f'postgres://{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}@'
                   f'{os.environ["DB_HOST"]}:5432/{os.environ["DB_SCHEMA"]}'
    },
    "apps": {
        "daily_chollos": {
            'models': [
                'daily_chollos.infrastructure.model.product',
                'daily_chollos.infrastructure.model.brand',
                'daily_chollos.infrastructure.model.color',
                "aerich.models"
            ],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """ Initialize Tortoise """

    print('Initializing Tortoise...')

    await Tortoise.init(
        db_url=f'postgres://{os.environ["DB_USER"]}:{os.environ["DB_PASSWORD"]}@'
               f'{os.environ["DB_HOST"]}:5432/{os.environ["DB_SCHEMA"]}',
        modules={
            'daily_chollos': [
                'daily_chollos.infrastructure.model.product',
                'daily_chollos.infrastructure.model.brand',
                'daily_chollos.infrastructure.model.color',
                "aerich.models"
                ],
        },
    )
