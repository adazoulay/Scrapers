try:
    import twisted.internet.asyncioreactor

    twisted.internet.asyncioreactor.install()
except Exception as e:
    print(f"Exception when installing reactorL {e}")
    pass

from twisted.internet import reactor, defer

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from ecommerce_scraper.spiders.instacart import InstacartSpider
from ecommerce_scraper.spiders.loblaws import LoblawsSpider
from ecommerce_scraper.spiders.metro import MetroSpider
from ecommerce_scraper.spiders.uber_eats import UberEatsSpider
from ecommerce_scraper.spiders.walmart import WalmartSpider


configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

settings_no_proxy = {
    "BOT_NAME": "ecommerce_scraper",
    "SPIDER_MODULES": ["ecommerce_scraper.spiders"],
    "NEWSPIDER_MODULE": "ecommerce_scraper.spiders",
    "ROBOTSTXT_OBEY": False,
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    "FEED_EXPORT_ENCODING": "utf-8",
    "HTTPCACHE_ENABLED": False,
    "DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    "FEEDS": {
        # "/app/ecommerce_scraper/JSON_SCRIPT/items.csv": {"format": "csv"},
        "/app/ecommerce_scraper/JSON_SCRIPT/items.json": {"format": "json"},
    },
}

settings_with_proxy = dict(settings_no_proxy)
settings_with_proxy.update(
    {
        "SCRAPEOPS_API_KEY": "daea12f2-c861-4373-b3da-47c01582e74f",
        "SCRAPEOPS_PROXY_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 725,
        },
    }
)

runner_no_proxy = CrawlerRunner(settings_no_proxy)
runner_with_proxy = CrawlerRunner(settings_with_proxy)


def crawl(brand_name):
    runner_no_proxy.crawl(LoblawsSpider, brand_name=brand_name)
    runner_no_proxy.crawl(UberEatsSpider, brand_name=brand_name)
    runner_no_proxy.crawl(InstacartSpider, brand_name=brand_name)

    runner_with_proxy.crawl(MetroSpider, brand_name=brand_name)
    # runner_with_proxy.crawl(WalmartSpider, brand_name=brand_name)

    d = defer.DeferredList([runner_no_proxy.join(), runner_with_proxy.join()])
    d.addBoth(lambda _: reactor.stop())

    reactor.run()


if __name__ == "__main__":
    brand_name = "oikos"
    crawl(brand_name=brand_name)
