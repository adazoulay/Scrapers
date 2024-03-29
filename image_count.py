import os
import json


def count_image_urls(directory):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    total = 0
    for filename in os.listdir(directory):

        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "r") as file:
                    data = json.load(file)
                    image_count = sum(len(item.get("image_urls", [])) for item in data)
                    total += image_count
                    print(f"{filename}: {image_count}")

            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

        else:
            print(f"Skipping non-JSON file: {filename}")

    print(f"Total images: {total}")


count_image_urls("JSON_NO_DUPS")
# count_image_urls("JSON")
# count_image_urls("JSON_V1/JSON_NO_DUPS")
