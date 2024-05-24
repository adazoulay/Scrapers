from pathlib import Path

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
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

#! LOGS
log_dir = Path("/app/logs")
log_dir.mkdir(parents=True, exist_ok=True)

LOG_FILE = log_dir / "metro.log"  
LOG_ENABLED = True
LOG_LEVEL = "DEBUG"


#! JSON Data
output_dir = Path("/app/data")
output_dir.mkdir(parents=True, exist_ok=True)

FEEDS = {
    str(output_dir / "metro.json"): {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
    },
}

# ! PROXY
SCRAPEOPS_API_KEY = "daea12f2-c861-4373-b3da-47c01582e74f"
SCRAPEOPS_PROXY_ENABLED = True
DOWNLOADER_MIDDLEWARES = {
    "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 725,
}
SCRAPEOPS_PROXY_ENABLED = True