import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from guard import SecurityConfig, SecurityMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from tortoise import Tortoise

from daily_chollos.domain.repository.product_repository_interface import ProductRepository
from daily_chollos.infrastructure.di_container import Container
from daily_chollos.infrastructure.model import init_db
from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp
from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp
from daily_chollos.infrastructure.repository.product_repository import ProductRepositoryImp
from daily_chollos.interface.adapters.fastapi_adapter import register_routes_tortoise
from daily_chollos.service.privatesportshop_service import PrivateSportShopService
from daily_chollos.service.product_service import ProductService
from daily_chollos.service.scrappers.private_sport_shop_scrapper import PrivateSportShopScrapper

ENVIRONMENT = os.getenv("ENV", "local")

@asynccontextmanager
async def lifespan_tortoise(app: FastAPI):
    await init_db()
    scheduler.start()

    yield

    await Tortoise.close_connections()
    scheduler.shutdown()


app = FastAPI(
    title="dailychollos web",
    redirect_slashes=False,
    openapi_url=None,
    lifespan=lifespan_tortoise,
)

# DI injector
container = Container()
app.container = container

#
# config = SecurityConfig(
#     enable_redis=True,
#     redis_url=f"redis://:{os.environ['REDIS_TOKEN']}@{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}/0",
#     redis_prefix="myapp:security:",
#     blocked_user_agents=["curl", "wget"],
#     auto_ban_threshold=5,
#     auto_ban_duration=60 * 5,
#     custom_log_file="logs/security.log",
#     trust_x_forwarded_proto=False,
#     rate_limit=20,
#     rate_limit_window=10,
#     enforce_https=ENVIRONMENT == "production",
#     cors_allow_origins=["https://dailychollos.com"] if ENVIRONMENT == "production" else ["http://localhost:8000"],
#     cors_allow_methods=["*"],
#     cors_allow_headers=["*"],
#     cors_max_age=600,
#     block_cloud_providers={"AWS", "GCP", "Azure"},
# )
#
# app.add_middleware(SecurityMiddleware, config=config)

scheduler = AsyncIOScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dailychollos.com"]
    if ENVIRONMENT == "production" else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


async def periodic_tasks():
    product_service = ProductService(product_repository=ProductRepositoryImp(),
                                     color_repository=ColorRepositoryImp(),
                                     brand_repository=BrandRepositoryImp())
    private_sport_shop_scrapper = PrivateSportShopScrapper()
    private_sport_shop_service = PrivateSportShopService(scrapper=private_sport_shop_scrapper)
    await private_sport_shop_service.get_data_and_store(product_service=product_service)


register_routes_tortoise(app=app)
