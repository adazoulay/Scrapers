import scrapy
import uuid


class ProductItem(scrapy.Item):
    pdp_url = scrapy.Field()
    image_urls = scrapy.Field()


class ProductItemExpanded(scrapy.Item):
    id = scrapy.Field(serializer=lambda x: str(x), default=uuid.uuid4)
    vendor = scrapy.Field()
    sub_vendor = scrapy.Field()
    pdp_url = scrapy.Field()
    image_urls = scrapy.Field()
    product_brand = scrapy.Field()
    product_name = scrapy.Field()
    product_description = scrapy.Field()
    product_category = scrapy.Field()
    product_price = scrapy.Field()
