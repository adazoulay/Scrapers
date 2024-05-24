import scrapy
from scrapy_playwright.page import PageMethod
from ecommerce_scraper.items import ProductItemExpanded


#! Notes
# Proxy enabled
# - scrapy crawl loblaws12 -o loblaws.json


class MetroSpider(scrapy.Spider):
    name = "metro"
    requires_proxy = True

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 7,
        "CONCURRENT_REQUESTS": 7,
        # "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        # "CONCURRENT_REQUESTS": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,  
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
        super(MetroSpider, self).__init__(*args, **kwargs)
        self.brand_name = brand_name
        self.start_urls = [
            f"https://www.metro.ca/epicerie-en-ligne/recherche?freeText=true&filter={brand_name}"
        ]

    def start_requests(self):
        print(f"!== Existing settings metro: {self.settings.attributes}")
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
        await page.wait_for_timeout(10000)
        try:
            await page.wait_for_selector(".pt__content", timeout=5000)
            product_containers = await page.query_selector_all(".pt__content")
            urls = []
            for container in product_containers:
                brand_span = await container.query_selector(".head__brand")
                brand_name = await brand_span.inner_text() if brand_span else ""
                if brand_name.strip().lower() == self.brand_name.lower():
                    pdp_links = await container.query_selector_all(
                        ".product-details-link"
                    )
                    for link in pdp_links:
                        href = await link.get_attribute("href")
                        full_url = response.urljoin(href)
                        if href:
                            urls.append(full_url)
                        else:
                            print(f"brand name didn't match for {full_url}")
                else:
                    print(
                        f"Brand names didn't match: {brand_name.strip().lower()} VS { self.brand_name.lower()}"
                    )

            print(f"========= PAGE URLS LEN:  {len(urls)}")

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

            # await page.wait_for_selector("a[aria-label='Suivant']", timeout=5000)
            next_page_link = await page.query_selector("a[aria-label='Suivant']")

            print("========== BEFORE NEXT PAGE")
            if next_page_link:
                next_page_url = await next_page_link.get_attribute("href")
                print(f"========== NEXT PAGE URL: {next_page_url}")
                if next_page_url:
                    full_next_page_url = response.urljoin(next_page_url)
                    print(f"====== !!! full_next_page_url : {full_next_page_url}")
                    yield scrapy.Request(
                        url=full_next_page_url,
                        callback=self.parse,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                        },
                    )
            else:
                print("No next page")
                # input("Coudn't find next page: INSPECT")

        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    async def parse_product(self, response):
        page = response.meta["playwright_page"]
        print("Parsing PDP")
        await page.wait_for_timeout(7000)
        try:
            timeout = 10000  # Increased timeout
            #! Product Name
            name_selectors = [".pi--title"]
            product_name_element = ""
            for selector in name_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=timeout)
                    product_name_element = await page.query_selector(selector)
                    if product_name_element:
                        break
                except Exception as e:
                    print(f"Error while waiting for Title selector {selector}: {e}, {page.url}")

            product_name = await product_name_element.inner_text() if product_name_element else ""
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
                    print(f"Error while waiting for price selector {selector}: {e}, {page.url}")

            product_price = await price_elements.inner_text() if price_elements else ""
            print(f"Product price: {product_price}")
            
            #! Product Category
            category_selctor = ".b--list li"
            try:
                await page.wait_for_selector(category_selctor, timeout=timeout)
                breadcrumb_elements = await page.query_selector_all(category_selctor)
            except Exception as e:
                print(f"Error while waiting for category selector {category_selctor}: {e}, {page.url}")

            category_path_parts = []
            try:
                for element in breadcrumb_elements:
                    await element.wait_for_selector("a", timeout=timeout)
                    a_tag = await element.query_selector("a")
                    if a_tag:
                        await a_tag.wait_for_selector("span[itemprop='name']", timeout=timeout)
                        span_tag = await a_tag.query_selector("span[itemprop='name']")
                        text = await span_tag.inner_text() if span_tag else ""
                    else:
                        await element.wait_for_selector("span[itemprop='name']", timeout=timeout)
                        span_tag = await element.query_selector("span[itemprop='name']")
                        if span_tag:
                            text = await span_tag.inner_text()
                    if text:
                        category_path_parts.append(text)
            except Exception as e:
                print(f"Error while parsing category: {e}, {page.url}")

            category_path = "/".join(category_path_parts) if category_path_parts else ""
            print(f"Product category: {category_path}")
            
            #! Product Images
            image_selector = "picture#main-img img"
            image_urls_set = set()
            
            try:
                await page.wait_for_selector(image_selector, timeout=timeout)
                image_elements = await page.query_selector_all(image_selector)
                for img in image_elements:
                    src = await img.get_attribute("src")
                    if src:
                        image_urls_set.add(src)
            except Exception as e:
                print(f"Error while parsing images: {e}, {page.url}")
            
            image_urls_list = list(image_urls_set)
            if image_urls_list:
                yield ProductItemExpanded(
                    vendor="metro",
                    sub_vendor="N/A",
                    product_brand=self.brand_name,
                    pdp_url=response.url,
                    image_urls=image_urls_list,
                    product_name=product_name,
                    product_description="N/A",
                    product_category=category_path,
                    product_price=product_price,
                )
            else:
                print(f"No images found at {response.url}")
        except Exception as e:
            print(f"Error processing {response.url}: {e}")
        finally:
            await page.close()
