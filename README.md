# 🎬 Media Organizer & Renamer

A command-line tool that parses messy video filenames, fetches official titles via **The Movie Database (TMDB)**, and automatically organizes them into Movie and TV Show directories following **Plex naming conventions**.

If a filename cannot be identified through standard parsing, the tool can optionally use Google's **Gemini API** as an AI fallback to analyze and correct it.

---

## ⚡ Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **FFmpeg** (includes `ffprobe` for media resolution/quality detection):
  - **Windows (PowerShell)**: `winget install ffmpeg`
  - **macOS (Homebrew)**: `brew install ffmpeg`
  - **Linux (Debian/Ubuntu)**: `sudo apt install ffmpeg`

### 2. Installation
```bash
git clone https://github.com/ugoteuliere/rename.git
cd rename
pip install -r requirements.txt
```

### 3. Configuration
Configure the tool interactively via the setup wizard:
```bash
python main.py configure
```
The wizard guides you through setting your media folder paths, API keys, and preferences with automatic path validation.

---

## 💻 Basic Usage

```bash
# Default: Scan download folder, rename files, and move them to Movies/TV Shows
python main.py

# Rename files in place without moving them
python main.py -r

# Move already cleanly named files into your library
python main.py -m

# Rename files in a custom folder
python main.py -r --path="path/to/folder"
```

### Options
- `-a`, `--auto` : Run automatically without confirmation prompts.
- `-i`, `--ai` : Enable Gemini AI fallback for unrecognizable filenames.
- `-e`, `--mail` : Send an email notification if an error occurs.
- `-l`, `--log` : Write logs to a file instead of the terminal.
- `-v`, `--verbose` : Display detailed error tracebacks.

**Example:**
```bash
python main.py --auto --ai
```

---

## 📖 Documentation

For the full command reference, CLI configuration options, and guides on obtaining TMDB and Gemini API keys, see the [CLI Reference & Documentation](docs/CLI_REFERENCE.md).