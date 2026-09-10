# 🎬 Media Organizer & Renamer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A command-line tool that parses messy video filenames, fetches official titles via **The Movie Database (TMDB)**, and automatically organizes them into Movie and TV Show directories following **Plex naming conventions**.

If a filename cannot be identified through standard parsing, the tool can optionally use Cloud AI models (**Google Gemini**, **Groq Cloud**, **OpenRouter**, or **Cloudflare Workers AI**) as an intelligent fallback to analyze and correct it.

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
The wizard guides you through setting your folder paths (downloads, movies, TV shows), API keys (TMDB and optional AI providers), and preferences.

## 💻 Basic Usage

```bash
# Scan download folder, rename files, and move them to Movies/TV Shows (Pure local parsing & TMDB)
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

# Enable Cloud AI fallback for highly cryptic filenames
python main.py -i

# Choose a specific AI cloud provider (e.g. Groq, OpenRouter, Cloudflare, or Gemini)
python main.py -i --provider groq

# Enable AI keyword learning to discover and save missing tags into gemini_tags.json
python main.py -L

# Preview changes in simulation mode while learning new tags discovered by AI
python main.py -s -L

# Enable AI keyword learning and receive email alerts for newly learned tags
python main.py -L -t
```

## ✨ Features

- **Autonomous Background Watcher**: Runs continuously as a daemon (`-a`, `--autonomous`), polling for new downloads at configurable intervals.
- **Plex-Standard Renaming**: Identifies Movies and TV Shows via TMDB and formats titles following official Plex conventions.
- **100% Usable Without AI**: Fully operational out-of-the-box using local regex/PTN parsing and TMDB queries. AI fallback (`-i`) and keyword learning (`-L`) are two independent, completely optional flags.
- **Multi-Cloud AI Fallback & Failover**: Supports **Google Gemini** (`gemini-2.5-flash-lite`), **Groq Cloud** (`llama-3.3-70b-versatile`), **OpenRouter** (free models), and **Cloudflare Workers AI** (`llama-3.1-8b-instruct`). If a provider encounters a rate limit or quota exhaustion, it automatically fails over to the next configured cloud provider for that batch.
- **TMDB Match Probability Scorer**: Mathematically evaluates the likelihood that a local TMDB match is accurate before accepting it. If confidence is low, the item is queued for AI verification.
- **Efficient Batch Processing**: Bundles files needing AI analysis into batches (up to 25 items) to slash latency, tokens, and API requests.
- **Simulation Mode**: Preview proposed renames and file moves without making any changes to your files.
- **Rename-Only Mode**: Rename files in-place without moving them (`-r`), with standalone support for targeting any specific folder directly via `--path`.
- **Resolution & Quality Tagging**: Inspects video streams to append resolution and quality tags.
- **Email Notifications**: Receive automated email reports on successful file processing, newly learned AI tags, or when errors occur.
- **Interactive Setup Wizard**: Easily configure your folders, credentials, and options.

## 📖 Documentation

For the full command reference, CLI configuration commands, and setup guides, see the [Documentation](docs/documentation.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.