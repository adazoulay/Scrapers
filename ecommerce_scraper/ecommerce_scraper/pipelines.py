from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request


class EcommerceScraperPipeline:
    def process_item(self, item, spider):
        return item


class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [
            Request(x, meta={"image_id": item.get("image_id")})
            for x in item.get("image_urls", [])
        ]

    def file_path(self, request, response=None, info=None, *, item=None):
        image_id = request.meta["image_id"]
        image_ext = request.url.split(".")[-1]
        # Assuming image_id includes the original 'id' and index
        return f"{image_id}.{image_ext}"
