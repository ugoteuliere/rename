from pathlib import Path
import pandas as pd
import re
import sys
import shutil
import os
from src import ui, utils
from config import MOVIES_FOLDER, TV_SHOWS_FOLDER, NOT_SORTED_MEDIA_FILES_FOLDER

def search_media_files(path):
    target_dir = Path(path).resolve() if path is not None else Path(NOT_SORTED_MEDIA_FILES_FOLDER)
    
    # check if the directory actually exists
    if not target_dir.exists() or not target_dir.is_dir():
        ui.print_log(f"Error: The directory '{target_dir}' does not exist.")
        return None

    video_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.m4v'}
    
    messy_data_table = []
    clean_data_table = []

    # recursively searches all folders
    for file_path in target_dir.rglob('*'):
        
        # filter video file type
        if file_path.suffix in video_extensions :
            # filters video that already match the format Movie title (Year) or TV Show title SXXEXX
            name_without_ext = file_path.stem.strip()
            if not re.fullmatch(r"^.+ \(\d{4}\)$", name_without_ext) and not re.fullmatch(r"^.+ S\d{2}E\d{2}$", name_without_ext) :
                
                parse, media = utils.parse_filename(file_path.name)
                
                messy_data_table.append({
                    'File': file_path.name,
                    'Folder': file_path.parent.name,
                    'Path': str(file_path),
                    'Clean': utils.clean_filename(file_path.name),
                    'Parse': parse,
                    'Media': media
                })
            else:
                parse, media = utils.parse_filename(file_path.name)

                if media == "movie": 
                    clean_data_table.append({
                        'Original': file_path.stem,
                        'Corrected': file_path.stem,
                        'Path': str(file_path),
                        'Media': media,
                        'Season': None,
                        'Episode': None   
                    })

                elif media == "tv": 
                    clean_data_table.append({
                        'Original': file_path.stem,
                        'Corrected': file_path.stem,
                        'Path': str(file_path),
                        'Media': media,
                        'Season': parse[2],
                        'Episode': parse[3]
                    })

    if len(messy_data_table) == 0 and len(clean_data_table) == 0:
        ui.print_log("❌ No media files found in that folder")
        sys.exit(1)
    else:
        ui.print_log(f"\n📂 Folder scan report:\n - {len(messy_data_table)} files to rename\n - {len(clean_data_table)} files with clean filename\n")

    messy_data = pd.DataFrame(messy_data_table)
    clean_data = pd.DataFrame(
        clean_data_table, 
        columns=['Original', 'Corrected', 'Path', 'Media', 'Season', 'Episode']
    )
    
    sorted_clean_data = clean_data.sort_values(
        by=['Corrected', 'Season', 'Episode'], 
        ascending=[True, True, True], 
        ignore_index=True
    )

    return messy_data, sorted_clean_data

def make_safe_path(path: Path) -> str:
    if os.name != 'nt':
        return str(path)

    path_str = str(path)

    if path_str.startswith("\\\\"):
        return "\\\\?\\UNC\\" + path_str.lstrip("\\")
    else:
        return "\\\\?\\" + path_str

def rename_media_files(clean_data_table):
    renamed_count = 0
    already_clean_files_count = 0

    for index, row in clean_data_table.iterrows():
        if row['Corrected'] == None:
            ui.print_log(f"⏭ Ignored (not found) : {row['Original']}")
            continue
            
        original_path = Path(str(row['Path'])).resolve()
        safe_old_path = make_safe_path(original_path)
        
        if not os.path.exists(safe_old_path):
            ui.print_log(f"Error (file does not exist) : {original_path.name[:30]}...")
            continue
            
        extension = original_path.suffix
        new_filename = f"{row['Corrected']}{extension}"
        
        new_path = original_path.with_name(new_filename).resolve()
        safe_new_path = make_safe_path(new_path)

        try:
            if safe_old_path == safe_new_path:
                already_clean_files_count += 1
                continue
                
            clean_data_table.loc[index, 'Path'] = str(new_path)
            os.rename(safe_old_path, safe_new_path)
            
            renamed_count += 1
            
        except Exception as e:
            raise RuntimeError(ui.print_error(f" ❌ Error: Impossible to rename {original_path.name[:30]}...",e))

    if renamed_count == 0:
        ui.print_log("\n ❌ No files have been renamed.")
    else:
        ui.print_log(f"\n🎉 Done ! {renamed_count}/{len(clean_data_table)-already_clean_files_count} file(s) have been successfully renamed.\n\n")
    
    return clean_data_table

def sort_media_files(clean_data_table):
    paths = []

    for index, movie in clean_data_table.iterrows():
        old_path = Path(str(movie['Path']))
        extension = old_path.suffix
        media = movie['Media']
        
        corrected_name = f"{movie['Corrected']}{extension}"
        
        if media == "movie":
            folder_path = Path(MOVIES_FOLDER)
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

            folder_path = Path(TV_SHOWS_FOLDER) / tv_show_name / season_folder
            folder_path.mkdir(parents=True, exist_ok=True)
            new_path = folder_path / corrected_name
            
        else:
            ui.print_log(f"⏭ Ignored (not found) : {corrected_name}")
            continue
        
        paths.append([old_path, new_path])

    if not paths:
        ui.print_log("No media to move to a new folder.")
        sys.exit(1)

    return paths

def move_file(old_path, new_path):
    old_abs = old_path.resolve()
    new_abs = new_path.resolve()

    safe_old = make_safe_path(old_abs)
    safe_new = make_safe_path(new_abs)

    try:
        shutil.move(safe_old, safe_new) 
    except Exception as e:
        raise RuntimeError(ui.print_error(f" ❌ Error: Impossible to move the file \n Old path {safe_old} \n New path {safe_new}",e))

def remove_empty_folders(target_path):
    if not os.path.exists(target_path):
        ui.print_log(f"The path '{target_path}' does not exist.")
        return

    for dirpath, dirnames, filenames in os.walk(target_path, topdown=False):
        if dirpath == target_path:
            continue
            
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
            except OSError as e:
                raise RuntimeError(ui.print_error(f" ❌ Error: An error occurred while deleting {dirpath}",e))

def move_media_files (paths):
    success_count = 0
    for old, new in paths:
        move_file(old, new)
        success_count += 1
            
    ui.print_log(f"\n✅ {success_count} files have been successfully sorted and moved!")

    remove_empty_folders(Path(NOT_SORTED_MEDIA_FILES_FOLDER))