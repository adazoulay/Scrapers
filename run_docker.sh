#!/bin/bash

# Stop the existing container, if running
docker stop scrapy_container || true

# Remove the existing container, if it exists
docker rm scrapy_container || true

# Build the Docker image
docker build -t my_scrapy_project .

# Run the container from the image with volume mapping
docker run --name scrapy_container -v "$(pwd)/JSON_SCRIPT:/app/ecommerce_scraper/JSON_SCRIPT" my_scrapy_project
