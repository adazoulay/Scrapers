import scrapy
import json


class ImageIdSpider(scrapy.Spider):
    name = "image_id"

    custom_settings = {
        # "DOWNLOAD_DELAY": 2,
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
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
        #! Image pipeline
        "ITEM_PIPELINES": {"ecommerce_scraper.pipelines.CustomImagesPipeline": 1},
        "IMAGES_STORE": "all_images",
    }

    def start_requests(self):
        try:
            with open(
                "../all_competitors_merged_id.json", "r"
            ) as file:  # Adjusted path
                data = json.load(file)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return

        for item in data:
            for image_info in item.get("image_urls", []):
                for url, uuid in image_info.items():
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        meta={"uuid": uuid},
                        dont_filter=True,
                    )

    async def parse(self, response):
        print(f"Success: {response.url}")
        yield {"image_urls": [response.url], "uuid": response.meta["uuid"]}


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
        "ITEM_PIPELINES": {"scrapy.pipelines.images.ImagesPipeline": 1},
        "IMAGES_STORE": "saved_images",
    }

    def start_requests(self):
        try:
            with open("all_oikos_merged.json", "r") as file:  # Updated path
                data = json.load(file)
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {e}")
            return

        for item in data:
            image_urls = item.get("image_urls", [])
            pdp_url = item.get("pdp_url")  # Capture the pdp_url for use in the meta
            for url in image_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "pdp_url": pdp_url,  # Include pdp_url in request meta
                    },
                    dont_filter=True,
                )

    async def parse(self, response):
        yield {"image_urls": [response.url]}
        page = response.meta.get("playwright_page")
        if page:
            await page.close()
