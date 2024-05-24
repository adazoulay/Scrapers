#!/bin/sh

scrapy crawl walmart -a brand_name=oikos -s SETTINGS_MODULE=ecommerce_scraper.walmart.settings