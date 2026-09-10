# Media Organizer & Renamer

[![CI](https://github.com/ugoteuliere/rename/actions/workflows/github-ci.yml/badge.svg)](https://github.com/ugoteuliere/rename/actions/workflows/github-ci.yml)
[![Release](https://img.shields.io/github/v/release/ugoteuliere/rename?color=blue)](https://github.com/ugoteuliere/rename/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A CLI tool that parses video filenames, retrieves official titles via **The Movie Database (TMDB)**, and organizes files into Movie and TV Show directories according to **Plex naming conventions**.

When standard regex and parsing algorithms fail to identify heavily obfuscated filenames, the tool optionally falls back to Cloud AI providers (**Google Gemini**, **Groq Cloud**, **OpenRouter**, or **Cloudflare Workers AI**).

## Quick Start

### 1. Installation

#### Option A: Standalone Executable (Recommended — No Python Required)
Download the self-contained binary for your operating system directly from [GitHub Releases](https://github.com/ugoteuliere/rename/releases/latest):

* **Windows**: Download `media-organizer-windows-x64.exe` (or `.zip`) $\rightarrow$ double-click to configure, or run from PowerShell / CMD.
* **Linux**: Download `media-organizer-linux-x64` $\rightarrow$ make executable (`chmod +x media-organizer-linux-x64`) $\rightarrow$ run `./media-organizer-linux-x64`.
* **macOS**: Download `media-organizer-macos-arm64` (Apple Silicon M1/M2/M3) or `media-organizer-macos-x64` (Intel) $\rightarrow$ make executable (`chmod +x media-organizer-macos-*`) $\rightarrow$ run `./media-organizer-macos-*`.

#### Option B: From Source (Python 3.10+)

```bash
git clone https://github.com/ugoteuliere/rename.git
cd rename
pip install -r requirements.txt
```

### 2. Configuration

Configure storage folders, API keys, and options using either the graphical interface or the terminal wizard:

```bash
# Launch Graphical Configuration Tool (GUI)
media-organizer --gui

# Launch Terminal Wizard
media-organizer configure
```

### 3. Run

```bash
# Rename and sort media files
media-organizer
```

## Operational Modes

| Command | Mode | Description |
| :--- | :--- | :--- |
| `python main.py` | **Rename & Move** | Scans download folder, matches TMDB, renames and moves items to Movies/TV Shows. |
| `python main.py -r` | **Rename Only** | Renames files in-place without moving them to library directories. |
| `python main.py -s` | **Simulation** | Dry-run preview: prints proposed renames without modifying files on disk. |
| `python main.py -a` | **Autonomous** | Continuous background daemon polling download folder every X minutes (silent terminal, writes to log file). |
| `python main.py -i` | **Cloud AI Fallback** | Uses Cloud AI models to resolve obfuscated filenames when local parsing fails. |
| `python main.py -L` | **Keyword Learning** | Discovers missing release tags via AI and saves them to `gemini_tags.json`. |
| `python main.py --path="<dir>"` | **Custom Target** | Overrides incoming download folder, or targets a specific folder with `-r`. |

## Options Cheat Sheet

| Flag | Long Option | Config Setting | Description |
| :--- | :--- | :--- | :--- |
| `-s` | `--simulate` | — | Dry-run preview without modifying disk or sending emails. |
| `-r` | `--only-rename` | — | Renames files in-place without moving. |
| `-a` | `--autonomous` | `options.autonomous` | Continuous polling daemon (automatically enables `-b` and writes logs silently to file). |
| — | `--interval <min>` | `options.polling_interval` | Polling interval in minutes for autonomous mode (default: `15`). |
| `-b` | `--bypass` | `options.bypass` | Bypasses interactive confirmation prompts. |
| `-i` | `--ai` | `options.ai` | Enables Cloud AI fallback for unrecognized filenames. |
| `-L` | `--learn` | `options.learn` | Enables AI keyword learning (saves discovered tags). |
| — | `--provider <name>` | `options.ai_provider` | Selects active provider (`auto`, `gemini`, `groq`, `openrouter`, `cloudflare`). |
| `-R` | `--resolution` | `options.resolution` | Appends video resolution tags (e.g. `[1080p]`, `[4K]`). Requires `ffprobe`. |
| `-q` | `--quality` | `options.quality` | Appends video quality tags (e.g. `[BluRay]`, `[WEB-DL]`). Requires `ffprobe`. |
| `-l` | `--log` | `options.log` | Writes console output to daily log files (`log/YYYY-MM-DD.txt`). |
| `-v` | `--verbose` | `options.verbose` | Displays detailed error tracebacks in console output. |
| — | `--notify-success` | `options.notify_on_success` | Sends an email notification on successful processing. |
| — | `--notify-error` | `options.notify_on_error` | Sends an email notification when an error occurs. |
| `-t` | `--notify-tag` | `options.notify_on_tag` | Sends an email notification when a new keyword tag is learned. |

## Documentation

For directory structure details, provider tutorials, free quota limits, mathematical probability scoring, and headless deployment guides, see the [Full Documentation](docs/documentation.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.