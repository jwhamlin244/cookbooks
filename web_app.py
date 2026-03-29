from flask import Flask, render_template_string, send_from_directory, Response
import os
from cookbook_metadata import CookBookMetadataParser
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    cm = CookBookMetadataParser()
    cm.load_config()
    cookbook_folder = cm.cookbook_folder
    books = []
    for f in os.listdir(cookbook_folder):
        cookbook = os.path.join(cookbook_folder, f)
        if os.path.isdir(cookbook):
            opf_list = cm.get_opf_file(cookbook)
            if opf_list:
                opf_path = opf_list[0]
                title = cm.get_title(opf_path)
                author = cm.get_author(opf_path)
                cover = cm.get_cover(cookbook)
                first_page = cm.get_first_page(opf_path)
                opf_dir = os.path.dirname(opf_path)
                books.append({'title': title, 'author': author, 'cover': cover, 'first_page': first_page, 'opf_dir': opf_dir, 'book_id': f})

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cookbook Library</title>
        <style>
            .book {
                border: 1px solid #ddd;
                padding: 10px;
                margin: 10px;
                width: 200px;
                display: inline-block;
                vertical-align: top;
                text-align: center;
            }
            .cover {
                max-width: 150px;
                max-height: 200px;
            }
            .title {
                font-weight: bold;
                margin-top: 5px;
            }
            .author {
                font-style: italic;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <h1>Cookbook Library</h1>
        {% for book in books %}
        <div class="book">
            {% if book.cover and book.first_page %}
            <a href="/page/{{ book.book_id }}/{{ book.first_page }}">
                <img src="/cover/{{ book.cover }}" class="cover" alt="Cover">
            </a>
            {% elif book.cover %}
            <img src="/cover/{{ book.cover }}" class="cover" alt="Cover">
            {% endif %}
            <div class="title">{{ book.title }}</div>
            <div class="author">by {{ book.author }}</div>
        </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html, books=books)

@app.route('/cover/<path:filepath>')
def serve_cover(filepath):
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename)

@app.route('/css/<book_id>/<path:filepath>')
def serve_css(book_id, filepath):
    cm = CookBookMetadataParser()
    cm.load_config()
    cookbook_folder = cm.cookbook_folder
    cookbook_path = os.path.join(cookbook_folder, book_id)
    
    opf_list = cm.get_opf_file(cookbook_path)
    if not opf_list:
        return "No OPF found", 404
    
    opf_dir = os.path.dirname(opf_list[0])
    return send_from_directory(opf_dir, filepath, mimetype='text/css')

@app.route('/img/<book_id>/<path:filepath>')
def serve_img(book_id, filepath):
    cm = CookBookMetadataParser()
    cm.load_config()
    cookbook_folder = cm.cookbook_folder
    cookbook_path = os.path.join(cookbook_folder, book_id)
    
    opf_list = cm.get_opf_file(cookbook_path)
    if not opf_list:
        return "No OPF found", 404
    
    opf_dir = os.path.dirname(opf_list[0])
    return send_from_directory(opf_dir, filepath)

@app.route('/page/<book_id>/<path:filename>')
def serve_page(book_id, filename):
    cm = CookBookMetadataParser()
    cm.load_config()
    cookbook_folder = cm.cookbook_folder
    cookbook_path = os.path.join(cookbook_folder, book_id)
    
    opf_list = cm.get_opf_file(cookbook_path)
    if not opf_list:
        return "No OPF found", 404
    
    opf_dir = os.path.dirname(opf_list[0])
    
    # Read the current page content
    page_path = os.path.join(opf_dir, filename)
    if not os.path.exists(page_path):
        return "Page not found", 404
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse and modify links
    soup = BeautifulSoup(content, 'html.parser')
    page_dir = os.path.dirname(page_path)
    
    def resolve_href(href):
        if href.startswith('http') or href.startswith('/'):
            return href  # Absolute or our routes
        # Resolve relative to page_dir
        full_path = os.path.normpath(os.path.join(page_dir, href))
        # Make relative to opf_dir
        try:
            rel_path = os.path.relpath(full_path, opf_dir)
            return rel_path
        except ValueError:
            return href  # Fallback
    
    # Update CSS links
    for link in soup.find_all('link', rel='stylesheet'):
        if link.get('href'):
            resolved = resolve_href(link['href'])
            link['href'] = f'/css/{book_id}/{resolved}'
    
    # Update image sources
    for img in soup.find_all('img'):
        if img.get('src'):
            resolved = resolve_href(img['src'])
            img['src'] = f'/img/{book_id}/{resolved}'
    
    # Update other relative links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if not (href.startswith('http') or href.startswith('/')):
            a['href'] = f'/page/{book_id}/{href}'
    
    content = str(soup)
    
    # Find the OPF file
    opf_files = [f for f in os.listdir(opf_dir) if f.endswith('.opf')]
    if opf_files:
        opf_path = os.path.join(opf_dir, opf_files[0])
        
        # Parse the spine
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(opf_path)
            root = tree.getroot()
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            
            spine = root.find('.//opf:spine', ns)
            if spine is not None:
                itemrefs = spine.findall('opf:itemref', ns)
                hrefs = []
                for itemref in itemrefs:
                    idref = itemref.get('idref')
                    item = root.find(f'.//opf:item[@id="{idref}"]', ns)
                    if item is not None:
                        href = item.get('href')
                        if href:
                            hrefs.append(href)
                
                # Find next page
                try:
                    current_index = hrefs.index(filename)
                    next_index = current_index + 1
                    if next_index < len(hrefs):
                        next_href = hrefs[next_index]
                        next_link = f'<div style="position: fixed; bottom: 10px; right: 10px;"><a href="/page/{book_id}/{next_href}" style="padding: 10px; background: #007bff; color: white; text-decoration: none;">Next</a></div>'
                    else:
                        next_link = '<div style="position: fixed; bottom: 10px; right: 10px;">End of book</div>'
                except ValueError:
                    next_link = '<div style="position: fixed; bottom: 10px; right: 10px;">Navigation error</div>'
                
                # Add next link to content
                if '</body>' in content:
                    content = content.replace('</body>', f'{next_link}</body>')
                else:
                    content += next_link
        
        except Exception as e:
            print(f"Error parsing OPF: {e}")
    
    return Response(content, mimetype='application/xhtml+xml')


def get_next_spine_item(opf_path, current_filename):
    """Get the next item in the spine after current_filename."""
    import xml.etree.ElementTree as ET
    
    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        spine = root.find('.//opf:spine', ns)
        if spine is None:
            return None
        
        itemrefs = spine.findall('opf:itemref', ns)
        hrefs = []
        for itemref in itemrefs:
            idref = itemref.get('idref')
            item = root.find(f'.//opf:item[@id="{idref}"]', ns)
            if item is not None:
                href = item.get('href')
                if href:
                    hrefs.append(href)
        
        try:
            current_index = hrefs.index(current_filename)
            next_index = current_index + 1
            if next_index < len(hrefs):
                return hrefs[next_index]
        except ValueError:
            pass
    except Exception:
        pass
    return None

if __name__ == '__main__':
    app.run(debug=True)