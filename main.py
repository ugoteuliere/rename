import sys
from src import ui, files, utils
    
def main():
    # args and env
    utils.verify_arguments()
    utils.verify_path()
    
    # analyse folder
    media_data_table = files.search_media_files()

    # find correct names and rename the files 
    try :
        corrected_data_table = utils.get_corrected_media_filenames(media_data_table)
    except Exception as e:
        ui.print_log(f" ❌ Correction of the filenames failed \n\n # Error : {e} \n\n")
        sys.exit(1)
        
    ui.display_corrected_filenames(corrected_data_table)
    ui.user_confirmation("rename the files")
    corrected_data_table = files.rename_media_files(corrected_data_table)
    
    # sort and move the files
    paths = files.sort_media_files(corrected_data_table)
    ui.display_sorted_files(paths)
    ui.user_confirmation("move the files to the correct folder")
    files.move_media_files(paths)

if __name__ == "__main__":
    main()