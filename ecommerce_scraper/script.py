from twisted.internet import asyncioreactor

asyncioreactor.install()

import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
from scrapy.signalmanager import dispatcher
from twisted.internet import reactor, defer

# Import your spider classes
from ecommerce_scraper.spiders.instacart import InstacartSpider
from ecommerce_scraper.spiders.loblaws import LoblawsSpider
from ecommerce_scraper.spiders.metro import MetroSpider
from ecommerce_scraper.spiders.uber_eats import UberEatsSpider
from ecommerce_scraper.spiders.walmart import WalmartSpider


from twisted.internet import asyncioreactor

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from ecommerce_scraper.spiders.instacart import InstacartSpider
from ecommerce_scraper.spiders.loblaws import LoblawsSpider
from ecommerce_scraper.spiders.metro import MetroSpider
from ecommerce_scraper.spiders.uber_eats import UberEatsSpider
from ecommerce_scraper.spiders.walmart import WalmartSpider


# if not reactor._installed:
#     asyncioreactor.install()


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
        "/app/ecommerce_scraper/JSON_SCRIPT/items_no_proxy.csv": {"format": "csv"},
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

brand_name = "oikos"


def crawl():

    # runner_no_proxy.crawl(LoblawsSpider, brand_name=brand_name)
    # runner_no_proxy.crawl(UberEatsSpider, brand_name=brand_name)
    # runner_no_proxy.crawl(InstacartSpider, brand_name=brand_name)

    runner_with_proxy.crawl(MetroSpider, brand_name=brand_name)
    # runner_with_proxy.crawl(WalmartSpider, brand_name=brand_name)

    d = defer.DeferredList([runner_no_proxy.join(), runner_with_proxy.join()])
    d.addBoth(lambda _: reactor.stop())

    reactor.run()


if __name__ == "__main__":
    print("STARTING SCRAPING")
    crawl()
    print("END OF SCRAPING")

# def spider_error_handler(failure, response, spider):
#     print(f"Error processing: {response.url}\nFailure: {failure.getErrorMessage()}")


# custom_settings = {
#     "BOT_NAME": "ecommerce_scraper",
#     "SPIDER_MODULES": ["ecommerce_scraper.spiders"],
#     "NEWSPIDER_MODULE": "ecommerce_scraper.spiders",
#     "ROBOTSTXT_OBEY": False,
#     "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
#     "FEED_EXPORT_ENCODING": "utf-8",
#     "HTTPCACHE_ENABLED": False,
#     "DOWNLOAD_HANDLERS": {
#         "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#         "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     },
#     "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
#     "PLAYWRIGHT_BROWSER_TYPE": "chromium",
#     "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
#     # "LOG_ENABLED": True,
#     # "LOG_FILE": "logs.txt",
#     # "LOG_LEVEL": "DEBUG",
#     "FEEDS": {
#         "/app/ecommerce_scraper/JSON_SCRIPT/items.csv": {"format": "csv"},
#     },
# }


# def run_spiders(brand_name):
#     dispatcher.connect(spider_error_handler, signal=signals.spider_error)

#     spider_classes = [
#         # InstacartSpider,
#         # LoblawsSpider,
#         # MetroSpider,
#         UberEatsSpider,
#         # WalmartSpider,
#     ]

#     spiders_requiring_proxies = [
#         spider for spider in spider_classes if getattr(spider, "requires_proxy", False)
#     ]
#     spiders_not_requiring_proxies = [
#         spider
#         for spider in spider_classes
#         if not getattr(spider, "requires_proxy", False)
#     ]

#     print(f"===== Spider With  proxy: {spiders_requiring_proxies}")
#     print(f"===== Spider No proxy: {spiders_not_requiring_proxies}")

#     # settings = get_project_settings()
#     # print(f"======= SETIINGS: {settings}")

#     process = CrawlerProcess(settings=custom_settings)

#     for spider_class in spiders_not_requiring_proxies:
#         print(f"NO PROXY:  STARTING {getattr(spider_class, 'name')}")
#         process.crawl(spider_class, brand_name=brand_name)

#     # @defer.inlineCallbacks
#     # def run_sequential_spiders():
#     #     for spider_class in spiders_requiring_proxies:
#     #         print(f"PROXY: STARTING {getattr(spider_class, 'name')}")
#     #         yield process.crawl(spider_class, brand_name=brand_name)
#     #     reactor.stop()

#     process.start(stop_after_crawl=False)

#     # if spiders_requiring_proxies:
#     #     print(f"NO PROXY:  STARTING run_sequential_spiders")
#     #     run_sequential_spiders()

#     if not reactor.running:
#         reactor.run()


# if __name__ == "__main__":
#     brand_name = "oikos"
#     print("STARTING SCRAPING")
#     run_spiders(brand_name)
#     print("END OF SCRAPING")
