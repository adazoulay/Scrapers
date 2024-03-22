import os
import json


def give_id(filename, output_filename=None):
    filepath = os.path.join("JSON_NO_DUPS", filename)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filename}")
        return
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return

    seen_urls = set()

    for idx, item in enumerate(data):
        new_image_urls = [url for url in item["image_urls"] if url not in seen_urls]
        seen_urls.update(new_image_urls)
        item["image_urls"] = new_image_urls
        item["id"] = idx

    output_filename = filename.replace(".json", "_id.json")
    output_filepath = os.path.join("JSON_IDX", output_filename or filename)

    try:
        with open(output_filepath, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error writing to file {output_filepath}: {e}")


for filename in os.listdir("JSON_NO_DUPS"):
    if filename.endswith(".json"):
        give_id(filename)
