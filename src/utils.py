import sys
import os
import re
import PTN
import pandas as pd
from pathlib import Path
from src import ui, api, mail
from src.ui import AI_FALLBACK_ENABLED, print_error
from data.data import TAGS, TLDS

import config
MOVIES_FOLDER = getattr(config, 'MOVIES_FOLDER', None)
TV_SHOWS_FOLDER = getattr(config, 'TV_SHOWS_FOLDER', None)
NOT_SORTED_MEDIA_FILES_FOLDER = getattr(config, 'NOT_SORTED_MEDIA_FILES_FOLDER', None)

DATA_FILE = Path("../data/data.py")

def verify_folders():
    required_folders = [MOVIES_FOLDER, TV_SHOWS_FOLDER, NOT_SORTED_MEDIA_FILES_FOLDER]
    missing_folders = []

    if MOVIES_FOLDER == None or TV_SHOWS_FOLDER == None or NOT_SORTED_MEDIA_FILES_FOLDER == None:
        ui.print_log("❌ Missing configuration: \nThe global variables MOVIES_FOLDER,TV_SHOWS_FOLDER and NOT_SORTED_MEDIA_FILES_FOLDER all need to be configured in a config.py file at the root of the script. Please refer to the following documentation: https://github.com/ugoteuliere/rename\n\n Stopping program.")
        sys.exit(1)

    for folder_path in required_folders:
        if not os.path.isdir(folder_path):
            missing_folders.append(folder_path)

    # If any folders are missing, log the error and exit
    if missing_folders:
        ui.print_log(f"❌ Missing required folders: {', '.join(missing_folders)}.\n\n Stopping program.")
        sys.exit(1)

    return 0

def add_new_tags(missing_tags):
    if not missing_tags:
        return

    # read file
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as e:
        raise RuntimeError(print_error(f" ❌ Error: The file {DATA_FILE} does not exist",e))

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
        if not success and AI_FALLBACK_ENABLED:
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
    global AI_FALLBACK_ENABLED
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
        if not success and AI_FALLBACK_ENABLED:
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
    filename_without_url = re.sub(r'\d{5,}', '', filename_without_url)
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

def get_corrected_media_filenames(messy_data_table, clean_data_table):
    
    ui.print_log(f"\nAnalysing {len(messy_data_table)} files. Please wait...\n")
    
    new_clean_data_rows = []
    for index, file in messy_data_table.iterrows():
        if file['Media'] == "movie": 
            corrected_name = correct_movie_filename(file) 
            new_clean_data_rows.append({
                'Original': file['File'],
                'Corrected': corrected_name,
                'Path': file['Path'],
                'Media': file['Media'],
                'Season': None,
                'Episode': None   
            })

        elif file['Media'] == "tv": 
            corrected_name, season, episode = correct_tv_show_filename(file) 
            new_clean_data_rows.append({
                'Original': file['File'],
                'Corrected': corrected_name,
                'Path': file['Path'],
                'Media': file['Media'],
                'Season': season,
                'Episode': episode
            })
        else:
            ui.print_log("Ignored : " + file['File'] + "\n")
        
    new_clean_data_rows_df = pd.DataFrame(new_clean_data_rows)
    if not new_clean_data_rows_df.empty:
        if clean_data_table.empty:
            df = new_clean_data_rows_df
        else:
            df = pd.concat([clean_data_table, new_clean_data_rows_df], ignore_index=True)
    else:
        df = clean_data_table

    df = df.sort_values(
        by=['Corrected', 'Season', 'Episode'], 
        ascending=[True, True, True], 
        ignore_index=True
    )

    # check for duplicates among the corrected files
    check_for_duplicates = df[df.duplicated(subset=['Corrected'], keep=False)]
    if not check_for_duplicates.empty:
        conflicts = check_for_duplicates['Corrected'].unique()
        
        ui.print_log("❌ Error: Filename conflict detected!")
        ui.print_log("Multiple files will end up with the exact same name, which would cause overwrites.")
        ui.print_log(f"⚠️ Conflicting names: {', '.join(conflicts)}")
        
        for i in conflicts:
            fichiers_originaux = conflicts[conflicts['Corrected'] == i]['Original'].tolist()
            ui.print_log(f"   - '{i}' is generated by: {', '.join(fichiers_originaux)}")
            
        sys.exit(1)

    return df