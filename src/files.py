from pathlib import Path
import pandas as pd
import re
import PTN
import sys
import shutil
import os
from src.ui import print_log
from src.mail import send_email
from src.api import api_call, gemini_api_call
from data.tags import TAGS
from config import PATH

def search_media_files():
    directory_path = PATH
    target_dir = Path(directory_path) / ".download"
    video_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.m4v'}
    
    # check if the directory actually exists
    if not target_dir.exists() or not target_dir.is_dir():
        print_log(f"Error: The directory '{directory_path}' does not exist.")
        return None

    media_data_table = []

    # recursively searches all folders
    for file_path in target_dir.rglob('*'):
        
        # filter video file type
        if file_path.suffix in video_extensions :
            name_without_ext = file_path.stem.strip()

            # filters video that already match the format Movie title (Year) or TV Show title SXXEXX
            if not re.fullmatch(r"^.+ \(\d{4}\)$", name_without_ext) and not re.fullmatch(r"^.+ S\d{2}E\d{2}$", name_without_ext) :
                filename_parsed = PTN.parse(file_path.name)

                media = "tv" if (filename_parsed.get('season') or filename_parsed.get('episode')) else "movie"
                if media == "movie" :
                    parse = [filename_parsed.get('title'), filename_parsed.get('year')]
                else : 
                    parse = [filename_parsed.get('title'), filename_parsed.get('year'), filename_parsed.get('season'), filename_parsed.get('episode')]
                
                media_data_table.append({
                    'File': file_path.name,
                    'Folder': file_path.parent.name,
                    'Path': str(file_path),
                    'Clean': clean_filename(file_path.name),
                    'Parse': parse,
                    'Media': media
                })

    # convert to pandas dataframe
    if (len(media_data_table) == 0) :
        print_log("❌ No media files found in that folder")
        sys.exit(1)

    df = pd.DataFrame(media_data_table)
    return df

def clean_filename(file_name):
    raw_name = file_name.rsplit('.', 1)[0]
    raw_name = raw_name.replace('_', '.')
    
    # search for a year patern 
    year_match = re.search(r'\(?((?:19|20)\d{2})\)?', raw_name)
    year = year_match.group(1) if year_match else None
    
    clean_title = re.sub(r'https?://\S+', '', raw_name, flags=re.IGNORECASE)
    clean_title = re.sub(r'www\.\S+', '', clean_title, flags=re.IGNORECASE)
    tlds = r'(com|fr|net|org|io|tv|me|site|info|biz|ws|ru|co|uk|be|ch|ca)'
    clean_title = re.sub(rf'\b(?:[a-zA-Z0-9-]+\.){{1,2}}{tlds}\b(?:/\S*)?', '', clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r'S\d+E\d+', '', clean_title, flags=re.IGNORECASE)
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
    
    print_log(f"\nAnalysing {len(media_data_table)} files. Please wait...\n")
    
    for index, file in media_data_table.iterrows():
        if file['Media'] == "movie": 
            name = str(file['Parse'][0]) if file['Parse'][0] else ""
            year = str(file['Parse'][1]) if file['Parse'][1] else ""
            query = "Parse : " + name + " " + year
            
            tmdb_title, tmdb_year, original_language = api_call(name, year, "en-US", "movie")
            success = True if tmdb_title else False
            if success:
                new_file_name = tmdb_title + ' (' + tmdb_year + ')'
            else: 
                name = str(file['Clean'][0]) if file['Clean'][0] else ""
                year = str(file['Clean'][1]) if file['Clean'][1] else ""
                query = "Clean : " + name + " " + year
                
                tmdb_title, tmdb_year, original_language = api_call(name, year, "en-US", "movie")
                success = True if tmdb_title else False
                if success:
                    new_file_name = tmdb_title + ' (' + tmdb_year + ')'

            if success : 
                if original_language == "fr" or original_language == "fr-FR":
                    tmdb_title_fr, tmdb_year_fr, _ = api_call(name, year, "fr-FR", "movie")
                    success = True if tmdb_title_fr else False
                    if success:
                        new_file_name = tmdb_title_fr + ' (' + tmdb_year_fr + ')'
            else :
                gemini_title,gemini_year,gemini_lang,gemini_new_tags = gemini_api_call(file)
                success = True if gemini_title else False
                if success: 
                    new_file_name = gemini_title + ' (' + gemini_year + ')'

            if success:
                corrected_name = new_file_name.replace(':', ' -')
            else:
                send_email(f"The following media file does not provide enough informations to be renamed successfully: {file['File']}")

            corrected_data_table.append({
                'Original': file['File'],
                'Query': query,
                'Corrected': corrected_name if success else "Not found",
                'Path': file['Path'],
                'Media': file['Media']
            })

        elif file['Media'] == "tv": 
            name    = str(file['Parse'][0]) if file['Parse'][0] else ""
            year    = str(file['Parse'][1]) if file['Parse'][1] else ""
            season  = str(file['Parse'][2]) if file['Parse'][2] else ""
            episode = str(file['Parse'][3]) if file['Parse'][3] else ""
            query = "Parse : " + name + " " + year

            if not float(season)/10.0 >= 1.0 :
                season = "0" + str(season)
            else : 
                season = str(season)

            if not float(episode)/10.0 >= 1.0 :
                episode = "0" + str(episode)
            else :
                episode = str(episode)
            
            tmdb_title, tmdb_year, original_language = api_call(name, year, "en-US", "tv")
            success = True if tmdb_title else False
            if success:
                new_file_name = tmdb_title + ' S' + season + 'E' + episode
            else: 
                name = str(file['Clean'][0]) if file['Clean'][0] else ""
                year = str(file['Clean'][1]) if file['Clean'][1] else ""
                query = "Clean : " + name + " " + year
                
                tmdb_title, tmdb_year, original_language = api_call(name, year, "en-US", "tv")
                success = True if tmdb_title else False
                if success:
                    new_file_name = tmdb_title + ' S' + season + 'E' + episode
                
            if success : 
                if original_language == "fr" or original_language == "fr-FR":
                    tmdb_title_fr, tmdb_year_fr, _ = api_call(name, year, "fr-FR", "tv")
                    success = True if tmdb_title_fr else False
                    if success:
                        new_file_name = tmdb_title_fr + ' S' + season + 'E' + episode
            else :
                gemini_title,gemini_year,gemini_lang,gemini_new_tags = gemini_api_call(file)
                success = True if gemini_title else False
                if success:
                    new_file_name = gemini_title + ' S' + season + 'E' + episode

            if success:
                corrected_name = new_file_name.replace(':', ' -')
            else:
                send_email(f"The following media file does not provide enough informations to be renamed successfully: {file['File']}")
                    
            corrected_data_table.append({
                'Original': file['File'],
                'Query': query,
                'Corrected': corrected_name if success else "Not found",
                'Path': file['Path'],
                'Media': file['Media'],
                'Season': season,
                'Episode': episode
            })
        else :
            print_log("Ignored : " + file['File'] + "\n")
        
    df = pd.DataFrame(corrected_data_table)
    return df

def rename_media_files(corrected_data_table):
    renamed_count = 0

    for index, row in corrected_data_table.iterrows():
        if row['Corrected'] == "Not found":
            print_log(f"⏭ Ignored (not found) : {row['Original']}")
            continue
            
        original_path = Path(str(row['Path'])).resolve()
        magic_prefix = "\\\\?\\"
        safe_old_path = f"{magic_prefix}{original_path}"
        
        if not os.path.exists(safe_old_path):
            print_log(f"Error (file does not exist) : {original_path.name[:30]}...")
            continue
            
        extension = original_path.suffix
        new_filename = f"{row['Corrected']}{extension}"
        
        new_path = original_path.with_name(new_filename).resolve()
        safe_new_path = f"{magic_prefix}{new_path}"
        
        try:
            if safe_old_path == safe_new_path:
                continue
                
            corrected_data_table.loc[index, 'Path'] = str(new_path)
            os.rename(safe_old_path, safe_new_path)
            
            renamed_count += 1
            
        except Exception as e:
            print_log(f"❌ Error (impossible to rename) {original_path.name[:30]}... : {e}")

    if renamed_count == 0:
        print_log(f"\n❌ No files have been renamed.")
    else:
        print_log(f"\n🎉 Done ! {renamed_count}/{len(corrected_data_table)} file(s) have been successfully renamed.\n\n")
    
    return corrected_data_table

def sort_media_files(corrected_data_table):
    paths = []

    for index, movie in corrected_data_table.iterrows():
        old_path = Path(str(movie['Path']))
        extension = old_path.suffix
        media = movie['Media']
        
        corrected_name = f"{movie['Corrected']}{extension}"
        
        if media == "movie":
            folder_path = Path(PATH) / "Films"
            folder_path.mkdir(parents=True, exist_ok=True)
            new_path = folder_path / corrected_name
            
        elif media == "tv":
            match = re.search(r'S(\d+)E\d+', str(movie['Corrected']), flags=re.IGNORECASE)

            if match:
                season_number = match.group(1) 
                season_folder = f"Saison {season_number.zfill(2)}" 
            else:
                season_folder = "Unknown" 

            tv_show_name = re.sub(r'S\d+E\d+', '', str(movie['Corrected']), flags=re.IGNORECASE).strip()

            folder_path = Path(PATH) / "Séries" / tv_show_name / season_folder
            folder_path.mkdir(parents=True, exist_ok=True)
            new_path = folder_path / corrected_name
            
        else:
            print_log(f"⏭ Ignored (not found) : {corrected_name}")
            continue
        
        paths.append([old_path, new_path])

    if not paths:
        print_log("No media to move to a new folder.")
        sys.exit(1)

    return paths

def move_file(old_path, new_path):
    old_abs = old_path.resolve()
    new_abs = new_path.resolve()
    
    magic_prefix = "\\\\?\\"
    safe_old = f"{magic_prefix}{old_abs}"
    safe_new = f"{magic_prefix}{new_abs}"

    try:
        shutil.move(safe_old, safe_new) 
    except Exception as e:
        print_log(f"❌ Error : impossible to move file \n\n # Error response : {e} \n\n # Old path {safe_old} \n\n # New path {safe_new}")
        sys.exit(1)

def remove_empty_folders(target_path):
    if not os.path.exists(target_path):
        print_log(f"The path '{target_path}' does not exist.")
        return

    for dirpath, dirnames, filenames in os.walk(target_path, topdown=False):
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
            except OSError as e:
                print_log(f"Error deleting {dirpath}: {e}")
                sys.exit(1)

def move_media_files (paths):
    success_count = 0
    for old, new in paths:
        try:
            move_file(old, new)
            success_count += 1
        except Exception as e:
            print_log(f"❌ Error : impossible to move file \n\n # Error response : {e} \n\n # Old path {old} \n\n # New path {new}")
            sys.exit(1)
            
    print_log(f"\n✅ {success_count} files have been successfully sorted and moved!")

    remove_empty_folders(Path(PATH) / ".download")