# ecommerce_scraper/instacart/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY ecommerce_scraper /app/ecommerce_scraper

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN playwright install
RUN playwright install-deps    

WORKDIR /app/ecommerce_scraper/ecommerce_scraper

ENV SCRAPY_SETTINGS_MODULE=ecommerce_scraper.settings.settings_instacart

EXPOSE 8080

CMD ["tail", "-f", "/dev/null"]
