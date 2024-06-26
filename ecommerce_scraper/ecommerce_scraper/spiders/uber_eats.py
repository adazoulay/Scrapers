import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded
from bs4 import BeautifulSoup


#! Notes
# - Dissable proxy
# - Some selectors seem to change. Need to update when running again


class UberEatsSpider(scrapy.Spider):
    name = "uber_eats"
    requires_proxy = False
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
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
        #! Proxy
        "SCRAPEOPS_PROXY_ENABLED": False,
    }

    def __init__(self, brand_name=None, *args, **kwargs):
        super(UberEatsSpider, self).__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.start_urls = [
            f"https://www.ubereats.com/search?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkhvdXNlJTIwb24lMjBQYXJsaWFtZW50JTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyMDdiYzE4ZmYtYmMzMS1iZjcxLTI3MTYtYzY3YzUwZjEzNmJiJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMnViZXJfcGxhY2VzJTIyJTJDJTIybGF0aXR1ZGUlMjIlM0E0My42NjM1ODM1JTJDJTIybG9uZ2l0dWRlJTIyJTNBLTc5LjM2Nzk1OTklN0Q%3D&q={brand_name}&sc=SEARCH_BAR&searchType=GLOBAL_SEARCH&vertical=ALL",
            f"https://www.ubereats.com/search?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMjQ4NzMlMjBBdi4lMjBXZXN0bW91bnQlMjIlMkMlMjJyZWZlcmVuY2UlMjIlM0ElMjJFakUwT0RjeklFRjJMaUJYWlhOMGJXOTFiblFzSUZkbGMzUnRiM1Z1ZEN3Z1VVTWdTRE5aSURGWk1Td2dRMkZ1WVdSaElqRVNMd29VQ2hJSlE4RDZtYWtReVV3UkNLWS1aQnpXTDRVUWlTWXFGQW9TQ1Rsa09RRUhHc2xNRWFKYWstVGRtQzE0JTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMmdvb2dsZV9wbGFjZXMlMjIlMkMlMjJsYXRpdHVkZSUyMiUzQTQ1LjQ4MDg2NzQlMkMlMjJsb25naXR1ZGUlMjIlM0EtNzMuNjEwNzI2MyU3RA%3D%3D&q={brand_name}&sc=SEARCH_BAR&searchType=GLOBAL_SEARCH&vertical=ALL",
        ]

    def start_requests(self):
        print(f"!== Existing settings uber: {self.settings.attributes}")
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [],
                },
            )

    async def parse(self, response):
        try:
            page = response.meta["playwright_page"]
            vendor_link = await find_element_with_retry(page, ".ak.bu a")

            urls = [await link.get_attribute("href") for link in vendor_link]
            print(f"========= Number of vendor URLs:  {len(urls)}")

            for url in urls:

                base_url = response.urljoin(url)
                query_separator = "&" if "?" in base_url else "?"
                full_url = (
                    f"{base_url}{query_separator}storeSearchQuery={self.brand_name}"
                )

                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_vendor,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                )
        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    async def parse_vendor(self, response):
        try:
            page = response.meta["playwright_page"]

            await page.wait_for_timeout(100000)

            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            links = soup.select('a[tabindex="0"]')

            sub_vendor_element = soup.select_one("h1 span[data-testid='rich-text']")
            sub_vendor_text = (
                sub_vendor_element.text if sub_vendor_element else "Unknown Vendor"
            )
            print(f"Subvendor and len urls: {sub_vendor_text} : {len(links)}")

            for link in links:
                spans = link.find_all("span", {"data-testid": "rich-text"})
                span_texts = [span.text.lower() for span in spans if span.text]

                if any(self.brand_name.lower() in text for text in span_texts):
                    print("Brand in text")
                    url = link.get("href")
                    full_url = response.urljoin(url)
                    yield scrapy.Request(
                        url=full_url,
                        callback=self.parse_product,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [],
                            "sub_vendor": sub_vendor_text,
                        },
                    )
                else:
                    for text in span_texts:
                        print(f"Brand NOT in text: {text}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    #! ===============  Parse product =================
    async def parse_product(self, response):
        page = response.meta["playwright_page"]
        await page.wait_for_timeout(5000)
        sub_vendor = response.meta["sub_vendor"]
        try:
            timeout = 5000
            #! Name and Price parent element
            parent_element_html = await page.evaluate(
                """() => {
                // Attempt to select the span based on the first structure
                let target = document.querySelector("div > h2 + h1");
                if (!target) {
                    // If the first structure isn't found, attempt the second structure
                    target = document.querySelector("div > h2 + h1 + div + span[data-testid='rich-text']");
                }
                if (!target) {
                    // If the first structure isn't found, attempt the second structure
                    target = document.querySelector("div > h2 + h1 + span[data-testid='rich-text']");
                }
                return target ? target.parentElement.outerHTML : null;
            }"""
            )

            if parent_element_html:
                print("Great success!")
            else:
                print("Coundn't find parent")
                input("INSPECT ELEMENT")
                await page.close()
                return

            # BS Get TEXT
            soup = BeautifulSoup(parent_element_html, "html.parser")

            product_name = soup.find("h1").text if soup.find("h1") else None
            if not product_name or self.brand_name not in product_name.lower():
                print(f"===== SHOUDLN'T HAPPEN: {self.brand_name} not on page")
                await page.close()
                return
            spans = soup.find_all("span")

            product_price = ""
            for span in spans:
                product_price += span.text + " "
            product_price = product_price.strip()
            product_price = product_price if product_price else None

            #! List of selectors for description elements
            description_selectors = [
                'p[aria-hidden="true"] span[data-testid="rich-text"]',
            ]

            description_elements = []
            for selector in description_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    description_elements = await page.query_selector_all(
                        selector
                    )  #! Maybe query_all?
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

            #! List of selectors for image elements
            image_selectors = ['img[alt][role="presentation"]']

            image_urls_set = set()
            for image_selector in image_selectors:
                try:
                    await page.wait_for_selector(image_selector, timeout=timeout)
                    image_elements = await page.query_selector_all(image_selector)
                    for img in image_elements:
                        src = await img.get_attribute("src")
                        if src:
                            image_urls_set.add(src)
                except Exception as e:
                    print(
                        f"Error while waiting for image selector {image_selector}: {e}"
                    )
                    # input("GET SELECTOR: Image")

            #! ===== Yeild to create entity =====
            if image_urls_set:
                yield ProductItemExpanded(
                    vendor="uber_eats",
                    sub_vendor=sub_vendor,
                    pdp_url=response.url,
                    product_brand=self.brand_name,
                    image_urls=list(image_urls_set),
                    product_name=product_name,
                    product_description=product_description,
                    product_category="N/A",
                    product_price=product_price,
                )
            else:
                print(f"No images found at {response.url}")
                # input("GET SELECTOR")

        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()


async def find_element_with_retry(page, selector, retries=3, delay=5):
    for attempt in range(retries):
        try:
            await page.wait_for_selector(selector, state="attached", timeout=5000)
            # print("FOUND 1")
            return await page.query_selector_all(selector)
        except Exception as e:
            print(f"Attempt {attempt + 1}: Selector not found, retrying...")
            await page.wait_for_timeout(5000)

    print("NOT FOUND 1 after retries")
    # input("INSPECT ELEMENT")
    return None
