FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps    

WORKDIR /app/ecommerce_scraper

EXPOSE 8080

CMD ["python3", "script.py"]
