BOT_NAME = "ecommerce_scraper"
SPIDER_MODULES = ["ecommerce_scraper.spiders"]
NEWSPIDER_MODULE = "ecommerce_scraper.spiders"


ROBOTSTXT_OBEY = False
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"

#! Cache
HTTPCACHE_ENABLED = False

#! Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"

#! Headless Browser
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": False}

#! LOGS
LOG_ENABLED = True
LOG_FILE = "logs.txt"
LOG_LEVEL = "DEBUG"

#! Image store
# ITEM_PIPELINES = {
#     "scrapy.pipelines.images.ImagesPipeline": 1,
# }
# IMAGES_STORE = "saved_images"

#! JSON Data
FEEDS = {
    "image_scrape.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
    },
}

# FEEDS = {
#     "instacart_iogo.json": {
#         "format": "json",
#         "encoding": "utf8",
#         "store_empty": False,
#         "fields": None,
#         "indent": 4,
#     },
#     "instacart_iogo.csv": {
#         "format": "csv",
#         "encoding": "utf8",
#         "store_empty": False,
#         "fields": None,
#     },
# }

# ! PROXY
# SCRAPEOPS_API_KEY = "daea12f2-c861-4373-b3da-47c01582e74f"
# SCRAPEOPS_PROXY_ENABLED = True
# DOWNLOADER_MIDDLEWARES = {
#     "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 725,
# }
# SCRAPEOPS_PROXY_ENABLED = True


# # # DOWNLOADER_MIDDLEWARES = {
# # #     "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,  # 300
# # #     "rotating_proxies.middlewares.BanDetectionMiddleware": 620,  # 301
# # # }

# # # ROTATING_PROXY_LIST_PATH = "proxies.txt"
