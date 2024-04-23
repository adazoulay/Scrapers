import json
import uuid


def generate_uuids_for_images(input_file, output_file):

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        print(f"Failed to read {input_file}: {e}")
        return

    # Process each product to replace image URLs with UUID mappings
    for product in data:
        image_urls = product.get("image_urls", [])
        product["image_urls"] = [{url: str(uuid.uuid4())} for url in image_urls]

    # Write the modified data to the output JSON file
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to write {output_file}: {e}")


input_file = "all_competitors_merged_no_dups.json"
output_file = "all_competitors_merged_id.json"

generate_uuids_for_images(input_file, output_file)
