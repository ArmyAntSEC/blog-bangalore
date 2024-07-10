import os
import glob
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from datetime import datetime

def is_date_valid(year, month, day):
    try:
        datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        return True
    except ValueError:
        return False

def extract_entry_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'lxml')
            entry_content = soup.find('div', class_='entry-content')
            if entry_content:
                return entry_content.prettify()
            else:
                print(f"No entry-content found in {file_path}")
                return None
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def convert_html_to_markdown(content):
    soup = BeautifulSoup(content, 'lxml')
    entry_content = soup.find('div', class_='entry-content')
    
    if entry_content:
        # Handle iframes separately before converting the rest to Markdown
        for iframe in entry_content.find_all('iframe'):
            src = iframe.get('src')
            if 'youtube' in src:
                video_id = src.split('/')[-1].split('?')[0]
                iframe.replace_with(f'{{{{< youtube {video_id} >}}}}')
            elif 'vimeo' in src:
                video_id = src.split('/')[-1].split('?')[0]
                iframe.replace_with(f'{{{{< vimeo {video_id} >}}}}')
        
        # Convert to markdown
        markdown_content = md(entry_content.prettify(), heading_style="ATX")
        return markdown_content
    else:
        print("No entry-content found.")
        return None

def add_hugo_header(content, title, date_str):
    try:
        # Create the Hugo header
        header = f"""+++
title = '{title}'
date = {date_str}
draft = false
+++\n\n"""

        # Add the header to the content
        new_content = header + content
        return new_content

    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def save_content(content, file_path):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Saved content to {file_path}")
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")

def process_html_files(directory):
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    for file_path in html_files:
        parts = file_path.split(os.sep)
        if len(parts) >= 5 and parts[-5].isdigit() and parts[-4].isdigit() and parts[-3].isdigit():
            year, month, day = parts[-5], parts[-4], parts[-3]
            if is_date_valid(year, month, day):
                print(f"Processing {file_path}...")
                extracted_content = extract_entry_content(file_path)
                if extracted_content:
                    markdown_content = convert_html_to_markdown(extracted_content)
                    if markdown_content:
                        title = parts[-2].replace('-', ' ').title()
                        date_str = f"{year}-{month}-{day}T00:00:00+00:00"
                        final_content = add_hugo_header(markdown_content, title, date_str)
                        if final_content:
                            safe_title = ''.join([c if c.isalnum() or c in ' -_' else '_' for c in title])
                            new_file_path = os.path.join(directory, f"blog/{year}-{month}-{day}--{safe_title}/index.md")
                            save_content(final_content, new_file_path)

if __name__ == '__main__':
    # Use the current working directory
    directory = os.getcwd()

    # Process HTML files to extract content, convert to Markdown, and save with Hugo headers
    process_html_files(directory)
