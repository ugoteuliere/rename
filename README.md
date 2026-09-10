# 🎬 Media Organizer & Renamer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

# Enable AI keyword learning to discover and save missing tags from Gemini
python main.py -L

# Preview changes in simulation mode while learning new tags discovered by Gemini
python main.py -s -L

# Enable AI keyword learning and receive email alerts for newly learned tags
python main.py -L -t
```

## ✨ Features

- **Autonomous Background Watcher**: Runs continuously as a daemon (`-a`, `--autonomous`), polling for new downloads at configurable intervals.
- **Plex-Standard Renaming**: Identifies Movies and TV Shows via TMDB and formats titles following official Plex conventions.
- **Simulation Mode**: Preview proposed renames and file moves without making any changes to your files.
- **Rename-Only Mode**: Rename files in-place without moving them (`-r`), with standalone support for targeting any specific folder directly via `--path`.
- **Gemini AI Fallback & Keyword Learning**: Employs Google's Gemini AI to identify cryptic filenames, with optional auto-learning to discover missing tags.
- **Resolution & Quality Tagging**: Inspects video streams to append resolution and quality tags.
- **Email Notifications**: Receive automated email reports on successful file processing, newly learned AI tags, or when errors occur.
- **Interactive Setup Wizard**: Easily configure your folders, credentials, and options.

## 📖 Documentation

For the full command reference, CLI configuration commands, and setup guides, see the [Documentation](docs/documentation.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.