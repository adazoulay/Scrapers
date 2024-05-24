import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded
import os

#! Notes
# - scrapy crawl loblaws -o loblaws.json
# - Dissable proxy


class LoblawsSpider(scrapy.Spider):
    name = "loblaws"
    requires_proxy = False

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
        "CONCURRENT_REQUESTS": 8,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        },
        # "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_IGNORE_HTTPS_ERRORS": True,
        "PLAYWRIGHT_HEADLESS": True,
        #! Proxy
        "SCRAPEOPS_PROXY_ENABLED": False,
    }

    def __init__(self, brand_name=None, *args, **kwargs):
        super(LoblawsSpider, self).__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.start_urls = [f"https://www.loblaws.ca/search?search-bar={brand_name}"]

    def start_requests(self):
        for key, attribute in self.settings.attributes.items():
            print(f"{key}: {attribute.value}")
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

        print(f"========= PAGE URLS LEN:  {len(urls)}")

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

            product_name_element = await page.query_selector(
                "h1.product-name__item.product-name__item--name"
            )
            product_description_element = await page.query_selector(
                ".product-description-text__text"
            )

            category_element = await page.query_selector_all(
                ".breadcrumbs__list__item a"
            )

            price_element = await page.query_selector(
                ".price__value.selling-price-list__item__price.selling-price-list__item__price--now-price__value"
            )

            product_name = (
                await product_name_element.inner_text()
                if product_name_element
                else "N/A"
            )
            product_description = (
                await product_description_element.inner_text()
                if product_description_element
                else "N/A"
            )

            category_path = "/".join([await el.inner_text() for el in category_element])

            product_price = await price_element.inner_text() if price_element else "N/A"

            image_urls_list = list(image_urls_set)
            if image_urls_list:
                yield ProductItemExpanded(
                    vendor="loblaws",
                    sub_vendor="N/A",
                    product_brand=self.brand_name,
                    pdp_url=response.url,
                    image_urls=image_urls_list,
                    product_name=product_name,
                    product_description=product_description,
                    product_category=category_path,
                    product_price=product_price,
                )
            else:
                self.logger.warning(f"No images found at {response.url}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()
