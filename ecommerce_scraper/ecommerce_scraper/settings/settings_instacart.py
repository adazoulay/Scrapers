from pathlib import Path

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
log_dir = Path("/app/logs")
log_dir.mkdir(parents=True, exist_ok=True)

LOG_FILE = log_dir / "instacart.log"  
LOG_ENABLED = True
LOG_LEVEL = "DEBUG"


#! JSON Data
output_dir = Path("/app/data")
output_dir.mkdir(parents=True, exist_ok=True)

FEEDS = {
    str(output_dir / "instacart.json"): {
        "format": "json",
        "encoding": "utf8",
        "indent": 4,
    },
}

