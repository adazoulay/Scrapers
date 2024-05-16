api_key = "scp-live-1c8282c63f104c0f94aaa49cdc2e64e4"
base_url = "https://api.scrapfly.io/scrape"
params = {
    "url": "https://www.ubereats.com/search?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMkhvdXNlJTIwb24lMjBQYXJsaWFtZW50JTIyJTJDJTIycmVmZXJlbmNlJTIyJTNBJTIyMDdiYzE4ZmYtYmMzMS1iZjcxLTI3MTYtYzY3YzUwZjEzNmJiJTIyJTJDJTIycmVmZXJlbmNlVHlwZSUyMiUzQSUyMnViZXJfcGxhY2VzJTIyJTJDJTIybGF0aXR1ZGUlMjIlM0E0My42NjM1ODM1JTJDJTIybG9uZ2l0dWRlJTIyJTNBLTc5LjM2Nzk1OTklN0Q%3D&q=oikos&sc=SEARCH_BAR&searchType=GLOBAL_SEARCH&vertical=ALL",
    "country": "ca",
    "render_js": "true",
    "proxy_pool": "public_residential_pool",
    "key": api_key,
    "render_js": "true",
}

from urllib.parse import urlencode

full_url = base_url + "?" + urlencode(params)

print(full_url)
