#!/usr/bin/env python3
"""Convert WordPress WXR export to Hugo content."""

import xml.etree.ElementTree as ET
import os
import re
import html
from datetime import datetime

WXR = '/home/node/.openclaw/media/inbound/1645dd5d-bc19-4d11-b8d1-5c8fd62dcbc4'
CONTENT_DIR = '/home/node/.openclaw/workspace/floof-farm/content'

ns = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
    'dc': 'http://purl.org/dc/elements/1.1/',
}

tree = ET.parse(WXR)
root = tree.getroot()
channel = root.find('channel')
items = channel.findall('item')

def clean_html(text):
    """Convert WordPress HTML/blocks to markdown-ish content."""
    if not text:
        return ''
    
    # Remove WordPress block comments
    text = re.sub(r'<!-- /?wp:.*?-->', '', text)
    
    # Convert common HTML to markdown
    # Headers
    for i in range(6, 0, -1):
        text = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', lambda m: '#' * i + ' ' + m.group(1), text, flags=re.DOTALL)
    
    # Bold/italic
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)
    
    # Links
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
    
    # Images - convert to markdown, keep figure/figcaption
    text = re.sub(r'<figure[^>]*>(.*?)</figure>', lambda m: m.group(1), text, flags=re.DOTALL)
    text = re.sub(r'<figcaption[^>]*>(.*?)</figcaption>', lambda m: '\n*' + m.group(1).strip() + '*\n', text, flags=re.DOTALL)
    text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?\s*>', r'![\2](\1)', text, flags=re.DOTALL)
    text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?\s*>', r'![](\1)', text, flags=re.DOTALL)
    
    # Lists
    text = re.sub(r'<ul[^>]*>', '', text)
    text = re.sub(r'</ul>', '', text)
    text = re.sub(r'<ol[^>]*>', '', text)
    text = re.sub(r'</ol>', '', text)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    
    # Paragraphs and line breaks
    text = re.sub(r'<p[^>]*>', '\n\n', text)
    text = re.sub(r'</p>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<div[^>]*>', '\n', text)
    text = re.sub(r'</div>', '\n', text)
    
    # Blockquotes
    text = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n> ' + m.group(1).strip().replace('\n', '\n> '), text, flags=re.DOTALL)
    
    # Tables - keep as HTML (Hugo renders them)
    # Remove other tags but keep content
    text = re.sub(r'<(?!/?table|/?thead|/?tbody|/?tr|/?td|/?th)[^>]+>', '', text)
    
    # Clean up entities
    text = html.unescape(text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text

def get_meta(item, key):
    for pm in item.findall('wp:postmeta', ns):
        k = pm.find('wp:meta_key', ns).text
        if k == key:
            return pm.find('wp:meta_value', ns).text
    return None

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

# Category mapping for sections
CAT_TO_SECTION = {
    'Does': 'does',
    'Bucks': 'bucks', 
    'For Sale': 'for-sale',
    'Sold': 'sold',
    'Wethers': 'wethers',
    'Blog': 'blog',
    'Research': 'blog',
    'Genetics': 'genetics',
    'Herd Book': 'herd-book',
}

# Process published posts
post_count = 0
page_count = 0

for item in items:
    pt = item.find('wp:post_type', ns).text
    status = item.find('wp:status', ns).text
    
    if status != 'publish':
        continue
    if pt not in ('post', 'page'):
        continue
    
    title = item.find('title').text or ''
    slug = item.find('wp:post_name', ns).text or slugify(title)
    content_raw = item.find('content:encoded', ns).text or ''
    excerpt = item.find('excerpt:encoded', ns).text or ''
    date_str = item.find('wp:post_date', ns).text or ''
    author = item.find('dc:creator', ns).text or ''
    
    cats = [c.text for c in item.findall('category') if c.get('domain') == 'category' and c.text]
    tags = [c.text for c in item.findall('category') if c.get('domain') == 'post_tag' and c.text]
    
    # Parse date
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        date_iso = date.strftime('%Y-%m-%dT%H:%M:%S-08:00')
    except:
        date_iso = '2024-01-01T00:00:00-08:00'
    
    # Convert content
    content_md = clean_html(content_raw)
    
    # Determine output path
    if pt == 'page':
        # Pages go to their slug
        page_map = {
            'floof-farm-pnw-dairy-goats': ('_index.md', ''),
            'bucks': ('bucks/_index.md', ''),
            'for-sale': ('for-sale/_index.md', ''),
            'contact': ('contact.md', ''),
            'sales-policy': ('sales-policy.md', ''),
            'adga-goat-shows': ('shows.md', ''),
            'goat-gestation-calculator': ('gestation-calculator.md', ''),
        }
        if slug in page_map:
            filepath, _ = page_map[slug]
        elif 'breeding-schedule' in slug:
            filepath = f'breeding-schedules/{slug}.md'
        else:
            filepath = f'{slug}.md'
        
        out_path = os.path.join(CONTENT_DIR, filepath)
        section = ''
        page_count += 1
    else:
        # Posts - determine section from category
        section = 'blog'  # default
        for cat in cats:
            if cat in CAT_TO_SECTION:
                section = CAT_TO_SECTION[cat]
                break
        
        # Goat profiles go to their section
        if section in ('does', 'bucks', 'sold', 'wethers', 'for-sale'):
            out_path = os.path.join(CONTENT_DIR, section, f'{slug}.md')
        else:
            out_path = os.path.join(CONTENT_DIR, section, f'{slug}.md')
        
        post_count += 1
    
    # Build front matter
    fm = f'---\ntitle: "{title.replace(chr(34), chr(92)+chr(34))}"\n'
    fm += f'date: {date_iso}\n'
    if pt == 'post':
        fm += f'draft: false\n'
    if slug:
        fm += f'slug: "{slug}"\n'
    if cats:
        fm += f'categories:\n'
        for c in cats:
            fm += f'  - "{c}"\n'
    if tags:
        fm += f'tags:\n'
        for t in tags:
            fm += f'  - "{t}"\n'
    if excerpt:
        clean_excerpt = clean_html(excerpt).replace('"', '\\"').replace('\n', ' ')
        fm += f'description: "{clean_excerpt}"\n'
    if author:
        fm += f'author: "{author}"\n'
    
    # Add layout hints for goat profiles
    if section in ('does', 'bucks', 'sold', 'wethers'):
        fm += f'type: "{section}"\n'
        # Try to extract featured image from content
        img_match = re.search(r'!\[.*?\]\((https?://[^)]+)\)', content_md)
        if img_match:
            fm += f'featured_image: "{img_match.group(1)}"\n'
    
    fm += '---\n\n'
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(fm + content_md)

print(f'Converted {post_count} posts and {page_count} pages')

# Create section _index.md files
sections = {
    'does': ('Does', 'Our ADGA registered dairy does - Nigerian Dwarf and Toggenburg'),
    'bucks': ('Bucks', 'Our ADGA registered dairy bucks'),
    'sold': ('Sold', 'Goats that have found new homes'),
    'wethers': ('Wethers', 'Pet wethers'),
    'blog': ('Blog', 'Updates from the farm and goat care information'),
    'for-sale': ('For Sale', 'Goats currently available for purchase'),
    'genetics': ('Genetics', 'Our work in improving herd quality through modern genetic techniques'),
    'breeding-schedules': ('Breeding Schedules', 'Our breeding plans by year'),
}

for sec, (title, desc) in sections.items():
    idx_path = os.path.join(CONTENT_DIR, sec, '_index.md')
    if not os.path.exists(idx_path):
        os.makedirs(os.path.dirname(idx_path), exist_ok=True)
        with open(idx_path, 'w') as f:
            f.write(f'---\ntitle: "{title}"\ndescription: "{desc}"\n---\n')

print('Created section index files')
