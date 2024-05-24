#!/bin/sh

scrapy crawl instacart -a brand_name=oikos -s SETTINGS_MODULE=ecommerce_scraper.instacart.settings
