import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItem
import asyncio


class InstacartSpider(scrapy.Spider):
    name = "instacart11"
    start_urls = [
        # TORONTO
        # "https://www.instacart.ca/store/s?k=oikos&actid=0d3b9bf0-806d-4847-8b5c-37317e1d5f49&search_source=logged_out_home_cross_retailer_search&search_id=9558493a-76cd-4cdb-96a5-95727c66d234&page_view_id=57468446-27c1-5c11-b493-7a8e38218387"
        # MONTREAL
        "https://www.instacart.ca/store/s?k=oikos&search_id=801daef9-6b3c-4f8a-8174-3476eef0732f&page_view_id=171d7b8d-1937-5425-9d37-d44bc0225a6e"
    ]

    custom_settings = {
        # "DOWNLOAD_DELAY": 10,
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        # "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_IGNORE_HTTPS_ERRORS": True,
        "PLAYWRIGHT_HEADLESS": False,
        "ROBOTSTXT_OBEY": False,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", ".e-gsplpt"),
                    ],
                },
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        vendor_link = await find_element_with_retry(page, ".e-gsplpt")

        urls = [await link.get_attribute("href") for link in vendor_link]

        for url in urls:
            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_pdp,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
            )

    async def parse_pdp(self, response):
        page = response.meta["playwright_page"]

        await page.wait_for_timeout(5000)

        pdp_links = await page.query_selector_all(
            "div[aria-label='Product'][role='group'] a"
        )
        urls = [await link.get_attribute("href") for link in pdp_links]

        for url in urls:
            if url and "oikos" in url.lower():
                full_url = response.urljoin(url)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_product,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", ".e-ggkabs"),
                        ],
                    },
                )

    async def parse_product(self, response):
        page = response.meta["playwright_page"]

        print("=== 1")
        await page.wait_for_timeout(5000)
        print("=== 2")
        await wait_for_cloudflare(page)
        print("=== 3")
        await page.wait_for_timeout(5000)
        print("=== 4")

        selectors = [".e-ggkabs", ".e-2szg1"]
        found = False
        for selector in selectors:
            try:
                print("=== 5")
                await page.wait_for_selector(selector, timeout=5000)
                print("=== 6")
                found = True
                break
            except Exception as e:
                print(f"Selector {selector} not found, trying next. Error: {e}")

        if not found:
            print(f"No valid selectors found for URL: {response.url}")
            return
        print("=== 7")
        image_urls_set = set()
        for selector in selectors:
            try:
                print("=== 8")
                image_elements = await page.query_selector_all(f"{selector} img")
                print("=== 9")
                for img in image_elements:
                    src = await img.get_attribute("src")
                    if src:
                        image_urls_set.add(src)
                if image_urls_set:
                    break
            except Exception as e:
                print(f"Failed to fetch images with {selector}. Error: {e}")

        if image_urls_set:
            yield ProductItem(pdp_url=response.url, image_urls=list(image_urls_set))
        else:
            print(f"No images found at {response.url}")

        await page.close()

    # async def parse_product(self, response):
    #     page = response.meta["playwright_page"]
    #     print("1")
    #     await page.wait_for_timeout(5000)
    #     try:
    #         # await page.wait_for_selector(".e-ggkabs", timeout=5000)
    #         await page.wait_for_selector(".e-ggkabs")
    #     except Exception as e:
    #         await page.wait_for_selector(".e-2szg1")

    #     print("2")
    #     try:
    #         image_urls_set = set()
    #         try:
    #             image_elements = await page.query_selector_all(
    #                 ".e-ggkabs img", timeout=5000
    #             )
    #         except Exception as e:
    #             image_elements = await page.query_selector_all(".e-2szg1", timeout=5000)

    #         print("3")

    #         for img in image_elements:
    #             print("4")
    #             src = await img.get_attribute("src")
    #             print("5")
    #             if src:
    #                 image_urls_set.add(src)

    #         image_urls_list = list(image_urls_set)
    #         if image_urls_list:
    #             yield ProductItem(pdp_url=response.url, image_urls=image_urls_list)
    #         else:
    #             self.logger.warning(f"No images found at {response.url}")
    #     except Exception as e:
    #         print("6")
    #         print(f"Error processing {response.url}: {e}")
    #     finally:
    #         await page.close()


async def find_element_with_retry(page, selector, retries=3, delay=5):
    for attempt in range(retries):
        try:
            await page.wait_for_selector(selector, state="attached", timeout=5000)
            print("FOUND 1")
            return await page.query_selector_all(selector)
        except Exception as e:
            print(f"Attempt {attempt + 1}: Selector not found, retrying...")
            await page.wait_for_timeout(5000)

    print("NOT FOUND 1 after retries")
    input("INSPECT ELEMENT")
    return None


import time


async def wait_for_cloudflare(page, timeout=300):
    print("==== IN CLOUDFLARE")
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(
                "Timed out waiting for Cloudflare challenge to disappear."
            )
        challenge_element = await page.query_selector(".challenge-running")
        if challenge_element is None:
            print("Cloudflare challenge is no longer detected.")
            break
        print("Waiting for Cloudflare challenge to be resolved...")
        await asyncio.sleep(5)
