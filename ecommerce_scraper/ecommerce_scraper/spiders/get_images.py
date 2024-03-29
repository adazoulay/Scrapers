import scrapy
import json
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItem


class ImageSpider(scrapy.Spider):
    name = "image"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "CONCURRENT_REQUESTS": 4,
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
        "ITEM_PIPELINES": {"scrapy.pipelines.images.ImagesPipeline": 1},
        "IMAGES_STORE": "saved_images",
    }

    def start_requests(self):
        try:
            with open("../JSON/metro.json", "r") as file:  #! Change here
                data = json.load(file)
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {e}")
            return

        for item in data:
            image_urls = item.get("image_urls", [])
            for url in image_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"playwright": True, "playwright_include_page": True},
                    dont_filter=True,
                )

    async def parse(self, response):
        yield {"image_urls": [response.url]}
        page = response.meta.get("playwright_page")
        if page:
            await page.close()


class ImageIdSpider(scrapy.Spider):
    name = "image_id"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "CONCURRENT_REQUESTS": 4,
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
        #! Image pipeline
        "ITEM_PIPELINES": {"ecommerce_scraper.pipelines.CustomImagesPipeline": 1},
        "IMAGES_STORE": "saved_images",
    }

    def start_requests(self):
        try:
            with open("../JSON_IDX/metro_with_id.json", "r") as file:
                data = json.load(file)
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {e}")
            return

        for item in data:
            image_urls = item.get("image_urls", [])
            pdp_id = item.get("id")
            for idx, url in enumerate(image_urls, start=1):
                image_id = f"{pdp_id}.{idx}"
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "image_id": image_id,
                    },
                    dont_filter=True,
                )

    async def parse(self, response):
        image_id = response.meta["image_id"]
        yield {"image_urls": [response.url], "image_id": image_id}
        page = response.meta.get("playwright_page")
        if page:
            await page.close()
