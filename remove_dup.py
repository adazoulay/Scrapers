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
    output_filepath = os.path.join("JSON_NO_DUPS", output_filename or filename)

    try:
        with open(output_filepath, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error writing to file {output_filepath}: {e}")


remove_dups("metro.json")
# remove_dups("loblaws.json")
# remove_dups("walmart.json")


def combine_and_deduplicate_json(file_path1, file_path2, output_file_path):
    def load_data(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file {file_path}")
            return []
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []

    def remove_duplicates(data):
        seen_urls = set()
        for item in data:
            new_image_urls = [url for url in item["image_urls"] if url not in seen_urls]
            seen_urls.update(new_image_urls)
            item["image_urls"] = new_image_urls
        return data

    data1 = load_data(file_path1)
    data2 = load_data(file_path2)
    combined_data = data1 + data2

    deduplicated_data = remove_duplicates(combined_data)

    try:
        with open(output_file_path, "w") as file:
            json.dump(deduplicated_data, file, indent=4)
    except Exception as e:
        print(f"Error writing to file {output_file_path}: {e}")


# combine_and_deduplicate_json(
#     "JSON/uber_eats_MR.json",
#     "JSON/uber_eats_T.json",
#     "JSON_NO_DUPS/uber_eats_merged.json",
# )
