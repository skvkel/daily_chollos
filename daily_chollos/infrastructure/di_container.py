# DI container should be in infrastructure slayer beccause:
# 1. Gestiona cómo se construyen e instancian los objetos.
# 2. esuelve qué implementación concreta usar para cada abstracción.
# 3. Conecta las piezas que definiste en el dominio y la aplicación.

from dependency_injector import (
    containers,
    providers
)

from daily_chollos.infrastructure.repository.color_repository import ColorRepositoryImp
from daily_chollos.infrastructure.repository.product_repository import ProductRepositoryImp
from daily_chollos.infrastructure.repository.brand_repository import BrandRepositoryImp
from daily_chollos.service.brand_service import BrandService
from daily_chollos.service.color_service import ColorService
from daily_chollos.service.privatesportshop_service import PrivateSportShopService
from daily_chollos.service.product_service import ProductService
from daily_chollos.service.scrappers.scrapper_engine import ScrapperHandlerImp


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["daily_chollos.interface.adapters.fastapi_adapter"]
    )

    product_repository = providers.Factory(ProductRepositoryImp)
    color_repository = providers.Factory(ColorRepositoryImp)
    brand_repository = providers.Factory(BrandRepositoryImp)
    scrapper_handler = providers.Factory(ScrapperHandlerImp)

    product_service = providers.Factory(
        ProductService,
        product_repository=product_repository,
        color_repository=color_repository,
        brand_repository=brand_repository
    )

    brand_service = providers.Factory(
        BrandService,
        brand_repository=brand_repository,
    )

    color_service = providers.Factory(
        ColorService,
        color_repository=color_repository,
    )

    private_sport_shop_service = providers.Factory(
        PrivateSportShopService,
        scrapper=scrapper_handler
    )
