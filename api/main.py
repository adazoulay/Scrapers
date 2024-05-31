from fastapi import FastAPI, HTTPException
import subprocess
import json
from pathlib import Path
import tempfile
import time

app = FastAPI()

@app.get("/health")
async def health():
    return "Up and running"
    


def run_scraper_in_container(container_name, spider_name, brand_name):
    cmd = f"docker exec {container_name} scrapy crawl {spider_name} -a brand_name={brand_name}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error running spider: {result.stderr}")

    tmp_dir = Path(tempfile.gettempdir())
    output_file = tmp_dir / f"{spider_name}.json"

    # Wait for the file to be populated
    timeout = 300  # Timeout in seconds
    start_time = time.time()
    last_size = -1

    while time.time() - start_time < timeout:
        if output_file.exists():
            current_size = output_file.stat().st_size
            if current_size != last_size:
                last_size = current_size
                time.sleep(1)
            else:
                # File size hasn't changed in the last second, assuming it's done
                break
        else:
            time.sleep(1)
    else:
        raise HTTPException(status_code=500, detail="Timeout waiting for scraped data")

    # Read the file
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    return data

@app.get("/scrape/{spider_name}")
async def scrape(spider_name: str, brand_name: str):
    container_name = f"{spider_name}_spider"
    data = run_scraper_in_container(container_name, spider_name, brand_name)
    return data

@app.get("/scrape/all")
async def scrape_multiple(spiders: str, brand_name: str):
    spider_list = spiders.split(',')
    results = {}
    for spider in spider_list:
        container_name = f"{spider}_spider"
        data = run_scraper_in_container(container_name, spider, brand_name)
        results[spider] = data
    return results
