~# cookbooks

A Python application for parsing and serving EPUB cookbook files with a web interface.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Unit Tests

### Test Cookbook Metadata
Tests metadata parsing, OPF file detection, and web page accessibility:

```bash
# Run all tests
python -m unittest test_cookbook_metadata.py -v

# Run specific test
python -m unittest test_cookbook_metadata.TestCookBookMetadata.test_all_cookbooks_have_opf -v

# Run with less verbose output
python -m unittest test_cookbook_metadata.py
```

### Available Tests
- `test_all_cookbooks_have_opf` - Verify each cookbook has exactly one OPF file
- `test_all_cookbooks_have_title` - Verify each cookbook has a title
- `test_all_cookbooks_have_author` - Verify each cookbook has an author
- `test_all_cookbooks_have_cover_photos` - Verify each cookbook has a cover image
- `test_web_app_index_page` - Verify the web app index page loads
- `test_all_cookbook_pages_no_404` - Verify all pages are accessible without 404 errors
- `test_first_page_of_each_cookbook` - Verify the first page of each cookbook is accessible

## Running the Web App

Start the development server:
```bash
python web_app.py
```

The app will be available at `http://127.0.0.1:5000/`

## Project Structure

- `cookbook_metadata.py` - Core metadata parser for EPUB files
- `web_app.py` - Flask web application for serving cookbooks
- `test_cookbook_metadata.py` - Unit tests
- `config/params.json` - Configuration file with cookbook folder path
- `app.py` - Terminal-based book information display