import os

from file_manipulation import FileManipulator
from cookbook_metadata import CookBookMetadataParser

if __name__ == "__main__":
    fm = FileManipulator()
    #fm.convert_epubs_to_zip()
    #fm.shorten_filenames()
    #fm.unzip_zips_to_folders()

    cm = CookBookMetadataParser()
    cookbook_folder = cm.get_cookbook_folder()
    for f in os.listdir(cookbook_folder):
        cookbook = os.path.join(cookbook_folder, f)
        if os.path.isdir(cookbook):
            opf_list = cm.get_opf_file(cookbook)
            title = cm.get_title(opf_list[0]) 
            author = cm.get_author(opf_list[0])
            print(f"Title: {title}, Author: {author}")
        
