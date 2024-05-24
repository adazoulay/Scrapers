#!/bin/sh

scrapy crawl metro -a brand_name=oikos -s SETTINGS_MODULE=ecommerce_scraper.metro.settings
