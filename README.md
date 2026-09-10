# 🎬 Media Organizer & Renamer

A command-line tool that parses messy video filenames, fetches official titles via **The Movie Database (TMDB)**, and automatically organizes them into Movie and TV Show directories following **Plex naming conventions**.

If a filename cannot be identified through standard parsing, the tool can optionally use Google's **Gemini API** as an AI fallback to analyze and correct it.

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/ugoteuliere/rename.git
cd rename
pip install -r requirements.txt
```

### 2. Configuration
Configure the tool interactively via the setup wizard:
```bash
python main.py configure
```
The wizard guides you through setting your folder paths (downloads, movies, TV shows), API keys, and preferences.

## 💻 Basic Usage

```bash
# Scan download folder, rename files, and move them to Movies/TV Shows
python main.py

# Autonomous mode: continuous background polling every X minutes
python main.py -a

# Autonomous mode with custom 10-minute polling interval
python main.py -a --interval 10

# Rename and move from a specific folder (overrides download folder)
python main.py --path="path/to/folder"

# Rename files in-place without moving them
python main.py -r

# Rename files in a specific folder in-place (standalone, no folder setup required)
python main.py -r --path="path/to/folder"
```

## ✨ Features

- **Autonomous Background Watcher**: Runs continuously as a daemon (`-a`, `--autonomous`), polling for new downloads at configurable intervals.
- **Plex-Standard Renaming**: Automatically identifies Movies and TV Shows via TMDB and formats titles following official Plex conventions.
- **Simulation Mode**: Safely preview proposed renames and file moves without making any changes to your files.
- **Rename-Only Mode**: Cleanly rename files in-place without moving them (`-r`), with standalone support for targeting any specific folder directly via `--path` without configuring library paths.
- **Gemini AI Fallback**: Employs Google's Gemini AI to identify cryptic or obfuscated filenames when standard matching fails.
- **Resolution & Quality Tagging**: Inspects video streams to append resolution (e.g. `[1080p]`, `[4K]`) and quality tags (e.g. `[FullHD BluRay]`).
- **Email Notifications**: Receive automated email reports on successful file processing or when errors occur (ideal for server cron jobs).
- **Interactive Setup Wizard**: Easily configure your folders, API credentials, and persistent defaults with built-in best practice tips.

## 📖 Documentation

For the full command reference, CLI configuration commands, and setup guides, see the [Documentation](docs/documentation.md).