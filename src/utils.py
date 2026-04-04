import sys
import os
import re
from pathlib import Path
from src.ui import print_log
from config import PATH

def verify_arguments(): 
    args = sys.argv[1:]
    if len(args) > 2:
        print_log("Wrong arguments : maximum 2 arguments expected (e.g., 'auto'/'manual' and/or 'log').")
        sys.exit(1)

    for arg in args:
        if arg not in ["auto", "manual", "log"]:
            print_log("Wrong arguments : expected values are 'auto', 'manual', 'log' or nothing.")
            sys.exit(1)
            
    if "auto" in args and "manual" in args:
        print_log("Wrong arguments : cannot use 'auto' and 'manual' at the same time.")
        sys.exit(1)

    return 0

def verify_path():
    path = PATH
    if not os.path.exists(path):
        print_log(f"❌ The base path '{path}' does not exist. Stopping program.")
        sys.exit(1) 

    required_folders = ["Films", "Séries", ".download"]
    missing_folders = []
    unexpected_items = []
    expected_items = ["desktop.ini"]

    actual_contents = os.listdir(path)

    for folder in required_folders:
        folder_path = os.path.join(path, folder)
        if not os.path.isdir(folder_path):
            missing_folders.append(folder)

    for item in actual_contents:
        if item not in required_folders and item not in expected_items:
            unexpected_items.append(item)

    if missing_folders:
        print_log(f"❌ Missing folders: {', '.join(missing_folders)}. Stopping program.")
        sys.exit(1)

    if unexpected_items:
        print_log(f"❌ Unexpected items found in '{path}': {', '.join(unexpected_items)}.")
        print_log(f"⚠️ The program expects ONLY the following folders to be present: {', '.join(required_folders)}. Stopping program.")
        sys.exit(1)

    return 0

DATA_FILE = Path("../data/tags.py")

def add_new_tags(missing_tags):
    if not missing_tags:
        return

    # 1. Lecture du fichier
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print_log(f" ❌ Error : The fime {DATA_FILE} does not exist.")
        return

    tags_to_add = []
    for tag in missing_tags:
        clean_tag = tag.strip().lower()
        if not clean_tag:
            continue
            
        escaped_tag = re.escape(clean_tag)
        
        if f"r'{escaped_tag}'" not in content and f"r'{clean_tag}'" not in content:
            tags_to_add.append(escaped_tag)

    if not tags_to_add:
        return

    new_tags_formatted = ", ".join([f"r'{tag}'" for tag in tags_to_add])

    # 2. Recherche de la liste TAGS
    pattern = re.compile(r"(TAGS\s*=\s*\[.*?)(\n\s*\])", re.DOTALL)
    match = pattern.search(content)

    if match:
        group1 = match.group(1)
        
        if not group1.strip().endswith(','):
            group1 += ','
            
        injection = f"\n    # === Ajout Auto Gemini ===\n    {new_tags_formatted}"
        new_content = content[:match.end(1)] + injection + content[match.start(2):]
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print_log(f" ✅ New tag(s) added to {DATA_FILE.name} : {tags_to_add}")
    else:
        print_log(f" ❌ Erreur : Impossible de localiser la liste TAGS dans {DATA_FILE.name}")