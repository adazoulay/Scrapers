import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded


#! NOTE:
#! NEED TO CHANGE RETURNED PRODUCT URL SIZE PARAM FOR FULL SIZE
#! Enable Proxy


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

            product_name_element = await page.query_selector("h1.lh-copy.dark-gray.mv1")

            product_description_elements = await page.query_selector_all(
                ".dangerous-html"
            )
            product_description = []
            for element in product_description_elements:
                text = await element.inner_text()
                product_description.append(text)

            # await page.wait_for_selector( #! Categories never load
            #     'nav[aria-label="breadcrumb"] a span', timeout=10000
            # )
            category_elements = await page.query_selector_all(
                'nav[aria-label="breadcrumb"] a span'
            )
            category_names = [await el.inner_text() for el in category_elements]

            price_element = await page.query_selector('span[itemprop="price"]')

            product_name = (
                await product_name_element.inner_text()
                if product_name_element
                else "N/A"
            )

            if product_description:
                product_description = "\n".join(product_description)
            else:
                product_description = "N/A"

            category_path = "/".join(category_names)

            product_price = await price_element.inner_text() if price_element else "N/A"

            modified_image_urls = [
                url.replace("odnHeight=80&odnWidth=80", "odnHeight=612&odnWidth=612")
                for url in image_urls_set
            ]

            image_urls_list = list(image_urls_set)
            if image_urls_list:
                yield ProductItemExpanded(
                    pdp_url=response.url,
                    image_urls=modified_image_urls,
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
