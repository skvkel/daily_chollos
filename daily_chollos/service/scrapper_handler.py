from typing import override

from playwright.async_api import async_playwright, ViewportSize, Geolocation

from daily_chollos.domain.services.scrapper_engine_interface import ScrapperHandler


class ScrapperHandlerImpl(ScrapperHandler):

    def __init__(self):
        self.browser = None
        self.page = None

    @override
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True,
                                                             args=["--disable-dev-shm-usage",
                                                                   "--disable-gpu",
                                                                   "--disable-blink-features=AutomationControlled",
                                                                   "--no-sandbox",
                                                                   "--disable-dev-shm-usage",
                                                                   "--disable-infobars",
                                                                   "--window-size=1280,800",
                                                                   ])
        self.page = await self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport=ViewportSize({"width": 1280, "height": 800}),
            locale="es-ES",
            color_scheme="light",
            timezone_id="Europe/Madrid",
            geolocation=Geolocation({"longitude": -3.7038, "latitude": 40.4168}),
            permissions=["geolocation"],
            java_script_enabled=True
        )
        await self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)
        return self.page

    @override
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.page.close()
        await self.browser.close()
        await self.playwright.stop()

    async def click_cookies(self): ...
    async def deploy_login_page(self): ...
    async def do_login(self): ...
    async def do_scroll(self): ...
    async def get_items(self): ...
