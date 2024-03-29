import scrapy


class ProductItem(scrapy.Item):
    pdp_url = scrapy.Field()
    image_urls = scrapy.Field()


class ProductItemExpanded(scrapy.Item):
    pdp_url = scrapy.Field()
    image_urls = scrapy.Field()
    product_name = scrapy.Field()
    product_description = scrapy.Field()
    product_category = scrapy.Field()
    product_price = scrapy.Field()
