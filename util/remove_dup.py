import os
import json


def remove_dups(filename):
    filepath = os.path.join("JSON", filename)

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

    for item in data:
        new_image_urls = [url for url in item["image_urls"] if url not in seen_urls]
        seen_urls.update(new_image_urls)
        item["image_urls"] = new_image_urls
    output_filename = filename.replace(".json", "_no_dups.json")
    output_filepath = os.path.join("./", output_filename or filename)

    try:
        with open(output_filepath, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error writing to file {output_filepath}: {e}")


remove_dups("all_competitors_merged.json")
# remove_dups("loblaws.json")
# remove_dups("walmart.json")
