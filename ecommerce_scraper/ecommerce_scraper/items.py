import scrapy


class ProductItem(scrapy.Item):
    pdp_url = scrapy.Field()
    image_urls = scrapy.Field()
