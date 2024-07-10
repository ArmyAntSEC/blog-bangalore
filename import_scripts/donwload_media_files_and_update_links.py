import os
import re
import requests
from urllib.parse import urlparse, urlunparse, unquote

BASE_URL = "https://hex.armyr.se/wp-content/uploads"

def simplify_filename(filename):
    # Remove query parameters and fragments
    filename = filename.split('?')[0].split('#')[0]
    # Remove .html ending if present
    if filename.endswith('.html'):
        filename = filename[:-5]
    # Simplify the filename by removing any trailing -1 or -edited sequences, preserving the extension
    base, extension = os.path.splitext(filename)
    simplified_base = re.sub(r'(-1|-edited)+$', '', base)
    simplified_filename = simplified_base + extension
    return simplified_filename

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Downloaded {url} to {save_path}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def process_index_md(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Regex to find all image references
        image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)
        
        updated_content = content
        for image_url in image_urls:
            # Remove URL encoding and query parameters
            image_url = unquote(image_url)
            parsed_url = urlparse(image_url)
            clean_path = urlunparse(parsed_url._replace(query=""))
            clean_filename = os.path.basename(clean_path)
            simplified_filename = simplify_filename(clean_filename)

            if parsed_url.scheme and parsed_url.netloc:
                # Absolute URL
                full_url = clean_path
            else:
                # Relative URL, construct the correct URL
                parts = clean_path.split('/')
                if len(parts) > 3 and parts[-3].isdigit() and parts[-2].isdigit():
                    year, month, filename = parts[-3], parts[-2], clean_filename
                    full_url = f"{BASE_URL}/{year}/{month}/{filename}"
                else:
                    print(f"Invalid relative path: {image_url}")
                    continue

            # Construct the path to save the image
            save_path = os.path.join(os.path.dirname(file_path), clean_filename)
            
            # Try to download the original image
            if not download_image(full_url, save_path):
                # If download fails, try the simplified filename
                if parsed_url.scheme and parsed_url.netloc:
                    full_url = parsed_url._replace(path=f"{parsed_url.path.rsplit('/', 1)[0]}/{simplified_filename}")
                    full_url = full_url.geturl()
                else:
                    full_url = f"{BASE_URL}/{year}/{month}/{simplified_filename}"
                save_path = os.path.join(os.path.dirname(file_path), simplified_filename)
                
                if not download_image(full_url, save_path):
                    raise Exception(f"Failed to download image {full_url}")

            # Update the content to reference the downloaded image file without any paths
            updated_content = updated_content.replace(image_url, os.path.basename(save_path))

        # Save the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            print(f"Updated {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        raise e

def process_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "index.md":
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                try:
                    process_index_md(file_path)
                except Exception as e:
                    print(f"Stopping processing due to error: {e}")
                    return

if __name__ == '__main__':
    # Use the current working directory
    directory = os.getcwd()

    # Process index.md files to download images and update links
    process_files(directory)
