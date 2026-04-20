import sys
import traceback
from src import ui, files, utils, mail
    
def main():
    try:
        # verify environment
        args = ui.parse_arguments()
        
        if not(args.path):
            utils.verify_folders()
        
        # analyse folder
        messy_data_table, clean_data_table = files.search_media_files(args.path)

        # find correct names and rename the files 
        if not(args.only_move):
            if not(messy_data_table.empty):
                clean_data_table = utils.get_corrected_media_filenames(messy_data_table,clean_data_table)
                ui.display_corrected_filenames(clean_data_table)
                ui.user_confirmation("rename the files")
                clean_data_table = files.rename_media_files(clean_data_table)
            else: 
                ui.print_log("❌ No media files to rename\n")

        # sort the files and move them to the correct folder
        if not(args.only_rename):
            # sort and move the files
            if not(clean_data_table.empty):
                paths = files.sort_media_files(clean_data_table)
                ui.display_sorted_files(paths)
                ui.user_confirmation("move the files to the correct folder")
                files.move_media_files(paths)
            else:
                ui.print_log("❌ No media files to sort and move\n")
    
    except RuntimeError as error_message:
        ui.print_log(error_message)
        mail.send_email(f"The script failed. Please review the following error message: \n\n ⤷ Error message: {error_message} \n")
        sys.exit(1)

    except Exception as e:
        full_traceback = traceback.format_exc() 
        error_message = f" ❌ Error: A critical, unexpected error occurred  \n\n ⤷ Exception: {e} \n\n ⤷ Error logs: {full_traceback} \n"
        ui.print_log(error_message)
        mail.send_email(f"The script failed. Please review the following error message: \n\n ⤷ Error message: {error_message} \n")
        sys.exit(1)
        

if __name__ == "__main__":
    main()