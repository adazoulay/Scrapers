import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItem


#! NOTE:
#! NEED TO CHANGE RETURNED PRODUCT URL SIZE PARAM FOR FULL SIZE
class WalmartSpider(scrapy.Spider):
    name = "walmart32"
    start_urls = [
        "https://www.walmart.com/browse/oikos-gametime-protein/0/0/?_refineresult=true&_be_shelf_id=4192393&search_sort=100&facet=shelf_id%3A4192393&adsRedirect=false"
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
                    # "playwright_page_methods": [
                    #     PageMethod("wait_for_selector", "div[role='group'] > a[href]"),
                    # ],
                },
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        # await page.wait_for_timeout(10000)
        # await page.wait_for_selector("a[href]")

        # page_content = await page.content()
        # with open("page_content.html", "w") as f:
        #     f.write(page_content)

        pdp_links = await page.query_selector_all("div[role='group'] > a[href]")
        urls = [await link.get_attribute("href") for link in pdp_links]

        for url in urls:
            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_product,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
            )

    async def parse_product(self, response):
        page = response.meta["playwright_page"]
        try:
            image_urls_set = set()

            image_elements = await page.query_selector_all(".relative.db img")
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
