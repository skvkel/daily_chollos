from fastapi import FastAPI

from daily_chollos.interface.adapters.fastapi_adapter import (
    home_endpoints,
    product_endpoints,
    brand_endpoints, color_endpoints
)


def register_routes_tortoise(app: FastAPI):
    app.include_router(home_endpoints.router)
    app.include_router(product_endpoints.router)
    app.include_router(brand_endpoints.router)
    app.include_router(color_endpoints.router)

