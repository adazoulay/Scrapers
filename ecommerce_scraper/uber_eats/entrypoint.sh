#!/bin/sh

scrapy crawl uber_eats -a brand_name=oikos -s SETTINGS_MODULE=ecommerce_scraper.uber_eats.settings
