import sys
import os
import re
import PTN
import pandas as pd
from pathlib import Path
from src import ui, api, mail
from data.tags import TAGS, TLDS
from config import PATH, MOVIES_FOLDER_NAME, TV_SHOWS_FOLDER_NAME, NOT_SORTED_MEDIA_FILES_FOLDER_NAME

def verify_arguments(): 
    args = sys.argv[1:]
    if len(args) > 2:
        ui.print_log("Wrong arguments : maximum 2 arguments expected (e.g., 'auto'/'manual' and/or 'log').")
        sys.exit(1)

    for arg in args:
        if arg not in ["auto", "manual", "log"]:
            ui.print_log("Wrong arguments : expected values are 'auto', 'manual', 'log' or nothing.")
            sys.exit(1)
            
    if "auto" in args and "manual" in args:
        ui.print_log("Wrong arguments : cannot use 'auto' and 'manual' at the same time.")
        sys.exit(1)

    return 0

def verify_path():
    path = PATH
    if not os.path.exists(path):
        ui.print_log(f"❌ The base path '{path}' does not exist. Stopping program.")
        sys.exit(1) 

    required_folders = [MOVIES_FOLDER_NAME, TV_SHOWS_FOLDER_NAME, NOT_SORTED_MEDIA_FILES_FOLDER_NAME]
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
        ui.print_log(f"❌ Missing folders: {', '.join(missing_folders)}. Stopping program.")
        sys.exit(1)

    if unexpected_items:
        ui.print_log(f"❌ Unexpected items found in '{path}': {', '.join(unexpected_items)}.")
        ui.print_log(f"⚠️ The program expects ONLY the following folders to be present: {', '.join(required_folders)}. Stopping program.")
        sys.exit(1)

    return 0

DATA_FILE = Path("../data/tags.py")

def add_new_tags(missing_tags):
    if not missing_tags:
        return

    # read file
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f" ❌ Error: The file {DATA_FILE} does not exist \n\n ⤷ Error logs: {e} \n")

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

    # find tags list
    pattern = re.compile(r"(TAGS\s*=\s*\[)([^\]]*)\]")
    match = pattern.search(content)

    if match:
        group1 = match.group(1)
        
        if not group1.strip().endswith(','):
            group1 += ','
            
        injection = f"\n    # === Ajout Auto Gemini ===\n    {new_tags_formatted}"
        new_content = content[:match.end(1)] + injection + content[match.start(2):]
        
        # add tags to the list
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        ui.print_log(f" ✅ New tag(s) added to {DATA_FILE.name} : {tags_to_add}")
    else:
        ui.print_log(f" ❌ Error : Impossible to find TAGS list {DATA_FILE.name}")

def format_season_and_episode(season, episode):
    if float(season)/10.0 < 1.0 :
        season = "0" + str(season)
    else : 
        season = str(season)

    if float(episode)/10.0 < 1.0 :
        episode = "0" + str(episode)
    else :
        episode = str(episode)

    return season,episode

def correct_movie_filename(file):
    name = file['Parse'][0]
    year = file['Parse'][1]
    
    success, title, year, original_language = api.api_call(name, year, "en-US", "movie")
    if not success: 
        name = file['Clean'][0]
        year = file['Clean'][1]
        
        success, title, year, original_language = api.api_call(name, year, "en-US", "movie")
        if not success:
            success, title,year,original_language,_ = api.gemini_api_call(file)
    
    if success and original_language == "fr" or original_language == "fr-FR":
        success_fr,title_fr, year_fr, _ = api.api_call(name, year, "fr-FR", "movie")
        if success_fr:
            title = title_fr 
            year = year_fr

    if success:
        new_file_name = title + ' (' + year + ')'
        corrected_name = new_file_name.replace(':', ' -')
    else:
        corrected_name = None
        mail.send_email(f"The following media file does not provide enough informations to be renamed successfully: {file['File']}")

    return corrected_name

def correct_tv_show_filename(file):
    name    = file['Parse'][0]
    year    = file['Parse'][1]
    season  = file['Parse'][2]
    episode = file['Parse'][3]

    season,episode = format_season_and_episode(season,episode)
    
    success, title, _, original_language = api.api_call(name, year, "en-US", "tv")
    if not success:
        name = file['Clean'][0]
        year = file['Clean'][1]
        
        success, title, _, original_language = api.api_call(name, year, "en-US", "tv")
        if not success:
            success, title, _, _, _ = api.gemini_api_call(file)
        
    if success and original_language == "fr" or original_language == "fr-FR":
        success_fr, title_fr, _, _ = api.api_call(name, year, "fr-FR", "tv")
        if success_fr:
            title = title_fr

    if success:
        new_file_name = title + ' S' + season + 'E' + episode
        corrected_name = new_file_name.replace(':', ' -')
    else:
        corrected_name = None
        mail.send_email(f"The following media file does not provide enough informations to be renamed successfully: {file['File']}")

    return corrected_name, season, episode

def remove_url(filename):
    # setup
    tlds_pattern = '|'.join(TLDS)
    url_pattern = rf"""
        (?:
            # CASE 1: Starts with 'www.' (Safe to greedily capture multiple subdomains)
            \bwww\.(?:[a-zA-Z0-9-]+\.)+(?:{tlds_pattern})\b
            
            | # OR
            
            # CASE 2: No 'www.' (Strictly ONE word before the TLD chain)
            # This captures "site.com" or "amazon.co.uk" but stops before "My.Movie."
            \b[a-zA-Z0-9-]+\.(?:(?:{tlds_pattern})\.)*(?:{tlds_pattern})\b
        )
    """
    # clean
    clean_filename = re.sub(url_pattern, '', filename, flags=re.IGNORECASE | re.VERBOSE)
    clean_filename = re.sub(r'\.{2,}', '.', clean_filename)
    clean_filename = clean_filename.strip('.-_ ')

    return clean_filename

def parse_filename(filename):
    filename_without_url = remove_url(filename)
    filename_parsed = PTN.parse(filename_without_url)
    media = "tv" if (filename_parsed.get('season') or filename_parsed.get('episode')) else "movie"
    title = str(filename_parsed.get('title')) if filename_parsed.get('title') else ""
    year = str(filename_parsed.get('year')) if filename_parsed.get('year') else ""
    if media == "movie" :
        parse = [title, year]
    else : 
        season = str(filename_parsed.get('season')) if filename_parsed.get('season') else ""
        episode = str(filename_parsed.get('episode')) if filename_parsed.get('episode') else ""
        parse = [title, year, season, episode]
    
    return parse, media

def clean_filename(filename):
    raw_name = filename.rsplit('.', 1)[0]
    raw_name = raw_name.replace('_', '.')

    # remove urls
    filename_without_urls = remove_url(raw_name)
    
    # search for a year patern 
    year_match = re.search(r'\(?((?:19|20)\d{2})\)?', raw_name)
    year = year_match.group(1) if year_match else ""

    # regex filters
    clean_title = re.sub(r'S\d+E\d+', '', filename_without_urls, flags=re.IGNORECASE)
    clean_title = re.sub(r'\d{5,}', '', clean_title)
    clean_title = re.sub(r'\(?(?:19|20)\d{2}\)?', '', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    
    # remove torrent file informations
    for tag in TAGS:
        clean_title = re.sub(rf'(?i)\b{tag}\b', '', clean_title)
        
    # clean spaces
    clean_title = clean_title.replace('.', ' ').replace('_', ' ').replace('-', ' ')
    clean_title = ' '.join(clean_title.split()).strip()
    
    return clean_title, year

def get_corrected_media_filenames(media_data_table):
    corrected_data_table = []
    
    ui.print_log(f"\nAnalysing {len(media_data_table)} files. Please wait...\n")
    
    for index, file in media_data_table.iterrows():
        if file['Media'] == "movie": 
            corrected_name = correct_movie_filename(file)
            corrected_data_table.append({
                'Original': file['File'],
                'Corrected': corrected_name,
                'Path': file['Path'],
                'Media': file['Media']
            })

        elif file['Media'] == "tv": 
            corrected_name, season, episode = correct_tv_show_filename(file)
            corrected_data_table.append({
                'Original': file['File'],
                'Corrected': corrected_name,
                'Path': file['Path'],
                'Media': file['Media'],
                'Season': season,
                'Episode': episode
            })
        else :
            ui.print_log("Ignored : " + file['File'] + "\n")
        
    df = pd.DataFrame(corrected_data_table)
    return df