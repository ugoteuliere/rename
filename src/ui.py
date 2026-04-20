import sys
import os
from rich.console import Console
from rich.table import Table
from datetime import datetime
from pathlib import Path
import argparse

import config
MOVIES_FOLDER = getattr(config, 'MOVIES_FOLDER', None)
TV_SHOWS_FOLDER = getattr(config, 'TV_SHOWS_FOLDER', None)
GEMINI_API_KEY = getattr(config, 'GEMINI_API_KEY', None)
MAIL = getattr(config, 'MAIL', None)
MAIL_PSWD = getattr(config, 'MAIL_PSWD', None)

LOG_ENABLED = False
MAIL_ENABLED = False
AI_FALLBACK_ENABLED = False
AUTO_ENABLED = False
VERBOSE_ENABLED = False

def parse_arguments():
    global LOG_ENABLED, MAIL_ENABLED, AI_FALLBACK_ENABLED, AUTO_ENABLED, VERBOSE_ENABLED

    description_text = (
        "🎬 Media Organizer & Renamer\n"
        "Automatically parses, renames, and sorts messy video files using the TMDB and Gemini APIs."
    )
    
    epilog_text = (
        "Examples:\n"
        "  python main.py                    (Default: Renames AND moves files)\n"
        "  python main.py -r                 (Only renames the files)\n"
        "  python main.py -m                 (Only moves cleanly named files)\n\n"
        "Documentation & Updates: https://github.com/ugoteuliere/rename"
    )

    parser = argparse.ArgumentParser(
        description=description_text,
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-m", "--only_move", action="store_true", 
                        help="Moves already cleanly named files from the download folder into the Movie/TV Show folders.")
    
    parser.add_argument("-r", "--only_rename", action="store_true", 
                        help="Renames files in the configured download folder but does not move them.")
    
    parser.add_argument("--path", type=str, default=None,
                        help="Target a specific folder for the --only_rename option (e.g., -p \"path/to/custom/folder\").")
    
    parser.add_argument("-i", "--ai", action="store_true", 
                        help="Enables the Gemini AI fallback to intelligently parse and correct highly obfuscated filenames.")
    
    parser.add_argument("-e", "--mail", action="store_true", 
                        help="Sends an automated email notification if a critical error occurs during execution.")
    
    parser.add_argument("-l", "--log", action="store_true", 
                        help="Suppresses terminal output and writes all console messages to a dedicated log file instead.")
    
    parser.add_argument("-a", "--auto", action="store_true", 
                        help="Run the entire script automatically without asking for user confirmation before renaming or before moving the files.")
    
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Display error logs after the error messages.")
    
    args = parser.parse_args()

    # Conflict check: cannot move and rename explicitly at the same time
    if args.only_move and args.only_rename:
        parser.error(
            "Conflict: You cannot use '--only_move' (-m) and '--only_rename' (-r) at the same time.\n"
            "Reason: To perform both actions sequentially (which is the standard behavior), "
            "simply run the script without either flag (e.g., `python main.py`)."
        )

    # Path check: must be used with --only_rename and must exist
    if args.path:
        if not args.only_rename:
            parser.error(
                "Conflict: The '--path' (-p) option can only be used in conjunction with the '--only_rename' (-r) flag."
            )
        if not os.path.isdir(args.path):
            parser.error(
                f"Invalid path: The directory '{args.path}' does not exist or is not a valid folder."
            )

    if args.log:
        LOG_ENABLED = True

    if args.mail:
        if not MAIL or not MAIL_PSWD:
            parser.error(
                "Missing configuration: The '--mail' (-e) option requires 'MAIL' and 'MAIL_PSWD' "
                "to be set in the config.py file."
            )
        MAIL_ENABLED = True

    if args.ai:
        if not GEMINI_API_KEY:
            parser.error(
                "Missing configuration: The '--ai' (-i) option requires 'GEMINI_API_KEY' "
                "to be set in the config.py file."
            )
        AI_FALLBACK_ENABLED = True

    if args.auto:
        AUTO_ENABLED = True
    
    if args.verbose:
        VERBOSE_ENABLED = True
        
    return args

def print_log(message):
    if LOG_ENABLED:
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True) 
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(log_dir, f"{today}.txt")

        hour = datetime.now().strftime("%H:%M:%S")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{hour}] {str(message)}\n")
    else:
        print(message)

def print_error(message, logs):
    if VERBOSE_ENABLED:
        return f"\n {message} \n\n ⤷ Error logs: {logs} \n"
    else:
        return f"\n {message} \n"

def rich_print_log(*args, **kwargs):
    if LOG_ENABLED:
        console_capture = Console(force_terminal=False, no_color=True, width=150)
        with console_capture.capture() as capture:
            console_capture.print(*args, **kwargs)
            
        texte_brut = capture.get()
        if texte_brut.strip():
            print_log("\n" + texte_brut.rstrip("\n"))
    else:
        console = Console()
        console.print(*args, **kwargs)

def display_corrected_filenames(clean_data_table):
    
    movies_df = clean_data_table[clean_data_table['Media'] == 'movie']
    tv_shows_df = clean_data_table[clean_data_table['Media'] == 'tv']

    if tv_shows_df.empty and movies_df.empty:
        rich_print_log("[yellow]No media files detected.[/yellow]")
        return

    # --- MOVIES Table ---
    if not movies_df.empty:
        rich_print_log()
        table_movies = Table(title="🍿 [bold magenta]Movies[/bold magenta]", title_justify="left")
        
        table_movies.add_column("Original", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_movies.add_column("Corrected", style="green", no_wrap=True, max_width=40, overflow="ellipsis")

        for _, row in movies_df.iterrows():
            if row['Original'] != row['Corrected']:
                table_movies.add_row(str(row['Original']), str(row['Corrected']))

        rich_print_log(table_movies)

    # --- TV Shows table ---
    if not tv_shows_df.empty:
        rich_print_log()
        table_tv = Table(title="📺 [bold blue]TV Shows[/bold blue]", title_justify="left")
        
        table_tv.add_column("Original", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_tv.add_column("Season", justify="center", style="yellow")
        table_tv.add_column("Épisode", justify="center", style="yellow")
        table_tv.add_column("Corrected", style="green", no_wrap=True, max_width=40, overflow="ellipsis")

        for _, row in tv_shows_df.iterrows():
            if row['Original'] != row['Corrected']:
                table_tv.add_row(
                    str(row['Original']), 
                    str(row['Season']), 
                    str(row['Episode']), 
                    str(row['Corrected'])
                )

        rich_print_log(table_tv)
        rich_print_log()

def display_sorted_files(paths):
    movie_dir = Path(MOVIES_FOLDER)
    tv_dir = Path(TV_SHOWS_FOLDER)

    movies_data = []
    tv_shows_data = []

    # sort
    for chemin_ancien, chemin_nouveau in paths:
        p_new = Path(chemin_nouveau)
        old_name = str(Path(chemin_ancien).name)

        if p_new.is_relative_to(movie_dir):
            short_path = Path(movie_dir.name) / p_new.relative_to(movie_dir)
            movies_data.append((old_name, str(short_path)))
            
        elif p_new.is_relative_to(tv_dir):
            short_path = Path(tv_dir.name) / p_new.relative_to(tv_dir)
            tv_shows_data.append((old_name, str(short_path)))

    if not movies_data and not tv_shows_data:
        rich_print_log("[yellow]No sorted files to display.[/yellow]")
        return

    # movies
    if movies_data:
        rich_print_log()
        table_movies = Table(title="🍿 [bold magenta]Sorted Movies[/bold magenta]", title_justify="left")
        
        table_movies.add_column("Old", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_movies.add_column("New Path", style="green", no_wrap=True, max_width=70, overflow="ellipsis")

        for old, new in movies_data:
            table_movies.add_row(old, new)

        rich_print_log(table_movies)

    # tv shows
    if tv_shows_data:
        rich_print_log()
        table_tv = Table(title="📺 [bold blue]Sorted TV Shows[/bold blue]", title_justify="left")
        
        table_tv.add_column("Old", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_tv.add_column("New Path", style="green", no_wrap=True, max_width=70, overflow="ellipsis")

        for old, new in tv_shows_data:
            table_tv.add_row(old, new)

        rich_print_log(table_tv)
        rich_print_log()

def user_confirmation(message):
    if not(AUTO_ENABLED):
        console = Console()
        try:
            console.print(f"\n➡️  Press [green][Entrer][/green] to {message}, or [red][Ctrl+C][/red] to cancel...", end="")
            input()
        except KeyboardInterrupt:
            console.print("\n\n[red] ❌ Operation cancelled by the user. [/red]")
            sys.exit(1)