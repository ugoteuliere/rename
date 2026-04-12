import sys
import traceback
from src import ui, files, utils
    
def main():
    try:
        # verify environment
        utils.verify_arguments()
        utils.verify_path()
        
        # analyse folder
        media_data_table = files.search_media_files()

        # find correct names and rename the files 
        corrected_data_table = utils.get_corrected_media_filenames(media_data_table)

        ui.display_corrected_filenames(corrected_data_table)
        ui.user_confirmation("rename the files")
        corrected_data_table = files.rename_media_files(corrected_data_table)
        
        # sort and move the files
        paths = files.sort_media_files(corrected_data_table)
        ui.display_sorted_files(paths)
        ui.user_confirmation("move the files to the correct folder")
        files.move_media_files(paths)
    
    except RuntimeError as e:
        ui.print_log(e)
        sys.exit(1)

    except Exception as e:
        full_traceback = traceback.format_exc() 
        
        ui.print_log(f" ❌ Error: A critical, unexpected error occurred  \n\n ⤷ Error logs: {full_traceback} \n")
        sys.exit(1)
        

if __name__ == "__main__":
    main()