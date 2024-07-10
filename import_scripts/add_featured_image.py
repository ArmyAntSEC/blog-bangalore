import os
import re

def find_and_set_featured_image(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file == "index.md":
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Check if featured_image is already set
                in_front_matter = False
                featured_image_set = False
                for line in lines:
                    if line.strip() == "+++":
                        in_front_matter = not in_front_matter
                    if in_front_matter and "featured_image" in line:
                        featured_image_set = True
                        break

                if featured_image_set:
                    continue

                # Find the first image reference
                image_regex = re.compile(r'!\[.*\]\((.*)\)')
                featured_image = None
                for line in lines:
                    match = image_regex.search(line)
                    if match:
                        featured_image = match.group(1)
                        break

                if featured_image:
                    # Add featured_image to the front matter
                    new_lines = []
                    in_front_matter = False
                    for line in lines:
                        if line.strip() == "+++":
                            if in_front_matter:
                                new_lines.append(f'featured_image = "{featured_image}"\n')
                            in_front_matter = not in_front_matter
                        new_lines.append(line)

                    # Write the modified lines back to the file
                    with open(file_path, 'w') as f:
                        f.writelines(new_lines)
                    print(f"Set featured_image in {file_path}")

# Start in the current directory
find_and_set_featured_image(os.getcwd())
