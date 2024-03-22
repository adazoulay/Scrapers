import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItem


#! To get json out of this:
# - scrapy crawl loblaws12 -o loblaws.json


class LoblawsSpider(scrapy.Spider):
    name = "loblaws20"
    start_urls = ["https://www.loblaws.ca/search?search-bar=Oikos"]

    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
        # "DOWNLOAD_DELAY": 1,
        # "ITEM_PIPELINES": {"scrapy.pipelines.images.ImagesPipeline": 1},
        # "IMAGES_STORE": "saved_images",
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
                        PageMethod(
                            "wait_for_selector",
                            ".product-tile__details__info__name__link",
                        ),
                    ],
                },
            )

    async def parse(self, response, **kwargs):
        page = response.meta["playwright_page"]
        last_height = await page.evaluate("document.body.scrollHeight")

        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(5000)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == last_height:
                for _ in range(3):
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    await page.wait_for_timeout(1000)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break

            last_height = new_height

        pdp_links = await page.query_selector_all(
            ".product-tile__details__info__name__link"
        )
        urls = []
        for link in pdp_links:
            href = await link.get_attribute("href")
            if href:
                full_url = response.urljoin(href)
                urls.append(full_url)

        print(f"========= LEN =========: {len(urls)}")

        for url in urls:
            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_product,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "wait_for_selector",
                            ".product-tile__details__info__name__link",
                        ),
                    ],
                },
            )

        await page.close()

    async def parse_product(self, response):
        page = response.meta["playwright_page"]
        try:
            # Wait for the images to load with a specified timeout
            await page.wait_for_selector(
                ".responsive-image--product-details-page", timeout=10000
            )
            image_elements = await page.query_selector_all(
                ".responsive-image--product-details-page"
            )
            image_urls_set = set()

            for img in image_elements:
                src = await img.get_attribute("src")
                if src:
                    image_urls_set.add(src)

            image_urls_list = list(image_urls_set)
            if image_urls_list:
                yield ProductItem(pdp_url=response.url, image_urls=image_urls_list)
            else:
                self.logger.warning(f"No images found at {response.url}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()
