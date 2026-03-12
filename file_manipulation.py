import json
import os
import shutil
from pathlib import Path

def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        return json.load(f)

def convert_epubs_to_zip(config_file: str = "config.json") -> None:
    """
    Copy all EPUB files from source folder to subfolder and rename to .zip
    """
    config = load_config(config_file)
    source_folder = config["input_folder"]
    output_folder = config["output_folder"]
    
    # Create full path for output folder
    output_path = os.path.join(source_folder, output_folder)
    
    # Create output subfolder if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Iterate through files in source folder
    for filename in os.listdir(source_folder):
        if filename.lower().endswith(".epub"):
            source_file = os.path.join(source_folder, filename)
            
            # Skip if it's a directory
            if os.path.isdir(source_file):
                continue
            
            # Create new filename with .zip extension
            new_filename = os.path.splitext(filename)[0] + ".zip"
            destination_file = os.path.join(output_path, new_filename)
            
            # Copy and rename
            shutil.copy2(source_file, destination_file)
            print(f"Converted: {filename} → {new_filename}")

if __name__ == "__main__":
    convert_epubs_to_zip()