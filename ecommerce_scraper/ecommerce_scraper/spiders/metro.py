import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded


#! Notes
# - scrapy crawl loblaws12 -o loblaws.json
# - Dissable proxy


class LoblawsSpider(scrapy.Spider):
    name = "metro"
    start_urls = [
        "https://www.metro.ca/epicerie-en-ligne/recherche?freeText=true&filter=Oikos"
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        },
        # "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 100000,
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
                    "playwright_page_methods": [],
                },
            )

    #! Just testing for 1 page, need to do page 2 next
    async def parse(self, response, **kwargs):
        page = response.meta["playwright_page"]
        await page.wait_for_timeout(5000)
        try:
            pdp_links = await page.query_selector_all(".product-details-link")
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
                        "playwright_page_methods": [],
                    },
                )

            next_page_link = await page.query_selector('a[aria-label="Suivant"]')
            print("========== BEFORE NEXT PAGE")
            if next_page_link:
                next_page_url = await next_page_link.get_attribute("href")
                if next_page_url:
                    full_next_page_url = response.urljoin(next_page_url)
                    print("Scheduling next page:", full_next_page_url)
                    yield scrapy.Request(
                        url=full_next_page_url,
                        callback=self.parse,
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
        print("In parse_product")
        await page.wait_for_timeout(5000)
        try:
            timeout = 5000
            #! Product Name
            name_selectors = [".pi--title"]
            product_name_element = ""
            for selector in name_selectors:
                print("In for loop")
                try:
                    print("1")
                    await page.wait_for_selector(selector, timeout=timeout)
                    print("2")
                    product_name_element = await page.query_selector(selector)
                    if product_name_element:
                        break
                except Exception as e:
                    print(f"Error while waiting for Title selector {selector}: {e}")
                    input("GET SELECTOR: Name")

            product_name = (
                await product_name_element.inner_text()
                if product_name_element
                else "N/A"
            )
            print(f"Product name: {product_name}")

            #! Product Price
            price_selectors = ["div[data-main-price]"]
            price_elements = ""
            for selector in price_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    price_elements = await page.query_selector(selector)
                    if price_elements:
                        break
                except Exception as e:
                    print(f"Error while waiting for price selector {selector}: {e}")
                    # input("GET SELECTOR: Price")

            product_price = (
                await price_elements.inner_text() if price_elements else "N/A"
            )
            print(f"product_price: {product_price}")

            #! Product Category
            breadcrumb_elements = await page.query_selector_all(".b--list li")

            category_path_parts = []
            for element in breadcrumb_elements:
                a_tag = await element.query_selector("a")
                if a_tag:
                    span_tag = await a_tag.query_selector("span[itemprop='name']")
                    text = await span_tag.inner_text() if span_tag else ""
                else:
                    span_tag = await element.query_selector("span[itemprop='name']")
                    if span_tag:
                        text = await span_tag.inner_text()

                if text:
                    category_path_parts.append(text)
            category_path = "/".join(category_path_parts)

            #! Product Images
            image_elements = await page.query_selector_all("picture#main-img img")
            image_urls_set = set()

            for img in image_elements:
                src = await img.get_attribute("src")
                if src:
                    image_urls_set.add(src)

            image_urls_list = list(image_urls_set)
            if image_urls_list:
                yield ProductItemExpanded(
                    pdp_url=response.url,
                    image_urls=image_urls_list,
                    product_name=product_name,
                    product_description="N/A",
                    product_category=category_path,
                    product_price=product_price,
                )
            else:
                self.logger.warning(f"No images found at {response.url}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()
