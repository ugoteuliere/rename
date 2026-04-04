import sys
import os
from rich.console import Console
from rich.table import Table
from datetime import datetime
from pathlib import Path
from config import PATH

def print_log(message):
    if "log" in sys.argv:
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True) 
        today = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(log_dir, f"{today}.txt")

        hour = datetime.now().strftime("%H:%M:%S")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{hour}] {str(message)}\n")
    else:
        print(message)

def rich_print_log(*args, **kwargs):
    if "log" in sys.argv:
        console_capture = Console(force_terminal=False, no_color=True, width=150)
        with console_capture.capture() as capture:
            console_capture.print(*args, **kwargs)
            
        texte_brut = capture.get()
        if texte_brut.strip():
            print_log("\n" + texte_brut.rstrip("\n"))
    else:
        console = Console()
        console.print(*args, **kwargs)

def display_corrected_filenames(corrected_data_table):
    
    movies_df = corrected_data_table[corrected_data_table['Media'] == 'movie']
    tv_shows_df = corrected_data_table[corrected_data_table['Media'] == 'tv']

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
            table_movies.add_row(str(row['Original']), str(row['Corrected']))

        rich_print_log(table_movies)

    # --- TV Shows table ---
    if not tv_shows_df.empty:
        rich_print_log()
        table_tv = Table(title="📺 [bold blue]TV Shows[/bold blue]", title_justify="left")
        
        table_tv.add_column("Original", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_tv.add_column("Query", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
        table_tv.add_column("Season", justify="center", style="yellow")
        table_tv.add_column("Épisode", justify="center", style="yellow")
        table_tv.add_column("Corrected", style="green", no_wrap=True, max_width=40, overflow="ellipsis")

        for _, row in tv_shows_df.iterrows():
            table_tv.add_row(
                str(row['Original']), 
                str(row['Query']),
                str(row['Season']), 
                str(row['Episode']), 
                str(row['Corrected'])
            )

        rich_print_log(table_tv)
        rich_print_log()

def display_sorted_files(paths):
    rich_print_log()
    table = Table(title="➡️  [blue]Sorted files[/blue]", title_justify="left")
    
    table.add_column("Old", style="white", no_wrap=True, max_width=40, overflow="ellipsis")
    table.add_column("New", style="green", no_wrap=True, max_width=40, overflow="ellipsis")

    for chemin_ancien, chemin_nouveau in paths:
        racine_absolue = Path(PATH).resolve()
        table.add_row(
            str(chemin_ancien.resolve().relative_to(racine_absolue)), 
            str(chemin_nouveau.resolve().relative_to(racine_absolue))
        )

    rich_print_log(table)
    rich_print_log()

def user_confirmation(message):
    if "manual" in sys.argv:
        console = Console()
        try:
            console.print(f"\n➡️  Press [green][Entrer][/green] to {message}, or [red][Ctrl+C][/red] to cancel...", end="")
            input()
        except KeyboardInterrupt:
            console.print("\n\n[red]❌ Operation cancelled by the user. [/red]")
            sys.exit(1)