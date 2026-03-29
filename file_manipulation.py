import json
import os
import shutil
import zipfile

class FileManipulator:
    """Utility class for converting EPUBs to ZIPs and extracting them."""

    config_file: str = "config/params.json"
    source_folder: str = ""
    zip_folder_extension: str = ""

    def __init__(self) -> None:
        self.load_config()

    def load_config(self) -> dict:
        """Load configuration from JSON file and set class variables."""
        with open(self.config_file, "r") as f:
            config = json.load(f)

        self.source_folder = config["input_folder"]
        self.zip_folder_extension = config["zip_folder_extension"]
        return config

    def convert_epubs_to_zip(self) -> None:
        """
        Copy all EPUB files from source folder to subfolder and rename to .zip
        """
        print("Converting EPUBs to ZIPs...")
        if(self.source_folder == "" or self.zip_folder_extension == ""):
            self.load_config(self.config_file)

        output_path = os.path.join(self.source_folder, self.zip_folder_extension)
        os.makedirs(output_path, exist_ok=True)

        # Iterate through files in source folder
        for filename in os.listdir(self.source_folder):
            if filename.lower().endswith(".epub"):
                source_file = os.path.join(self.source_folder, filename)
                
                # Skip if it's a directory
                if os.path.isdir(source_file):
                    continue
                
                # Create new filename with .zip extension
                new_filename = os.path.splitext(filename)[0] + ".zip"
                destination_file = os.path.join(output_path, new_filename)
                
                # Skip if file already exists
                if os.path.exists(destination_file):
                    print(f"Skipped: {new_filename} (already exists)")
                    continue
                
                # Copy and rename
                shutil.copy2(source_file, destination_file)
                print(f"Converted: {filename} → {new_filename}")

    def shorten_filenames(self) -> None:
        print("Shortening filenames...")
        if (self.zip_folder_extension ==""):
            self.load_config(self.config_file)

        for filename in os.listdir(os.path.join(self.source_folder, self.zip_folder_extension)):
            """Shorten filename by removing text after the second '--'."""
            parts = filename.split(' -- ')
            if len(parts) >= 3:
                shortened_filename = "".join(parts[:2]) + ".zip"
                os.rename(os.path.join(self.source_folder, self.zip_folder_extension, filename), os.path.join(self.source_folder, self.zip_folder_extension, shortened_filename))
                print(f"Renamed: {filename} → {shortened_filename}")
    


    def unzip_zips_to_folders(self, config_file: str = "config/params.json") -> None:
        """Unzip all .zip files in the output folder into individual folders."""
        print("Unzipping ZIPs to folders...")
        if (self.zip_folder_extension ==""):
            self.load_config(config_file)

        output_path = os.path.join(self.source_folder, self.zip_folder_extension)

        for filename in os.listdir(output_path):
            if filename.lower().endswith(".zip"):
                zip_path = os.path.join(output_path, filename)

                # Skip if it's a directory
                if os.path.isdir(zip_path):
                    continue

                folder_name = os.path.splitext(filename)[0]
                extract_path = os.path.join(output_path, folder_name)

                # Create extraction folder if it doesn't exist
                os.makedirs(extract_path, exist_ok=True)

                # Unzip the file
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Unzipped: {filename} → {folder_name}")

