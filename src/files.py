from pathlib import Path
import pandas as pd
import re
import sys
import shutil
import os
import subprocess
import json
from src import ui, utils
from data.data import QUALITY_PATTERNS, RESOLUTION_PATTERNS

import config
MOVIES_FOLDER = getattr(config, 'MOVIES_FOLDER', None)
TV_SHOWS_FOLDER = getattr(config, 'TV_SHOWS_FOLDER', None)
NOT_SORTED_MEDIA_FILES_FOLDER = getattr(config, 'NOT_SORTED_MEDIA_FILES_FOLDER', None)

def search_media_files(path):
    target_dir = Path(path).resolve() if path is not None else Path(NOT_SORTED_MEDIA_FILES_FOLDER)
    
    # check if the directory actually exists
    if not target_dir.exists() or not target_dir.is_dir():
        ui.print_log(f"Error: The directory '{target_dir}' does not exist.")
        return None

    video_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.m4v'}
    movie_re = r"^.+? \(\d{4}\)(?: \[[^\]]+\])?$"
    series_re = r"^.+?(?: \(\d{4}\))? - S\d{2}E\d{2}(?: \[[^\]]+\])?$"
    
    messy_data_table = []
    clean_data_table = []

    # recursively searches all folders
    for file_path in target_dir.rglob('*'):
        
        # filter video file type
        if file_path.suffix in video_extensions :
            # filters video that already match the format Movie title (Year) or TV Show title SXXEXX
            name_without_ext = file_path.stem.strip()

            is_movie = re.fullmatch(movie_re, name_without_ext)
            is_series = re.fullmatch(series_re, name_without_ext)

            if not is_movie and not is_series:
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

        if pd.isna(row['Corrected']):
            ui.print_log(f"\n⏭   Ignored (not found) : {row['Original']}")
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
                season_folder = f"Season {season_number.zfill(2)}" 
            else:
                season_folder = "Unknown" 

            tv_show_name = re.sub(r'\s*(?:-\s*)?S\d+E\d+.*$', '', str(movie['Corrected']), flags=re.IGNORECASE).strip()
            tv_show_name = re.sub(r'\s*\[.*?\]', '', tv_show_name).strip()

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

    if new_abs.exists():
        error_msg = f" ❌ Conflict: Target file already exists at {new_abs}"
        raise FileExistsError(error_msg)

    safe_old = make_safe_path(old_abs)
    safe_new = make_safe_path(new_abs)

    try:
        shutil.move(safe_old, safe_new) 
    except Exception as e:
        raise RuntimeError(ui.print_error(f" ❌ Error: Impossible to move the file \n Old path {safe_old} \n New path {safe_new}", e))

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

def move_media_files(paths):
    success_count = 0
    failed_moves = []

    for old, new in paths:
        try:
            move_file(old, new)
            success_count += 1
        except (FileExistsError, RuntimeError) as e:
            ui.print_log(f" ⚠️ Skipping {old.name}: {e} \n")
            failed_moves.append(old.name)
            
    if success_count>0 :
        ui.print_log(f"\n✅ {success_count} files moved successfully!")
    
    if failed_moves:
        ui.print_log(f"❌ {len(failed_moves)} files could not be moved")

    remove_empty_folders(Path(NOT_SORTED_MEDIA_FILES_FOLDER))

def get_file_quality_resolution(file_path):
    metadata = get_metadata_with_ffprobe(file_path)
    
    if not metadata:
        return None, None

    technical_blob = ""
    width_map = {
        3840: "2160p 4k",
        2560: "1440p",
        1920: "1080p",
        1280: "720p",
        720:  "480p"
    }

    # scan data from ffprobe
    streams = metadata.get('streams', [])
    for stream in streams:
        width = stream.get('width')
        if width:
            res_name = width_map.get(width, "")
            technical_blob += f" {width}x{stream.get('height')} {res_name} "
        
        technical_blob += f" {stream.get('codec_name')} {stream.get('pix_fmt')} {stream.get('color_space')} "

    fmt = metadata.get('format', {})
    technical_blob += f" {fmt.get('format_name')} "
    
    tags = fmt.get('tags', {})
    for key, value in tags.items():
        technical_blob += f" {value} "
    
    scan_string = technical_blob.replace('_', ' ').replace('.', ' ')

    # resolution
    final_res = None
    for pattern in RESOLUTION_PATTERNS:
        match = re.search(pattern, scan_string, flags=re.IGNORECASE)
        if match:
            final_res = match.group(0).strip()
            break

    # quality
    final_qual = None
    for pattern in QUALITY_PATTERNS:
        match = re.search(pattern, scan_string, flags=re.IGNORECASE)
        if match:
            final_qual = match.group(0).strip()
            break

    # fallback : bitrate
    if final_qual is None:
        raw_bitrate = fmt.get('bit_rate')
        if raw_bitrate:
            mbps = round(int(raw_bitrate) / 1000000)
            final_qual = f"{mbps}Mbps"

    return final_res, final_qual

def get_metadata_with_ffprobe(file_path):
    # Check if ffprobe is installed on the system
    if not shutil.which("ffprobe"):
        print("❌ Error: ffprobe is not installed or not found in System PATH.")
        return None

    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "stream=width,height,codec_name,pix_fmt,color_space",
        "-show_entries", "format=format_name,bit_rate,tags",
        "-of", "json", 
        file_path
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        ui.print_error("❌ Error: An error occured while running ffprobe",e)
        return None