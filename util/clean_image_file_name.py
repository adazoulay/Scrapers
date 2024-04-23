import os


def clean_image_filenames(directory):
    for filename in os.listdir(directory):
        # Check if the filename contains a query parameter
        if "?" in filename:
            # Split the filename on '?' and take the first part, discarding query params
            clean_filename = filename.split("?")[0]
            original_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, clean_filename)
            try:
                os.rename(original_path, new_path)
                print(f"Renamed '{filename}' to '{clean_filename}'")
            except Exception as e:
                print(f"Error renaming '{filename}' to '{clean_filename}': {e}")


# Specify the directory containing your images
image_directory = "./all_images_competitors"
clean_image_filenames(image_directory)
