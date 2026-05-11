import sys
import os
import re
import PTN
import pandas as pd
from pathlib import Path
from src import ui, api, mail
from data.data import TAGS, TLDS, QUALITY_PATTERNS, RESOLUTION_PATTERNS

import config
MOVIES_FOLDER = getattr(config, 'MOVIES_FOLDER', None)
TV_SHOWS_FOLDER = getattr(config, 'TV_SHOWS_FOLDER', None)
NOT_SORTED_MEDIA_FILES_FOLDER = getattr(config, 'NOT_SORTED_MEDIA_FILES_FOLDER', None)
RESOLUTION = getattr(config, 'RESOLUTION', False)
QUALITY = getattr(config, 'QUALITY', False)

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
        raise RuntimeError(ui.print_error(f" ❌ Error: The file {DATA_FILE} does not exist",e))

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

def parse_season_episode(season, episode, filename):
    try:
        s = int(season)
        e = int(episode)
    except (ValueError, TypeError):
        season_regex = r'(?:saison|season|s)[.\s-]*(\d+)'
        episode_regex = r'(?:episode|ep|e)[.\s-]*(\d+)'

        s_match = re.search(season_regex, filename, re.IGNORECASE)
        e_match = re.search(episode_regex, filename, re.IGNORECASE)

        if s_match and e_match:
            s = int(s_match.group(1))
            e = int(e_match.group(1))
        else:
            raise ValueError(f"Could not extract season/episode from filename: {filename}")

    return s, e

def parse_resolution_quality(resolution_ptn,quality_ptn,resolution_clean,quality_clean):
    # resolution
    if resolution_ptn and str(resolution_ptn).strip():
        final_resolution = resolution_ptn
    elif resolution_clean and str(resolution_clean).strip():
        final_resolution = resolution_clean
    else:
        final_resolution = None

    # quality
    if quality_ptn and str(quality_ptn).strip():
        final_quality = quality_ptn
    elif quality_clean and str(quality_clean).strip():
        final_quality = quality_clean
    else:
        final_quality = None

    return final_resolution, final_quality

def format_season_and_episode(season, episode):
    try:
        season = int(season)
        episode = int(episode)
    except (ValueError, TypeError):
        raise ValueError("Failed parsing season or episode")

    if season < 10:
        season = "0" + str(season)
    else: 
        season = str(season)

    if episode < 10:
        episode = "0" + str(episode)
    else:
        episode = str(episode)

    return season, episode

def sort_media_dataframe(df):
    if df.empty:
        return df
    return df.sort_values(
        by=['Corrected', 'Season', 'Episode'], 
        ascending=[True, True, True], 
        ignore_index=True
    )

def correct_movie_filename(file):
    
    new_filename = None

    try:
        name = file['Parse'][0]
        year = file['Parse'][1]

        resolution,quality = parse_resolution_quality(file['Parse'][2],file['Parse'][3],file['Clean'][2],file['Clean'][3])
        
        success, title, year, original_language = api.api_call(name, year, "en-US", "movie")
        
        if not success: 
            name = file['Clean'][0]
            year = file['Clean'][1]
            
            success, title, year, original_language = api.api_call(name, year, "en-US", "movie")
            
            if not success and ui.AI_FALLBACK_ENABLED:
                success, title, year, original_language, _ = api.gemini_api_call(file)
        
        if success and original_language in ["fr", "fr-FR"]:
            success_fr, title_fr, year_fr, _ = api.api_call(name, year, "fr-FR", "movie")
            if success_fr:
                title = title_fr 
                year = year_fr
        
        new_filename = generate_new_movie_filename(success,title,year,resolution,quality)
            
    except Exception as e:
        failed_file = file.get('File', 'Unknown File')

        error_message = (
                f"Impossible to rename the following file: {failed_file}\n\n"
                f"⤷ Error logs: {e}\n"
            )
        
        mail.send_email(error_message)

        if ui.VERBOSE_ENABLED:  
            ui.print_log(error_message)
        
        new_filename = None

    return new_filename

def correct_tv_show_filename(file):

    new_filename = None
    season = None
    episode = None

    try :
        name             = file['Parse'][0]
        year             = file['Parse'][1]

        season,episode = parse_season_episode(file['Parse'][2],file['Parse'][3],file['File'])
        season,episode = format_season_and_episode(season,episode)
        resolution,quality = parse_resolution_quality(file['Parse'][4],file['Parse'][5],file['Clean'][2],file['Clean'][3])
        
        success, title, _, original_language = api.api_call(name, year, "en-US", "tv")
        if not success:
            name             = file['Clean'][0]
            year             = file['Clean'][1]
            
            success, title, _, original_language = api.api_call(name, year, "en-US", "tv")
            if not success and ui.AI_FALLBACK_ENABLED:
                success, title, _, _, _ = api.gemini_api_call(file)
            
        if success and original_language in ["fr", "fr-FR"]:
            success_fr, title_fr, _, _ = api.api_call(name, year, "fr-FR", "tv")
            if success_fr:
                title = title_fr

        new_filename = generate_new_tvshow_filename(success,title,year,season,episode,resolution,quality)
    
    except Exception as e:
        failed_file = file.get('File', 'Unknown File')

        error_message = (
                f"Impossible to rename the following file: {failed_file}\n\n"
                f"⤷ Error logs: {e}\n"
            )
        
        mail.send_email(error_message)

        if ui.VERBOSE_ENABLED:  
            ui.print_log(error_message)
        
        new_filename = None
        season = None
        episode = None

    return new_filename, season, episode

def generate_new_movie_filename(success, title, year, resolution, quality):
    is_title_valid = title and str(title).strip()

    if not success or not is_title_valid :
        raise LookupError("API calls failed or essential metadata (Title) is missing/empty.")

    new_name = title.replace(':', ' -')
    if year and str(year).strip():
        new_name += f" ({year})"

    # quality and resolution
    metadata_parts = []
    if QUALITY and quality and str(quality).strip():
        metadata_parts.append(str(quality))
    if RESOLUTION and resolution and str(resolution).strip():
        metadata_parts.append(str(resolution))
    if metadata_parts:
        new_name += f" [{' '.join(metadata_parts)}]"

    return new_name

def generate_new_tvshow_filename(success, title, year, season, episode, resolution, quality):
    is_title_valid = title and str(title).strip()
    is_season_valid = season and str(season).strip()
    is_episode_valid = episode and str(episode).strip()

    if not success or not is_title_valid or not is_season_valid or not is_episode_valid:
        raise LookupError("API calls failed or essential metadata (Title, Season, or Episode) is missing/empty.")

    new_name = title.replace(':', ' -')
    if year and str(year).strip():
        new_name += f" ({year})"

    # season and episode
    s_padded = str(season).zfill(2)
    e_padded = str(episode).zfill(2)
    new_name += f" - S{s_padded}E{e_padded}"

    # quality and resolution
    metadata_parts = []
    if QUALITY and quality and str(quality).strip():
        metadata_parts.append(str(quality))
    if RESOLUTION and resolution and str(resolution).strip():
        metadata_parts.append(str(resolution))
    if metadata_parts:
        new_name += f" [{' '.join(metadata_parts)}]"

    return new_name

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
    resolution = str(filename_parsed.get('resolution')) if filename_parsed.get('resolution') else ""
    quality = str(filename_parsed.get('quality')) if filename_parsed.get('quality') else ""
    if media == "movie" :
        parse = [title, year, resolution, quality]
    else : 
        season = str(filename_parsed.get('season')) if filename_parsed.get('season') else ""
        episode = str(filename_parsed.get('episode')) if filename_parsed.get('episode') else ""
        parse = [title, year, season, episode, resolution, quality]

    return parse, media

def clean_filename(filename):
    raw_name = filename.rsplit('.', 1)[0]
    raw_name = raw_name.replace('_', '.')

    # remove urls
    filename_without_urls = remove_url(raw_name)
    
    # search for a year patern 
    year_match = re.search(r'\(?((?:19|20)\d{2})\)?', raw_name)
    year = year_match.group(1) if year_match else ""

    resolution = ""
    for pattern in RESOLUTION_PATTERNS:
        res_match = re.search(pattern, raw_name, flags=re.IGNORECASE)
        if res_match:
            resolution = res_match.group(0)
            break

    quality = ""
    for pattern in QUALITY_PATTERNS:
        qual_match = re.search(pattern, raw_name, flags=re.IGNORECASE)
        if qual_match:
            quality = qual_match.group(0)
            break

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
    
    return clean_title, year, resolution, quality

import pandas as pd

def handle_conflicts_and_duplicates(df, failed_files):
    if df.empty:
        return df

    # Identify all rows where the 'Corrected' name is a duplicate
    check_for_duplicates = df[df.duplicated(subset=['Corrected'], keep=False)]
    
    if not check_for_duplicates.empty:
        conflicts = check_for_duplicates['Corrected'].unique()
        for i in conflicts:
            # Find all original filenames associated with this specific conflict
            fichiers_originaux = check_for_duplicates[check_for_duplicates['Corrected'] == i]['Original'].tolist()
            
            for original_file in fichiers_originaux:
                failed_files.append({
                    'Original': original_file,
                    'Reason': f"Conflict: Multiple files resolve to '{i}'"
                })
        
        # Remove ALL conflicting rows from the dataframe
        df = df.drop_duplicates(subset=['Corrected'], keep=False)
    
    return df

def get_corrected_media_filenames(messy_data_table, clean_data_table):
    ui.print_log(f"\nAnalysing {len(messy_data_table)} files. Please wait...\n")
    
    new_clean_data_rows = []
    failed_files = []
    
    for _, file in messy_data_table.iterrows():

        if file['Media'] == "movie": 
            corrected_name = correct_movie_filename(file) 
            season, episode = None, None
        elif file['Media'] == "tv": 
            corrected_name, season, episode = correct_tv_show_filename(file) 
        else:
            ui.print_log(f"Ignored : {file['File']}\n")
            continue
            
        if corrected_name is None:
            failed_files.append({
                'Original': file['File'], 
                'Reason': 'API or parsing failed'
            })
        else:
            new_clean_data_rows.append({
                'Original': file['File'],
                'Corrected': corrected_name,
                'Path': file['Path'],
                'Media': file['Media'],
                'Season': season,
                'Episode': episode   
            })
            
    new_df = pd.DataFrame(new_clean_data_rows)
    df = pd.concat([clean_data_table, new_df], ignore_index=True) if not new_df.empty else clean_data_table

    df = sort_media_dataframe(df)
    df = handle_conflicts_and_duplicates(df, failed_files)

    ui.display_skipped_filenames(failed_files)
            
    return df

def has_files_to_rename(data_table):
    data_empty = data_table.empty
    if not data_empty:
        data_empty = True
        for _, row in data_table.iterrows(): 
            if row['Original'] != row['Corrected']:
                data_empty = False
    return not data_empty