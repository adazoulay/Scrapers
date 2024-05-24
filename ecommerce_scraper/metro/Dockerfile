# ecommerce_scraper/metro/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY ecommerce_scraper /app/ecommerce_scraper

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN playwright install
RUN playwright install-deps    

WORKDIR /app/ecommerce_scraper/ecommerce_scraper

COPY ecommerce_scraper/metro/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
