#!/bin/bash

#wget --mirror --convert-links --adjust-extension --page-requisites --no-parent https://bangalore.armyr.se/

python3 ./convert_to_hugo.py

python3 ./donwload_media_files_and_update_links.py