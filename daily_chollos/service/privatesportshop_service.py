import asyncio

from daily_chollos.domain.services.scrapper_engine_interface import ScrapperHandler
from daily_chollos.service.product_service import ProductService
from daily_chollos.service.scrappers.private_sport_shop_scrapper import PrivateSportShopScrapper


class PrivateSportShopService:

    def __init__(self,
                 scrapper: ScrapperHandler,):
        self._scrapper = scrapper

    async def get_data_and_store(self,
                                 product_service: ProductService) -> None:

        async with self._scrapper as scrapper:
            await scrapper.go_to_webpage()
            await scrapper.click_cookies()
            await scrapper.deploy_login_page()
            await scrapper.do_login()
            list_webpages = await scrapper.get_links_homepage()

            print("Processing all links")
            product_entities = await scrapper.get_items_from_webpages(
                webpages=list_webpages
            )
            await product_service.store_products(
                product_entities=product_entities
            )
            print("Processing large pages")
            await scrapper.process_large_webpages(
                product_service=product_service
            )

async def main():
    private_sport_shop_scrapper = PrivateSportShopScrapper()
    private_sport_shop_service = PrivateSportShopService(
        scrapper=private_sport_shop_scrapper
    )

    product_service = []
    await private_sport_shop_service.get_data_and_store(product_service)

if __name__ == '__main__':
    asyncio.run(main())