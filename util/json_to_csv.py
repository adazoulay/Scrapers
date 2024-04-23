import csv
import json

# Load the JSON data
input_filename = "all_competitors_merged_id.json"
with open(input_filename, "r", encoding="utf-8") as file:
    data = json.load(file)

# Define the CSV output file
output_filename = "competitor_products_with_images.csv"
with open(output_filename, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(
        [
            "vendor",
            "sub_vendor",
            "product_brand",
            "product_name",
            "pdp_url",
            "product_description",
            "product_category",
            "product_price",
            "image_url",
            "image_uuid",
        ]
    )

    # Iterate through each product in the JSON data
    for product in data:
        # Extract product information
        vendor = product.get("vendor", "N/A")
        sub_vendor = product.get("sub_vendor", "N/A")
        product_brand = product.get("product_brand", "")
        product_name = product.get("product_name", "")
        pdp_url = product.get("pdp_url", "")
        product_description = product.get("product_description", "").replace("\n", " ")
        product_category = product.get("product_category", "")
        product_price = product.get("product_price", "")

        # Iterate through each image_url object in the image_urls list
        for image_info in product["image_urls"]:
            for image_url, uuid in image_info.items():
                # Write product and image information to CSV
                writer.writerow(
                    [
                        vendor,
                        sub_vendor,
                        product_brand,
                        product_name,
                        pdp_url,
                        product_description,
                        product_category,
                        product_price,
                        image_url,
                        uuid,
                    ]
                )
