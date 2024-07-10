import os

def replace_urls_in_file(file_path, old_url, new_url):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        new_content = content.replace(old_url, new_url)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

        print(f"Updated {file_path}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def process_files(directory, old_url, new_url):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                replace_urls_in_file(file_path, old_url, new_url)

if __name__ == '__main__':
    # Define the directory to start searching for .md files
    directory = './'  # Adjust this as necessary

    # Define the old and new URLs
    old_url = 'https://armyrhexhome.files.wordpress.com/'
    new_url = '../../../../wp-content/uploads/'

    process_files(directory, old_url, new_url)

