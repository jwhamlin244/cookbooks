import json
import os

class CookBookMetadataParser:
    config_file = "config/params.json"
    cookbook_folder = ""

    def __init__(self):
        return
    
    def get_cookbook_folder(self) -> str:
        """Returns the path to the cookbook folder from the config file."""
        if self.cookbook_folder == "":
            self.load_config()
        return self.cookbook_folder
    
    def load_config(self) -> None:
        """Load configuration from JSON file and set class variables."""
        with open(self.config_file, "r") as f:
            config = json.load(f)

        self.cookbook_folder = config["cookbook_folder"]
        return
    
    def get_opf_file(self, dir: str) -> list:
        """Returns a list of all possible opf files in a directory (cookbook)"""
        opf_files = []
        found_opf_file = False
        if os.path.isdir(dir):
            for root, dirs, files in os.walk(dir):
                for file in files:
                    if file.endswith('.opf'):
                        opf_path = os.path.join(root, file)
                        if found_opf_file:
                            print(f"Warning: Multiple OPF files found in {dir}")
                        opf_files.append(opf_path)
                        found_opf_file = True
            if not found_opf_file:
                print(f"Warning: opf file not found in {dir}")
        
        return opf_files
    
    def get_title(self, opf_path: str) -> str:
        """Returns the title of the book given opf file path"""
        import xml.etree.ElementTree as ET

        # Check that the file is a .opf file
        if not opf_path.endswith('.opf'):
            print(f"Error: {opf_path} is not an .opf file")
            return ""
        
        # Parse the .opf file to get the title
        try:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            # OPF files use Dublin Core metadata
            title_elem = root.find('.//{http://purl.org/dc/elements/1.1/}title')
            if title_elem is not None:
                return title_elem.text.strip()
            else:
                print(f"Error: Title tag not found in {opf_path}")
                return ""
        except Exception as e:
            print(f"Error reading {opf_path}: {e}")
            return ""
    
    def get_author(self, opf_path: str) -> str:
        """Returns the author of the book given opf file path"""
        import xml.etree.ElementTree as ET

        # Check that the file is a .opf file
        if not opf_path.endswith('.opf'):
            print(f"Error: {opf_path} is not an .opf file")
            return ""
        
        # Parse the .opf file to get the author
        try:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            # OPF files use Dublin Core metadata
            author_elem = root.find('.//{http://purl.org/dc/elements/1.1/}creator')
            if author_elem is not None:
                return author_elem.text.strip()
            else:
                print(f"Error: Creator tag not found in {opf_path}")
                return ""
        except Exception as e:
            print(f"Error reading {opf_path}: {e}")
            return ""
    
    def get_cover(self, opf_path: str) -> str:
        """Returns the path to the cover image for the book in the given directory"""
        import xml.etree.ElementTree as ET

        # Check that the file is a .opf file
        if not opf_path.endswith('.opf'):
            print(f"Error: {opf_path} is not an .opf file")
            return ""

        try:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            
            # Define the OPF namespace
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            
            # Find the meta element with name="cover"
            meta_elem = root.find('.//opf:meta[@name="cover"]', ns)
            if meta_elem is None:
                print(f"Error: Cover meta tag not found in {opf_path}")
                return ""
            
            cover_id = meta_elem.get('content')
            if not cover_id:
                print(f"Error: Cover meta tag has no content in {opf_path}")
                return ""
            
            # Find the item with the matching id
            item_elem = root.find(f'.//opf:item[@id="{cover_id}"]', ns)
            if item_elem is None:
                print(f"Error: Cover item with id '{cover_id}' not found in {opf_path}")
                return ""
            
            href = item_elem.get('href')
            if not href:
                print(f"Error: Cover item has no href in {opf_path}")
                return ""
            
            # Construct the full path relative to the opf file's directory
            opf_dir = os.path.dirname(opf_path)
            cover_path = os.path.join(opf_dir, href)
            
            # Check if the file exists
            if os.path.exists(cover_path):
                return cover_path
            else:
                print(f"Error: Cover image file not found at {cover_path}")
                return ""
        
        except Exception as e:
            print(f"Error reading {opf_path}: {e}")
            return ""
    

    def get_spine(self, opf_path: str) -> list:
        """Returns a list of all pages in the book's spine"""
        import xml.etree.ElementTree as ET

        if not opf_path.endswith('.opf'):
            print(f"Error: {opf_path} is not an .opf file")
            return []
        
        try:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            
            spine = root.find('.//opf:spine', ns)
            if spine is None:
                print(f"Error: Spine not found in {opf_path}")
                return []
            
            itemrefs = spine.findall('opf:itemref', ns)
            hrefs = []
            for itemref in itemrefs:
                idref = itemref.get('idref')
                item = root.find(f'.//opf:item[@id="{idref}"]', ns)
                if item is not None:
                    href = item.get('href')
                    if href:
                        hrefs.append(href)
            
            return hrefs
        except Exception as e:
            print(f"Error reading {opf_path}: {e}")
            return []



