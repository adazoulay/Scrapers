from bs4 import BeautifulSoup
import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded
import asyncio
import time

import logging

#! Notes
# - Dissable proxy
# - Some selectors seem to change. Need to update when running again


class InstacartSpider(scrapy.Spider):
    name = "instacart"
    requires_proxy = False

    custom_settings = {
        "DOWNLOAD_DELAY": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 10,
        "CONCURRENT_REQUESTS": 10,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_IGNORE_HTTPS_ERRORS": True,
        #! Proxy
        "SCRAPEOPS_PROXY_ENABLED": False,
    }

    def __init__(self, brand_name=None, *args, **kwargs):
        logging.info("IN SPIDER INNIT")
        super(InstacartSpider, self).__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.start_urls = [
            f"https://www.instacart.ca/store/s?k={brand_name}&actid=0d3b9bf0-806d-4847-8b5c-37317e1d5f49&search_source=logged_out_home_cross_retailer_search&search_id=9558493a-76cd-4cdb-96a5-95727c66d234&page_view_id=57468446-27c1-5c11-b493-7a8e38218387",
            f"https://www.instacart.ca/store/s?k={brand_name}&search_id=801daef9-6b3c-4f8a-8174-3476eef0732f&page_view_id=171d7b8d-1937-5425-9d37-d44bc0225a6e",
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        # PageMethod("wait_for_selector", ".e-3bd33f"),
                    ],
                },
            )

    async def parse(self, response):
        try:
            page = response.meta["playwright_page"]

            await page.wait_for_timeout(5000)

            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            vendor_links = soup.select("div[id='store-wrapper'] li a")
            print(f"Number of vendor URLs: {len(vendor_links)}")

            for link in vendor_links:

                first_spans_texts = [
                    div.find("span").text
                    for div in link.find_all("div", recursive=False)
                    if div.find("span")
                ]
                sub_vendor = (
                    first_spans_texts[0] if first_spans_texts else "Unknown Subvendor"
                )

                print(f"Sub-vendor name: {sub_vendor}")

                url = link.get("href")
                full_url = response.urljoin(url)
                print(f"yielding: {full_url}")
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_vendor,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "sub_vendor": sub_vendor,
                    },
                )

        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    async def parse_vendor(self, response):
        try:
            page = response.meta["playwright_page"]
            sub_vendor = response.meta["sub_vendor"]
            print("In parse_vendor")
            await page.wait_for_timeout(5000)

            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            product_containers = soup.find_all(
                "div", attrs={"aria-label": "Product", "role": "group"}
            )
            print(f"Subvendor and len urls: {sub_vendor} : {len(product_containers)}")

            for product in product_containers:
                spans = product.find_all("span")
                span_texts = [span.text.lower() for span in spans if span.text]

                if any(self.brand_name.lower() in text for text in span_texts):
                    print("Brand in text")
                    product_link = product.find("a", role="button")

                    if product_link and product_link.has_attr("href"):
                        url = product_link["href"]
                        full_url = response.urljoin(url)
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_product,
                            meta={
                                "playwright": True,
                                "playwright_include_page": True,
                                "vendor_name": sub_vendor,
                            },
                        )
                else:
                    vendor_text = " ".join(span_texts)
                    print(f"Brand NOT in text: {vendor_text}")

        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    async def parse_product(self, response):
        print("Parsing Product")
        page = response.meta["playwright_page"]
        sub_vendor = response.meta["vendor_name"]
        try:
            print("Parsing Product In try")
            timeout = 9000
            await page.wait_for_timeout(5000)
            await page.wait_for_timeout(5000)

            #! List of selectors for name elements
            name_selectors = [
                "div[id='item_details'] div div h2 span",
            ]

            name_element = None
            for selector in name_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    name_element = await page.query_selector(
                        selector
                    )  #! Maybe query_all?
                    if name_element:
                        break
                except Exception as e:
                    print(f"Error while waiting for name selector {selector}: {e}")
                    # input("GET SELECTOR: Name")

            product_name = await name_element.inner_text() if name_element else "N/A"

            print(f"product name: {product_name}")

            #! List of selectors for image elements
            selectors = [
                "li button img",
                "div.ic-image-zoomer img",
                "div[role='button'] picture img",
            ]

            image_urls_set = set()

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    image_elements = await page.query_selector_all(selector)

                    for img in image_elements:
                        src = await img.get_attribute("src")
                        if src:
                            image_urls_set.add(src)
                    if image_urls_set:
                        break
                except Exception as e:
                    print(f"Failed to fetch images with {selector}. Error: {e}")
                    # input("INSPECT IMG SELECTOR")

            #! List of selectors for description elements
            description_selectors = [
                "div[tabindex='-1']  h2 + div p",
            ]

            description_elements = []
            for selector in description_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    description_elements = await page.query_selector_all(selector)
                    if description_elements:
                        break
                except Exception as e:
                    print(
                        f"Error while waiting for description selector {selector}: {e}"
                    )
                    # input("GET SELECTOR: Description")

            product_description = ""
            for element in description_elements:
                product_description += await element.inner_text() + "\n"

            #! List of selectors for price elements
            price_selectors = ["div[id='item_details'] div[data-radium='true']  span"]

            price_element = None
            for selector in price_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    price_element = await page.query_selector(
                        selector
                    )  #! Maybe query_all?
                    if price_element:
                        break
                except Exception as e:
                    print(f"Error while waiting for price selector {selector}: {e}")
                    # input("GET SELECTOR: Price")

            product_price = await price_element.inner_text() if price_element else "N/A"

            if image_urls_set:
                print("Success!")
                yield ProductItemExpanded(
                    vendor="instacart",
                    sub_vendor=sub_vendor,
                    product_brand=self.brand_name,
                    pdp_url=response.url,
                    image_urls=list(image_urls_set),
                    product_name=product_name,
                    product_description=product_description,
                    product_category="N/A",
                    product_price=product_price,
                )
            else:
                print(f"No images found at {response.url}")

        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()


# async def wait_for_cloudflare(page, timeout=300):
#     # print("==== IN CLOUDFLARE")
#     start_time = time.time()
#     while True:
#         if time.time() - start_time > timeout:
#             raise TimeoutError(
#                 "Timed out waiting for Cloudflare challenge to disappear."
#             )
#         challenge_element = await page.query_selector(".challenge-running")
#         if challenge_element is None:
#             # print("Cloudflare challenge is no longer detected.")
#             break
#         print("Waiting for Cloudflare challenge to be resolved...")
#         await asyncio.sleep(5)
