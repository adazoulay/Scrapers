BOT_NAME = "ecommerce_scraper_instacart"
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
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

#! LOGS
LOG_ENABLED = True
LOG_FILE = "instacart.log"
LOG_LEVEL = "DEBUG"


#! JSON Data
FEEDS = {
    "instacart.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
    },
}

