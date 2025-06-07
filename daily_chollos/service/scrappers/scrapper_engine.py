
from typing import override

from playwright.async_api import async_playwright

from daily_chollos.domain.services.scrapper_engine_interface import ScrapperHandler


class ScrapperHandlerImp(ScrapperHandler):

    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None

    @override
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self._browser = await self.playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        return self

    @override
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._context.close()
        await self._browser.close()
        await self.playwright.stop()

