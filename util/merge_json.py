import os
import json


def merge_json_files(directory):
    merged_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            try:
                with open(
                    os.path.join(directory, filename), "r", encoding="utf-8"
                ) as file:
                    data = json.load(file)
                    if isinstance(
                        data, list
                    ):  # Ensuring the file contains a JSON array
                        merged_data.extend(data)
                    else:
                        print(
                            f"Warning: File {filename} does not contain a JSON array."
                        )
            except json.JSONDecodeError:
                print(f"Error reading {filename}: Invalid JSON.")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    try:
        with open("all_competitors_merged.json", "w", encoding="utf-8") as outfile:
            json.dump(merged_data, outfile, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing merged file: {e}")


path = "./JSON"
merge_json_files(path)
