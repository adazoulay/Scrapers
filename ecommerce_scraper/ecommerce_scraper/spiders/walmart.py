import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded
import requests

#! NOTE:
#! Enable Proxy


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    requires_proxy = True

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        "CONCURRENT_REQUESTS": 5,
        # "DEFAULT_REQUEST_HEADERS": {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        #     "Accept-Language": "en-US,en;q=0.9",
        # },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_IGNORE_HTTPS_ERRORS": True,
        "PLAYWRIGHT_HEADLESS": False,
        #! Proxy
        "SCRAPEOPS_PROXY_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 725,
        },
        "SCRAPEOPS_API_KEY": "daea12f2-c861-4373-b3da-47c01582e74f",
    }

    def __init__(self, brand_name=None, *args, **kwargs):
        super(WalmartSpider, self).__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.start_urls = [f"https://www.walmart.ca/search?q={brand_name}"]

        response = requests.get(
            url="https://headers.scrapeops.io/v1/browser-headers",
            params={
                "api_key": "daea12f2-c861-4373-b3da-47c01582e74f",
                "num_results": "1",
            },
        )

        if response.status_code == 200:
            headers = response.json().get("result", [])[0]

            formatted_headers = {
                k: v for k, v in headers.items() if k != "sec-fetch-mod"
            }
            self.custom_settings["DEFAULT_REQUEST_HEADERS"] = formatted_headers

        else:
            self.logger.error(
                "Failed to retrieve dynamic headers. Using default headers."
            )

    def start_requests(self):
        print(f"!== Existing settings walmart: {self.settings.attributes}")
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                },
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        try:
            await page.wait_for_timeout(10000)
            await page.wait_for_selector("a[href]", timeout=5000)

            pdp_links = await page.query_selector_all("div[role='group'] > a[href]")
            urls = [await link.get_attribute("href") for link in pdp_links]

            print(f"========= PAGE URLS LEN:  {len(urls)}")

            for url in urls:
                yield scrapy.Request(
                    url=response.urljoin(url),
                    callback=self.parse_product,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                )
        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

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
                print("Success!")
                yield ProductItemExpanded(
                    vendor="walmart",
                    sub_vendor="N/A",
                    product_brand=self.brand_name,
                    pdp_url=response.url,
                    image_urls=modified_image_urls,
                    product_name=product_name,
                    product_description=product_description,
                    product_category=category_path,
                    product_price=product_price,
                )
            else:
                print("Fail")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()
