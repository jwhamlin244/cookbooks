import unittest
import os
from cookbook_metadata import CookBookMetadataParser

class TestCookBookMetadata(unittest.TestCase):

    def setUp(self):
        self.cm = CookBookMetadataParser()
        self.cm.load_config()
        self.cookbook_folder = self.cm.cookbook_folder

    def test_all_cookbooks_have_opf(self):
        """Test that each cookbook folder contains exactly one .opf file."""
        for f in os.listdir(self.cookbook_folder):
            folder_path = os.path.join(self.cookbook_folder, f)
            if os.path.isdir(folder_path):
                opf_list = self.cm.get_opf_file(folder_path)
                self.assertEqual(len(opf_list), 1, f"Cookbook folder '{f}' does not contain exactly one .opf file")

    def test_all_cookbooks_have_title(self):
        """Test that each cookbook has a valid title in its .opf file."""
        for f in os.listdir(self.cookbook_folder):
            folder_path = os.path.join(self.cookbook_folder, f)
            if os.path.isdir(folder_path):
                opf_list = self.cm.get_opf_file(folder_path)
                if opf_list:
                    title = self.cm.get_title(opf_list[0])
                    self.assertTrue(title, f"Cookbook folder '{f}' has an .opf file but it does not contain a title")

    def test_all_cookbooks_have_author(self):
        """Test that each cookbook has a valid author in its .opf file."""
        for f in os.listdir(self.cookbook_folder):
            folder_path = os.path.join(self.cookbook_folder, f)
            if os.path.isdir(folder_path):
                opf_list = self.cm.get_opf_file(folder_path)
                if opf_list:
                    author = self.cm.get_author(opf_list[0])
                    self.assertTrue(author, f"Cookbook folder '{f}' has an .opf file but it does not contain an author")

    def test_all_cookbooks_have_cover_photos(self):
        """Test that each cookbook has a valid cover photo in its .opf file."""
        for f in os.listdir(self.cookbook_folder):
            folder_path = os.path.join(self.cookbook_folder, f)
            if os.path.isdir(folder_path):
                opf_list = self.cm.get_opf_file(folder_path)
                if opf_list:
                    cover = self.cm.get_cover(folder_path)
                    self.assertTrue(cover, f"Cookbook folder '{f}' has an .opf file but it does not contain a cover photo")

    def test_web_app_index_page(self):
        """Test that the web app index page loads without error."""
        try:
            from web_app import app
            client = app.test_client()
            response = client.get('/')
            self.assertEqual(response.status_code, 200, "Index page should return 200")
        except ImportError:
            self.skipTest("web_app module not available")

    def test_all_cookbook_pages_no_404(self):
        """Test that all pages in all cookbooks are accessible without 404 errors."""
        try:
            from web_app import app
            client = app.test_client()
        except ImportError:
            self.skipTest("web_app module not available")
        
        failed_pages = []
        
        for folder in os.listdir(self.cookbook_folder):
            cookbook_path = os.path.join(self.cookbook_folder, folder)
            if not os.path.isdir(cookbook_path):
                continue
            
            book_id = folder
            pages = self._get_spine_pages(cookbook_path)
            
            if not pages:
                continue
            
            for page_href in pages:
                url = f'/page/{book_id}/{page_href}/1'
                response = client.get(url)
                
                if response.status_code == 404:
                    failed_pages.append({
                        'book_id': book_id,
                        'page': page_href,
                        'url': url,
                        'status': response.status_code
                    })
        
        if failed_pages:
            error_msg = f"Found {len(failed_pages)} page(s) with 404 errors:\n"
            for fail in failed_pages:
                error_msg += f"  - {fail['book_id']}: {fail['page']}\n"
            self.fail(error_msg)

    def test_first_page_of_each_cookbook(self):
        """Test that the first page of each cookbook is accessible."""
        try:
            from web_app import app
            client = app.test_client()
        except ImportError:
            self.skipTest("web_app module not available")
        
        failed_first_pages = []
        
        for folder in os.listdir(self.cookbook_folder):
            cookbook_path = os.path.join(self.cookbook_folder, folder)
            if not os.path.isdir(cookbook_path):
                continue
            
            opf_list = self.cm.get_opf_file(cookbook_path)
            if not opf_list:
                continue
            
            first_page = self.cm.get_first_page(opf_list[0])
            book_id = folder
            
            if first_page:
                url = f'/page/{book_id}/{first_page}/1'
                response = client.get(url)
                
                if response.status_code != 200:
                    failed_first_pages.append({
                        'book_id': book_id,
                        'first_page': first_page,
                        'status': response.status_code
                    })
        
        if failed_first_pages:
            error_msg = f"Found {len(failed_first_pages)} cookbook(s) with inaccessible first page:\n"
            for fail in failed_first_pages:
                error_msg += f"  - {fail['book_id']}: {fail['first_page']} ({fail['status']})\n"
            self.fail(error_msg)

    def _get_spine_pages(self, cookbook_path):
        """Helper method to get all pages in the book's spine."""
        opf_list = self.cm.get_opf_file(cookbook_path)
        if not opf_list:
            return []
        
        pages = self.cm.get_spine(opf_list[0])
        return pages if pages else []

if __name__ == '__main__':
    unittest.main()