from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class EcommerceScraperPipeline:
    def process_item(self, item, spider):
        return item


class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item["image_urls"]:
            yield Request(image_url, meta={"uuid": item["uuid"]})

    def file_path(self, request, response=None, info=None, item=None):
        # Use the UUID from the meta as the filename
        uuid = request.meta["uuid"]
        image_ext = request.url.split(".")[-1]
        return f"{uuid}.{image_ext}"
