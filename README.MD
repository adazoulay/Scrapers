### Running spiders

- `cd` into ecommerce_scraper dir
- To run scraper json: `scrapy crawl spider_name -o output_file.json`
- To run scraper csv: `scrapy crawl spider_name -o output_file.csv`

#### Note:

- In some spiders (uber_eats, instacart) uncomment desrired url to target desired region (Montreal, Toronto)
- Some spiders require the proxy to be dissabled, usually written in comment at the top of the spider

### Getting images

- Go to `get_images.py` and update path: `with open("../JSON/metro.json", "r") as file:  #! Change here`
- Uncomment `ITEM_PIPELINES` and `IMAGES_STORE` in `settings.py`
