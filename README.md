# 🎬 Media Organizer & Renamer

An automated, intelligent command-line tool written in Python that scans a download directory, parses messy video filenames, fetches official titles via the **TMDB API**, and cleanly categorizes them into organized Movie and TV Show directories.

## ✨ Features

* **Smart Parsing:** Uses `PTN` (Parse Torrent Name) to extract titles, years, seasons, and episodes from cluttered filenames.
* **TMDB Integration:** Automatically queries The Movie Database (TMDB) to retrieve official titles and release years.
* **Automated Sorting:** Automatically creates necessary folders and moves media into structured directories:
    * Movies: `Films/Title (Year).mkv`
    * TV Shows: `Séries/Show Name/Saison XX/Title SXXEXX.mkv`
* **Dual Modes:** Run safely in `manual` mode to review changes before committing, or `auto` mode for background automation.
* **Long Path Support:** Safely handles Windows long paths to prevent file operation errors.

## 📁 Required Directory Structure

The script is strictly designed to operate within a specific root directory. Before running the script, your `PATH` must contain **only** these three folders:

```text
📂 Your_Base_Directory/
 ├── 📂 .download/       (Output JDownloader)
 ├── 📂 Films/           (Movies will be moved here)
 └── 📂 Séries/          (TV Shows will be moved here)
Note: The script will deliberately exit if unexpected folders are found in the root directory to prevent accidental data modification.
```

# 🚀 Setup
### 1. Clone the repository:

```Bash
git clone [https://github.com/ugoteulier/rename.git](https://github.com/ugoteuliere/rename.git)
cd rename
```

### 2. Install dependencies:
Ensure you have Python 3.7+ installed. Run the following command:

```Bash
pip install -r requirements.txt
```

### 3. Configure Environment:
You must create a config.py file in the root directory containing your TMDB API key and base path:

```Python
# config.py
API_KEY = "your_tmdb_api_key_here"
PATH = "C:/Path/To/Your_Base_Directory/"
```

# 💻 How to use
Run the script via the command line. You can choose between two modes:

1. Auto Mode (Default)
Automatically renames and moves files without asking for user confirmation. Ideal for cron jobs or automated tasks.

```Bash
python main.py
# or
python main.py auto
```

2. Manual Mode
Displays the planned file renames and moves in a formatted table, pausing for your explicit confirmation (Enter to proceed, Ctrl+C to cancel).

```Bash
python main.py manual
```

# ⚠️ Notes
Supported Extensions: .mkv, .mp4, .avi, .mov, .wmv, .m4v

Empty folders left in the .download directory are automatically cleaned up after a successful run.

### Tag Configuration:
Ensure you have a src/data.py file that exports a TAGS list (used to clean out common torrent groups/tags if standard parsing fails):

```Python
# src/data.py
TAGS = ["1080p", "x264", "WebRip", "Bluray"] # Add your tags here
```

# Flow chart 

![flowchart](docs/flowchart_rename.drawio.svg)

# API request

![flowchart_api](docs/api_request_flowchart.drawio.svg)