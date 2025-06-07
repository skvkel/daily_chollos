from datetime import datetime
import os
import asyncio
import random
import re
import uuid
import gc
from decimal import Decimal
from zoneinfo import ZoneInfo

from playwright.async_api import (
    Frame,
    ElementHandle
)

from daily_chollos.domain.entities.product import (
    GenreEnum,
    ProductEntity
)
from daily_chollos.service.product_service import ProductService
from daily_chollos.service.scrappers.scrapper_engine import ScrapperHandlerImp


class PrivateSportShopScrapper(ScrapperHandlerImp):
    AMOUNT_PARALLEL_TASKS = 20
    AMOUNT_PARALLEL_LARGE_PAGES_TASKS = 20
    _semaphore_small_pages = asyncio.Semaphore(AMOUNT_PARALLEL_TASKS)
    _semaphore_large_pages = asyncio.Semaphore(AMOUNT_PARALLEL_LARGE_PAGES_TASKS)
    _lock_large_page = asyncio.Lock()

    def __init__(self,) -> None:
        super().__init__()
        self._large_webpages = []

    @staticmethod
    async def _block_images_loading(new_tab: Frame,) -> None:
        await new_tab.route("**/*", lambda  # noqa
            route: route.abort() if route.request.resource_type == "image" else route.continue_())

    @staticmethod
    async def _scroll_until_loaded(new_tab: Frame,
                                   items_selector: str,
                                   amount_items: int,
                                   url_webpage: str):

        async def _reload_all_items(new_tab: Frame) -> None:

            # Go to TOP
            await new_tab.evaluate("window.scrollTo(0, 0)")

            while True:
                # Do scroll
                await new_tab.mouse.wheel(0, 150)   # noqa
                await new_tab.wait_for_timeout(100)

                # Get length page
                new_height_reloading = await new_tab.evaluate("document.body.scrollHeight")
                # Get the position
                current_scroll_reloading = await new_tab.evaluate("window.scrollY + window.innerHeight")

                # If final reached
                if (
                        abs(current_scroll_reloading - new_height_reloading) <= 10 or
                        current_scroll_reloading >= new_height_reloading - 1
                ):
                    print("Closing reloading")
                    await asyncio.sleep(2)
                    return

        async def check_all_items_loaded(divs: list[ElementHandle],
                                         new_tab: Frame,
                                         url_webpage: str) -> None:

            description_selector = os.environ["PRIVATE_SPORT_SHOP_DESCRIPTION_ITEM_SELECTOR"]
            current_price_selector = os.environ["PRIVATE_SPORT_SHOP_CURRENT_PRICE_ITEM_SELECTOR"]

            retries_check_all_items = 0
            max_retries_check_all_items = 3

            while retries_check_all_items < max_retries_check_all_items:

                for div in divs:
                    # Get description
                    description_element = await div.query_selector(description_selector)
                    if not description_element:
                        print(f"Reloading items for {url_webpage}")
                        await _reload_all_items(new_tab)
                        retries_check_all_items += 1
                        break

                    new_price = await div.query_selector(current_price_selector)
                    if not new_price:
                        print(f"Reloading items for {url_webpage}")
                        await _reload_all_items(new_tab)
                        retries_check_all_items += 1
                        break
                break

        # Go to TOP
        await new_tab.evaluate("window.scrollTo(0, 0)")

        retries = 0
        max_retries = 2

        while retries < max_retries:
            while True:
                # Get the current number of items
                divs = await new_tab.query_selector_all(items_selector)
                current_count = len(divs)

                # Do scroll
                await new_tab.mouse.wheel(0, 150)   # noqa
                await new_tab.wait_for_timeout(100)

                # Get length page
                new_height = await new_tab.evaluate("document.body.scrollHeight")
                # Get the position
                current_scroll = await new_tab.evaluate("window.scrollY + window.innerHeight")

                # If all items are loaded
                if current_count >= amount_items:
                    # Ensure moving to the bottom
                    while True:

                        wheel_delta = random.randint(90, 120)
                        delay = random.randint(20, 30)

                        # Do scroll slowly
                        await new_tab.mouse.wheel(0, wheel_delta)  # noqa
                        await new_tab.wait_for_timeout(delay)

                        # Get length page
                        new_height_reloading = await new_tab.evaluate("document.body.scrollHeight")
                        # Get the position
                        current_scroll_reloading = await new_tab.evaluate(
                            "window.scrollY + window.innerHeight")

                        # If the final is reached, stop scrolling
                        if (
                                abs(current_scroll_reloading - new_height_reloading) <= 10 or
                                current_scroll_reloading >= new_height_reloading - 1
                        ):
                            break

                    # Ensure all property's items are loaded
                    await check_all_items_loaded(divs=divs,
                                                 new_tab=new_tab,
                                                 url_webpage=url_webpage)
                    # Wait for loading last items
                    await new_tab.wait_for_timeout(5000)
                    return

                # If all items are not loaded, retry from then top of the page
                if new_height == current_scroll and current_count < amount_items:
                    await new_tab.evaluate("window.scrollTo(0, 0)")
                    retries += 1
                    break

    @staticmethod
    async def _scroll_until_divs_large_page_loaded(tab: Frame,
                                                   divs: list[ElementHandle]) -> None:

        all_loaded = False
        max_retries_full_scroll = 5
        retry = 0
        description_selector = os.environ["PRIVATE_SPORT_SHOP_DESCRIPTION_ITEM_SELECTOR"]
        price_selector = os.environ["PRIVATE_SPORT_SHOP_CURRENT_PRICE_ITEM_SELECTOR"]

        while not all_loaded or retry < max_retries_full_scroll:
            original_webpage = tab.url

            await tab.evaluate("window.scrollTo(0, 0)")
            for _ in range(150):
                wheel_delta = random.randint(90, 110)
                delay = random.randint(20, 30)

                await tab.mouse.wheel(0, wheel_delta)   # noqa
                await tab.wait_for_timeout(delay)

                # Check if we scrolled to the next page
                if tab.url != original_webpage:
                    for _ in range(15):
                        wheel_delta = random.randint(90, 110)
                        delay = random.randint(20, 30)

                        await tab.mouse.wheel(0, wheel_delta)  # noqa
                        await tab.wait_for_timeout(delay)
                    break

            # Check divs loaded. If any div is not loaded, retry doing another scroll
            all_loaded = True
            for div in divs:
                if not await div.query_selector(description_selector):
                    all_loaded = False
                    break
                if not await div.query_selector(price_selector):
                    all_loaded = False
                    break

            retry += 1

            if all_loaded:
                break

    @staticmethod
    async def _do_screenshot(page: Frame):
        new_uuid = str(uuid.uuid4())
        await page.screenshot(path=f"webpage_{new_uuid}.png")   # noqa

    async def _get_item_properties(self,
                                   divs_details: list[ElementHandle],
                                   divs_links: list[ElementHandle],
                                   webpage: str) -> list[dict]:

        items = []

        for index, div in enumerate(divs_details):

            # Get description
            description = await self._get_description(div=div)

            # Get color
            try:
                if not description:
                    color = "NO ESPECIFICADO"
                else:
                    color = await self._get_color(description=description)
            except Exception as unexpected_exception:
                print(f"Error getting color for webpage {webpage} for item {description}: "
                      f"{unexpected_exception}")
                color = "NO ESPECIFICADO"

            # Get the current price
            try:
                price = await self._get_price(div=div)
            except Exception as unexpected_exception:
                print(f"Error getting price for webpage {webpage} for item {description}: "
                      f"{unexpected_exception}")
                price = 0.0

            # Get the discount
            try:
                discount = await self._get_discount(div=div)
                if discount == 0:
                    continue

            except Exception as unexpected_exception:
                print(f"Error getting discount: {unexpected_exception}")
                discount = 0

            # Get image
            try:
                image_src = await self._get_image(div=div)
            except Exception as unexpected_exception:
                print(
                    f"Error getting image attributes for webpage {webpage} for item {description}: "
                    f"{unexpected_exception}")
                image_src = None

            # Get brand
            try:
                brand = await self._get_brand(div=div)
            except Exception as unexpected_exception:
                print(
                    f"Error getting brand for webpage {webpage} for item {description}: "
                    f"{unexpected_exception}")
                brand = "No especificado"

            # Get genre
            try:
                genre = self._get_genre(description=description)
            except Exception as unexpected_exception:
                print(f"Error while getting genre: {unexpected_exception}. Setting NOT_SPECIFIED")
                genre = GenreEnum.NOT_SPECIFIED.value

            # Get link url
            try:
                link_url = await self._get_link_url(div=divs_links[index])
            except Exception as unexpected_exception:
                print(f"Error getting link url for webpage {webpage} for item {description}: "
                      f"{unexpected_exception}")
                link_url = ""

            items.append(
                {
                    "description": description,
                    "platform": "private_sport_shop",
                    "genre": genre,
                    "current_price": price,
                    "first_price": price,
                    "lower_price": price,
                    "first_discount": discount,
                    "current_discount": discount,
                    "last_viewed": datetime.now(ZoneInfo("Europe/Madrid")),
                    "image": image_src,
                    "brand": brand,
                    "color": color,
                    "link_url": link_url
                }
            )

        return items

    @staticmethod
    async def _get_description(div: ElementHandle) -> str:

        description_selector = os.environ["PRIVATE_SPORT_SHOP_DESCRIPTION_ITEM_SELECTOR"]
        description_element = await div.query_selector(description_selector)
        description = await description_element.inner_text()

        return description.strip()

    @staticmethod
    async def _get_color(description: str) -> str:

        color_pattern = os.environ["PRIVATE_SPORT_SHOP_COLOR_PATTERN_REGEX"]

        if (color := re.search(pattern=color_pattern,
                               string=description)):
            color = color.group(1)
        else:
            color = "No especificado"

        return color.strip()

    @staticmethod
    async def _get_price(div: ElementHandle) -> Decimal:

        price_selector = os.environ["PRIVATE_SPORT_SHOP_CURRENT_PRICE_ITEM_SELECTOR"]

        new_price = await div.query_selector(price_selector)
        new_price = await new_price.inner_text()

        new_price = re.sub(r"[^\d,.-]", "", new_price)
        new_price = new_price.split(",")

        new_price = f"{new_price[0].replace(".", "")}.{new_price[1]}"
        price = Decimal(new_price)

        return price

    @staticmethod
    async def _get_discount(div: ElementHandle) -> int:

        discount_selector = os.environ["PRIVATE_SPORT_SHOP_CURRENT_DISCOUNT_ITEM_SELECTOR"]

        discount_element = await div.query_selector(discount_selector)
        discount = await discount_element.inner_text() if discount_element else "0"

        if discount_element:
            discount = re.sub(r"[^\d,.-]", "", discount).replace(",", ".")
        else:
            discount = "0"

        return int(discount.strip())

    @staticmethod
    async def _get_image(div: ElementHandle) -> str:

        image_selector = os.environ["PRIVATE_SPORT_SHOP_IMAGE_ITEM_SELECTOR"]

        image_element = await div.query_selector(image_selector)
        image_src = await image_element.get_attribute("src")

        return image_src

    @staticmethod
    async def _get_brand(div: ElementHandle) -> str:

        brand_selector = os.environ["PRIVATE_SPORT_SHOP_BRAND_ITEM_SELECTOR"]

        brand_element = await div.query_selector(brand_selector)
        brand = await brand_element.inner_text()

        return brand.strip()

    @staticmethod
    def _get_genre(description: str) -> str:

        if (
                "mujer" in description.lower() or
                re.search(pattern=r"\woman\b", string=description.lower())
        ):
            genre = GenreEnum.WOMAN.value

        elif (
                "junior" in description.lower() or
                re.search(pattern=r"\bniñ.\b", string=description.lower())
        ):
            genre = GenreEnum.JUNIOR.value

        elif (
                "hombre" in description.lower() or
                re.search(pattern=r"\bman\b", string=description.lower())
        ):
            genre = GenreEnum.MAN.value
        else:
            genre = GenreEnum.NOT_SPECIFIED.value

        return genre

    @staticmethod
    async def _get_link_url(div: ElementHandle) -> str:

        link_pattern = os.environ["PRIVATE_SPORT_SHOP_LINK_PATTERN_REGEX"]
        website_url = os.environ["PRIVATE_SPORT_SHOP_URL"]

        link_regex = re.search(pattern=link_pattern,
                               string=await div.inner_html())
        link = link_regex.group(1).strip() if link_regex else ""

        return f"{website_url}{link}"

    @staticmethod
    async def _get_amount_items_loaded(tab: Frame) -> int:

        divs = await tab.query_selector_all("a.product-image")

        return len(divs)

    @staticmethod
    async def _get_amount_items(tab: Frame) -> int:

        amount_items_selector = os.environ["PRIVATE_SPORT_SHOP_AMOUNT_ITEMS_SELECTOR"]
        amount_items_xpath_selector = os.environ["PRIVATE_SPORT_SHOP_AMOUNT_ITEMS_XPATH"]

        try:
            # Simple CSS
            locator = tab.locator(amount_items_selector)
            await locator.wait_for(state="visible")
            element = await locator.inner_text()

            regex = re.search(pattern=r"[\d,]+",
                              string=element)
            if regex:
                amount_items = regex.group(0).replace(",", "")
                return int(amount_items)
            else:
                raise Exception("No content")

        except Exception as err:     # noqa
            print(f"Not found number of items: {err}. Retrying after 3 secs...")
            await asyncio.sleep(3)

            try:
                await tab.wait_for_selector(amount_items_xpath_selector,
                                            timeout=5000)
                element = await tab.locator(amount_items_xpath_selector).inner_text()
                regex = re.search(pattern=r"[\d,]+",
                                  string=element)
                if regex:
                    amount_items = regex.group(0).replace(",", "")
                    return int(amount_items)
                else:
                    return 0
            except:     # noqa
                return 0

    async def go_to_webpage(self) -> None:

        url = os.environ["PRIVATE_SPORT_SHOP_URL"]
        await self._page.goto(url,
                              wait_until="load")

    async def click_cookies(self) -> None:
        """ This method accepts cookies, doing click in button"""

        cookie_selector = os.environ["PRIVATE_SPORT_SHOP_COOKIE_SELECTOR"]
        cookie_button_selector = os.environ["PRIVATE_SPORT_SHOP_BUTTON_ACCEPT_COOKIE_SELECTOR"]

        await self._page.wait_for_selector(cookie_selector, timeout=10000)
        await self._page.click(cookie_button_selector)
        
    async def deploy_login_page(self) -> None:
        """ This method deploys the login page """

        login_button_selector = os.environ["PRIVATE_SPORT_SHOP_BUTTON_DEPLOY_LOGIN_SELECTOR"]
        
        login_button = self._page.locator(login_button_selector)
        await login_button.click()
        await self._page.wait_for_timeout(5000)
        
    async def do_login(self) -> None:
        """ Insert email and password and do login """

        email_selector = os.environ["PRIVATE_SPORT_SHOP_LOGIN_USER_BOX_SELECTOR"]
        password_selector = os.environ["PRIVATE_SPORT_SHOP_LOGIN_PASSWORD_BOX_SELECTOR"]
        email = os.environ["EMAIL_PRIVATE_SPORT_SHOP"]
        password = os.environ["PASSWORD_PRIVATE_SPORT_SHOP"]
        login_button = os.environ["PRIVATE_SPORT_SHOP_BUTTON_LOGIN_SELECTOR"]

        await self._page.fill(email_selector, email)
        await self._page.fill(password_selector, password)

        await self._page.click(login_button)
        await  self._page.wait_for_timeout(10000)

        await self._store_tokens()

    async def get_links_homepage(self) -> list[str]:
        """ Get all item links from the homepage"""

        items_homepage_selector = os.environ["PRIVATE_SPORT_SHOP_ITEMS_HOMEPAGE_SELECTOR"]

        await self._page.wait_for_timeout(2000)

        links = []
        while not links:
            try:
                links = self._page.locator(items_homepage_selector)
            except:     # noqa
                await self._page.wait_for_timeout(5000)

        webs = []
        while not webs:
            webs = [f"{os.environ['PRIVATE_SPORT_SHOP_URL']}{await link.get_attribute('href')}"
                    for link in await links.element_handles()
                    if await link.get_attribute('href')]

            if any(["javascript:void(0)" in webpage
                    for webpage in webs]):
                print("Error occurred while getting webpages (javascript:void() found). Retrying")
                await self._do_screenshot(self._page)
                await self.go_to_webpage()
                await self.deploy_login_page()
                await self.do_login()
                webs = []

        print(f"Found {len(webs)} links: {webs}")

        return webs

    async def get_items_from_webpages(self,
                                      webpages: list[str],) -> list[dict]:

        tasks = []

        for webpage in webpages:
            task = asyncio.create_task(self._task_get_and_store_items_from_single_webpage(
                url_webpage=webpage.rstrip(".")
            ))

            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        products_to_create = []
        for result in results:
            if not isinstance(result, list):
                print(f"Error while getting items from webpage: {result}")
                continue
            for product in result:
                product_obj = ProductEntity(**product)
                products_to_create.append(product_obj)

        return products_to_create

    async def process_large_webpages(self,
                                     product_service: ProductService) -> None:

        new_tasks = []

        for webpage_url in self._large_webpages:
            print(f"Creating task for large webpage {webpage_url}")
            task = asyncio.create_task(self._task_get_items_from_large_webpage(
                url_webpage=webpage_url,
                product_service=product_service
            ))

            new_tasks.append(task)

        await asyncio.gather(*new_tasks, return_exceptions=True)

    async def _task_get_and_store_items_from_single_large_webpage(self,
                                                                  url_webpage: str) -> list[dict]:
        async with self._semaphore_large_pages:
            print(f"Processing single large webpage {url_webpage}")
            product_list_selector = os.environ["PRIVATE_SPORT_SHOP_PRODUCT_LIST"]

            # Open a new tab
            new_tab = await self._context.new_page()
            await new_tab.context.add_cookies(self._cookies)

            try:
                try:
                    await new_tab.goto(url_webpage,
                                       wait_until="load")
                except:     # noqa E722
                    print("Error getting webpage. Trying again...")
                    await new_tab.goto(url_webpage,
                                       wait_until="load")

                try:
                    # Wait webpage loading
                    await new_tab.wait_for_selector(product_list_selector,
                                                    state="visible",)
                except:     # noqa E722
                    print("Error getting product list selector. Trying again...")
                    try:
                        await new_tab.wait_for_selector(product_list_selector,
                                                        timeout=100000)
                    except:     # noqa E722
                        return []

                # Decomment if we want bLock images to load
                # await self._block_images_loading(new_tab=new_tab)

                properties_selector = os.environ["PRIVATE_SPORT_SHOP_PROPERTIES_SELECTOR"]
                link_selector = os.environ["PRIVATE_SPORT_SHOP_LINK_SELECTOR"]

                try:
                    divs_details = await new_tab.query_selector_all(properties_selector)
                    divs_links = await new_tab.query_selector_all(link_selector)

                except: # noqa E722
                    print("Error getting divs. Trying again...")
                    divs_details = await new_tab.query_selector_all(properties_selector)
                    divs_links = await new_tab.query_selector_all(link_selector)

                try:
                    # Scroll to load all items on the page
                    await self._scroll_until_divs_large_page_loaded(
                        tab=new_tab,
                        divs=divs_details
                    )
                except: # noqa
                    print("Error scrolling to load all items. Trying again...")
                    await self._scroll_until_divs_large_page_loaded(
                        tab=new_tab,
                        divs=divs_details
                    )

                items_properties = await self._get_item_properties(divs_details=divs_details,
                                                                   divs_links=divs_links,
                                                                   webpage=url_webpage)

                return items_properties

            except Exception as e:
                print(f"Error while processing webpage {url_webpage}: {e}\n{e.args}")
                await self._do_screenshot(new_tab)

                return []

            finally:
                await new_tab.close()

    async def _task_get_and_store_items_from_single_webpage(self,
                                                            url_webpage: str,) -> list[dict]:
        """ This is the process to get all items (or products) from a single webpage """

        async with self._semaphore_small_pages:
            product_list_selector = os.environ["PRIVATE_SPORT_SHOP_PRODUCT_LIST"]
            items_selector = os.environ["PRIVATE_SPORT_SHOP_ITEMS_SELECTOR"]

            # Open a new tab
            new_tab = await self._context.new_page()
            await new_tab.context.add_cookies(self._cookies)

            try:
                try:
                    await new_tab.goto(url_webpage,
                                       timeout=200000)
                except:     # noqa
                    print("Error getting webpage. Closing and reopening...")
                    await new_tab.close()
                    new_tab = await self._context.new_page()
                    await new_tab.context.add_cookies(self._cookies)
                    await new_tab.goto(url_webpage,
                                       timeout=300000)

                # Wait for loading
                await new_tab.wait_for_timeout(10000)

                # Get the number of items
                amount_items = await self._get_amount_items(tab=new_tab)
                if amount_items == 0:
                    print(f"This webpage {url_webpage} is empty or wrong")
                    return []

                # Open in new windows if items are higher than 100
                if amount_items > 100:
                    print("This webpage has more than 100 items. Processing as large webpage...")
                    await new_tab.close()
                    gc.collect()
                    self._large_webpages.append(url_webpage)

                    return []

                try:
                    # Wait webpage loading
                    await new_tab.wait_for_selector(product_list_selector,
                                                    timeout=50000)
                except:     # noqa
                    await new_tab.wait_for_selector(product_list_selector,
                                                    timeout=1000000)
                # Decomment if we want bLock images loading
                # await self._block_images_loading(new_tab=new_tab)

                await self._scroll_until_loaded(new_tab=new_tab,
                                                items_selector=items_selector,
                                                amount_items=amount_items,
                                                url_webpage=url_webpage)

                properties_selector = os.environ["PRIVATE_SPORT_SHOP_PROPERTIES_SELECTOR"]
                link_selector = os.environ["PRIVATE_SPORT_SHOP_LINK_SELECTOR"]

                divs_details = await new_tab.query_selector_all(properties_selector)
                divs_links = await new_tab.query_selector_all(link_selector)

                if len(divs_details) < amount_items:
                    print(f"No se han encontrado todos los items. Cantidad marcada: {amount_items}."
                          f" Cantidad encontrada: {len(divs_details)}. URL: {url_webpage}")

                items_properties = await self._get_item_properties(divs_details=divs_details,
                                                                   divs_links=divs_links,
                                                                   webpage=url_webpage)

                return items_properties

            except Exception as e:
                print(f"Error while processing webpage {url_webpage}: {e}")
                await self._do_screenshot(new_tab)

                return []

            finally:
                await new_tab.close()
                gc.collect()

    async def _task_get_items_from_large_webpage(self,
                                                 url_webpage: str,
                                                 product_service: ProductService) -> None:

        async with self._lock_large_page:
            print(f"Task to process {url_webpage} has started")
            new_tab = await self._context.new_page()
            await new_tab.context.add_cookies(self._cookies)

            try:
                await new_tab.goto(url_webpage,
                                   wait_until="load")

                try:
                    # Wait for loading
                    await new_tab.wait_for_timeout(5000)
                except:     # noqa
                    await new_tab.wait_for_timeout(10000)

                # Get the number of items
                amount_products = await self._get_amount_items(tab=new_tab)
                # Get the number of items loaded per page
                amount_loaded_items_per_page = await self._get_amount_items_loaded(tab=new_tab)
                # Get the number of new tabs to open
                amount_tabs_to_open = (amount_products // amount_loaded_items_per_page) + 1

                new_tasks = []
                for page_number in range(amount_tabs_to_open):
                    print(f"Creating task for large webpage {url_webpage} with page {page_number}")
                    webpage_to_process = f"{url_webpage}&p={page_number}"
                    new_task = asyncio.create_task(
                        self._task_get_and_store_items_from_single_large_webpage(
                            url_webpage=webpage_to_process
                        ))
                    new_tasks.append(new_task)

                results = await asyncio.gather(*new_tasks, return_exceptions=True)

                products_to_create = []
                for result in results:
                    if not isinstance(result, list):
                        print(f"Error while getting items from webpage: {result}")
                        continue

                    for product in result:
                        product_obj = ProductEntity(**product)
                        products_to_create.append(product_obj)

                await product_service.store_products(
                    product_entities=products_to_create
                )

            finally:
                await new_tab.close()
                gc.collect()

    async def _store_tokens(self) -> None:
        cookies = await self._page.context.cookies(os.environ["PRIVATE_SPORT_SHOP_URL"])
        self._cookies = cookies