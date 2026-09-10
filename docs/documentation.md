# Documentation

Technical guide and reference for the Media Organizer & Renamer.

---

## Table of Contents

1. [Folder Structure & Plex Standards](#1-folder-structure--plex-standards)
2. [Configuration](#2-configuration)
   - [Graphical Configuration Tool (GUI)](#graphical-configuration-tool-gui)
   - [Terminal Setup Wizard](#terminal-setup-wizard)
   - [Command-Line Configuration (Inspect & Update)](#command-line-configuration-inspect--update)
   - [Environment Variables](#environment-variables)
   - [Configuration File Schema](#configuration-file-schema)
3. [Operational Modes](#3-operational-modes)
   - [Default: Rename & Move](#default-rename--move)
   - [Rename Only (In-Place)](#rename-only-in-place)
   - [Simulation Mode (Dry-Run)](#simulation-mode-dry-run)
   - [Autonomous Background Watcher](#autonomous-background-watcher)
4. [Options & CLI Flags](#4-options--cli-flags)
5. [Matching & Multi-Cloud AI Architecture](#5-matching--multi-cloud-ai-architecture)
   - [Metadata Extraction Pipeline](#metadata-extraction-pipeline)
   - [TMDB Match Probability Scorer](#tmdb-match-probability-scorer)
   - [Batch Processing & Failover](#batch-processing--failover)
6. [Provider Setup Guides & Free Quotas](#6-provider-setup-guides--free-quotas)
   - [The Movie Database (TMDB)](#the-movie-database-tmdb)
   - [Google Gemini](#google-gemini)
   - [Groq Cloud](#groq-cloud)
   - [OpenRouter](#openrouter)
   - [Cloudflare Workers AI](#cloudflare-workers-ai)
7. [Keyword & Tag Management](#7-keyword--tag-management)
8. [Email Alerts & System Setup](#8-email-alerts--system-setup)
   - [Gmail SMTP Setup](#gmail-smtp-setup)
   - [FFmpeg / ffprobe Setup](#ffmpeg--ffprobe-setup)

---

## 1. Folder Structure & Plex Standards

The application operates on three directories:
* **Downloads folder** (`paths.not_sorted_media_files_folder`): incoming, unsorted media files.
* **Movies folder** (`paths.movies_folder`): destination directory for processed movies.
* **TV Shows folder** (`paths.tv_shows_folder`): destination directory for processed series.

These folders are independent and can be located anywhere on local storage, external drives, or SMB/NFS network shares.

### Plex Standard Formatting
Processed files follow official Plex naming conventions:
* **Movies**: `Title (Year).ext` or `Title (Year) [Resolution Quality].ext`
* **TV Shows**: `Show Name/Season XX/Show Name - SXXEXX.ext`

---

## 2. Configuration

### Graphical Configuration Tool (GUI)
Launch the graphical settings window using Python's built-in `tkinter` interface (requires no extra packages):

```bash
python main.py configure --gui
# or
python main.py config --gui
```

Features:
* Native OS folder pickers (`Browse...` buttons) for library paths.
* Password-masked inputs with toggle visibility for API credentials.
* In-app connection verification buttons for TMDB, Gemini, Groq, OpenRouter, and Cloudflare.
* Toggle switches for automation, logging, and video stream metadata tags.
* Test email button to verify SMTP credentials before running headless.

---

### Terminal Setup Wizard
For headless environments or SSH sessions, run the interactive terminal wizard:

```bash
# Categorized menu wizard
python main.py configure

# Direct category setup
python main.py configure --paths     # Media library directories
python main.py configure --ai        # TMDB and Cloud AI credentials
python main.py configure --email     # Gmail SMTP credentials and triggers
python main.py configure --options   # Automation and logging defaults
python main.py configure --video     # FFmpeg resolution and quality tags
python main.py configure --full      # Step-by-step through all settings without menu
```

---

### Command-Line Configuration (Inspect & Update)

```bash
# List all settings (sensitive values are masked)
python main.py config --list

# List all settings unmasked
python main.py config --list --show-secrets

# Print active config file path
python main.py config --path

# Get a specific value
python main.py config --get paths.movies_folder
python main.py config --get api.tmdb_api_key

# Set a specific value
python main.py config --set paths.movies_folder "D:/Media/Movies"
python main.py config --set api.groq_api_key "gsk_..."
python main.py config --set options.bypass true

# Unset / delete a configuration key
python main.py config --unset api.gemini_api_key
```

---

### Environment Variables

All settings can be overridden by environment variables (useful for containerized or CI/CD deployments):

| Config Key | Environment Variable | Expected Value |
| :--- | :--- | :--- |
| `paths.movies_folder` | `RENAME_MOVIES_FOLDER` | Valid directory path |
| `paths.tv_shows_folder` | `RENAME_TV_SHOWS_FOLDER` | Valid directory path |
| `paths.not_sorted_media_files_folder` | `RENAME_NOT_SORTED_MEDIA_FILES_FOLDER` | Valid directory path |
| `api.tmdb_api_key` | `RENAME_TMDB_API_KEY` | TMDB API key or Bearer token |
| `api.gemini_api_key` | `RENAME_GEMINI_API_KEY` | Google Gemini API key |
| `api.groq_api_key` | `RENAME_GROQ_API_KEY` | Groq Cloud API key |
| `api.openrouter_api_key` | `RENAME_OPENROUTER_API_KEY` | OpenRouter API key |
| `api.cloudflare_api_token` | `RENAME_CLOUDFLARE_API_TOKEN` | Cloudflare Workers AI token |
| `api.cloudflare_account_id` | `RENAME_CLOUDFLARE_ACCOUNT_ID` | Cloudflare 32-character account ID |
| `options.ai_provider` | `RENAME_AI_PROVIDER` | `auto`, `gemini`, `groq`, `openrouter`, `cloudflare` |
| `options.tmdb_min_confidence` | `RENAME_TMDB_MIN_CONFIDENCE` | Float `0.0` to `1.0` (default: `0.75`) |
| `options.ai_min_confidence` | `RENAME_AI_MIN_CONFIDENCE` | Float `0.0` to `1.0` (default: `0.70`) |
| `options.bypass` | `RENAME_BYPASS` | Boolean (`true`/`false` or `y`/`n`) |
| `options.autonomous` | `RENAME_AUTONOMOUS` | Boolean |
| `options.polling_interval` | `RENAME_POLLING_INTERVAL` | Integer $\ge 1$ (minutes) |
| `options.ai` | `RENAME_AI` | Boolean |
| `options.learn` | `RENAME_LEARN` | Boolean |
| `options.resolution` | `RENAME_RESOLUTION` | Boolean |
| `options.quality` | `RENAME_QUALITY` | Boolean |
| `options.log` | `RENAME_LOG` | Boolean |
| `options.verbose` | `RENAME_VERBOSE` | Boolean |
| `mail.mail` | `RENAME_MAIL` | Sender Gmail address |
| `mail.mail_pswd` | `RENAME_MAIL_PSWD` | 16-character Gmail App Password |

---

### Configuration File Schema

Default file location:
* **Windows**: `%APPDATA%\rename\config.ini`
* **Linux / macOS**: `~/.config/rename/config.ini`

```ini
[paths]
movies_folder = /media/storage/Movies
tv_shows_folder = /media/storage/TV_Shows
not_sorted_media_files_folder = /media/storage/.downloads

[api]
tmdb_api_key = your_tmdb_api_key
gemini_api_key = your_gemini_api_key
groq_api_key = your_groq_api_key
openrouter_api_key = your_openrouter_api_key
cloudflare_api_token = your_cloudflare_api_token
cloudflare_account_id = your_cloudflare_account_id

[options]
ai_provider = auto
tmdb_min_confidence = 0.75
ai_min_confidence = 0.70
resolution = false
quality = false
bypass = false
autonomous = false
polling_interval = 15
ai = false
learn = false
log = false
verbose = false
notify_on_success = false
notify_on_error = true
notify_on_tag = false

[mail]
mail = your_email@gmail.com
mail_pswd = your_16_char_app_password
```

---

## 3. Operational Modes

### Default: Rename & Move
Scans incoming downloads, queries TMDB, prompts for user confirmation, renames files, and moves them to destination folders.
```bash
python main.py

# Override source folder
python main.py --path="/path/to/incoming"
```

### Rename Only (In-Place)
Renames files in-place without moving them to destination directories.
```bash
python main.py -r
# or
python main.py --only-rename

# Target any custom folder standalone (no library folder configuration required)
python main.py -r --path="/path/to/folder"
```

### Simulation Mode (Dry-Run)
Previews proposed renames and destination paths without writing to disk or sending emails.
```bash
python main.py -s
# or
python main.py --simulate

# Combine with other flags
python main.py -s -i --path="/path/to/test"
```

### Autonomous Background Watcher
Runs as a persistent daemon polling the incoming folder periodically.
```bash
# Polling interval from config (default: 15 min)
python main.py -a

# Custom polling interval (e.g. 5 minutes)
python main.py -a --interval 5
```
Autonomous mode automatically enables `-b` (`bypass`) and `-l` (`log`), skips in-progress downloads (`.crdownload`, `.part`, `.tmp`), and terminates cleanly on `SIGINT` / `Ctrl+C`.

---

## 4. Options & CLI Flags

| Flag | Long Option | Config Key | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `-s` | `--simulate` | — | `false` | Dry-run simulation preview. |
| `-r` | `--only-rename` | — | `false` | Renames files in-place without moving them. |
| `-a` | `--autonomous` | `options.autonomous` | `false` | Runs background watcher daemon. |
| — | `--interval <min>` | `options.polling_interval` | `15` | Polling interval for autonomous mode (minutes). |
| `-b` | `--bypass` | `options.bypass` | `false` | Bypasses interactive confirmation prompts. |
| `-i` | `--ai` | `options.ai` | `false` | Enables Cloud AI fallback for unrecognizable filenames. |
| `-L` | `--learn` | `options.learn` | `false` | Enables keyword learning to save newly discovered tags. |
| — | `--provider <p>` | `options.ai_provider` | `auto` | Selects AI provider (`auto`, `gemini`, `groq`, `openrouter`, `cloudflare`). |
| `-R` | `--resolution` | `options.resolution` | `false` | Appends video resolution tags (`[1080p]`, `[4K]`). Requires `ffprobe`. |
| `-q` | `--quality` | `options.quality` | `false` | Appends video quality tags (`[BluRay]`, `[WEB-DL]`). Requires `ffprobe`. |
| `-l` | `--log` | `options.log` | `false` | Writes console output to `log/YYYY-MM-DD.txt`. |
| `-v` | `--verbose` | `options.verbose` | `false` | Displays full error stack traces on failure. |
| — | `--notify-success` | `options.notify_on_success` | `false` | Sends email notification on successful processing. |
| — | `--notify-error` | `options.notify_on_error` | `true` | Sends email notification when an error occurs. |
| `-t` | `--notify-tag` | `options.notify_on_tag` | `false` | Sends email notification when a new keyword tag is learned. |
| — | `--path="<dir>"` | — | Incoming dir | Targets a specific folder. |

---

## 5. Matching & Multi-Cloud AI Architecture

```
Raw Filename 
    │
    ▼
[Regex & PTN Sanitization] ──► [TMDB Metadata Query]
                                         │
                                         ▼
                             [Match Probability Scorer]
                                         │
                        ┌────────────────┴────────────────┐
                        │ Probability >= 0.75              │ Probability < 0.75
                        ▼                                 ▼
                 [Accept Match]                 [Queue for AI Batch]
                                                          │
                                                          ▼
                                            [Multi-Cloud AI Orchestrator]
                                            (Gemini / Groq / OpenRouter / Cloudflare)
                                                          │
                                                          ▼
                                            [Pydantic Validation & Sanitization]
```

### Metadata Extraction Pipeline
1. **Local Cleaning**: Strips known release tags (from `data/tags.json`, `custom_tags.json`, `gemini_tags.json`), URLs, and technical markers.
2. **Local Parsing**: Uses PTN to isolate candidate title, release year, season, and episode.
3. **TMDB Query**: Queries The Movie Database in `en-US` (and `fr-FR` for French productions).
4. **Probability Scoring**: Evaluates candidate validity using token overlap and release year proximity.
5. **AI Batch Fallback**: Items with low confidence or failed lookups are bundled into batches of up to 25 items per request.

### TMDB Match Probability Scorer
Computes a match probability $P \in [0.0, 1.0]$:
$$P = 0.50 \cdot \text{SequenceSimilarity} + 0.35 \cdot \text{TokenOverlap} + 0.15 \cdot \text{YearProximity}$$
* If $P \ge 0.75$, the match is accepted directly.
* If $P < 0.75$ and AI fallback is enabled (`-i`), the item is queued for cloud AI verification.

### Batch Processing & Failover
* Items requiring AI are grouped into chunks of up to 25 files to minimize API roundtrips.
* Exactly one provider executes each batch.
* If the active provider returns an HTTP 429 (`RESOURCE_EXHAUSTED` / rate limit / quota exceeded), the orchestrator automatically bypasses it and retries the batch on the next configured provider.

---

## 6. Provider Setup Guides & Free Quotas

### The Movie Database (TMDB)
Core metadata provider for official titles, years, and season numbers.
* **Cost**: Free.
* **Setup**:
  1. Register an account at [themoviedb.org](https://www.themoviedb.org/).
  2. Navigate to **Settings** > **API** > **Request an API Key** > **Developer**.
  3. Copy your **API Key (v3 auth)** and configure it:
     ```bash
     python main.py config --set api.tmdb_api_key "<your_tmdb_key>"
     ```

---

### Google Gemini
* **Model**: `gemini-3.5-flash-lite` (with fallbacks `gemini-2.5-flash-lite`, `gemini-2.5-flash`).
* **Free Quota**: 15 requests/minute, 1,500 requests/day.
* **Setup**:
  1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
  2. Click **Get API key** > **Create API key**.
  3. Copy your key (`AIzaSy...`) and configure it:
     ```bash
     python main.py config --set api.gemini_api_key "<your_gemini_key>"
     ```

---

### Groq Cloud
* **Models**: `openai/gpt-oss-20b`, `llama-3.3-70b-versatile`, `openai/gpt-oss-120b`.
* **Free Quota**: 30 requests/minute, 14,400 requests/day (~0.03s latency).
* **Setup**:
  1. Visit [Groq Cloud Console](https://console.groq.com/keys).
  2. Sign in and click **Create API Key**.
  3. Copy your key (`gsk_...`) and configure it:
     ```bash
     python main.py config --set api.groq_api_key "<your_groq_key>"
     ```

---

### OpenRouter
* **Models**: Free tier models (`liquid/lfm-2.5-2.6b:free`, `google/gemma-4-26b-a4b-it:free`, `meta-llama/llama-3.3-70b-instruct:free`).
* **Cost**: $0.00 (setting a credit limit of $0 ensures you are never charged).
* **Free Quota**: ~20 requests/minute, ~200 requests/day without credits.
* **Setup**:
  1. Visit [OpenRouter](https://openrouter.ai/settings/keys).
  2. Click **Create Key**, set credit limit to `$0.00`.
  3. Copy your key (`sk-or-v1-...`) and configure it:
     ```bash
     python main.py config --set api.openrouter_api_key "<your_openrouter_key>"
     ```

---

### Cloudflare Workers AI
* **Model**: `@cf/meta/llama-3.1-8b-instruct`.
* **Free Quota**: 10,000 free Neurons per day (~2,000 to 10,000 requests/day at $0 cost).
* **Setup**:
  1. Open [Cloudflare Dashboard](https://dash.cloudflare.com/).
  2. Copy your 32-character **Account ID** from the right sidebar.
  3. Go to **My Profile** > **API Tokens** > **Create Token**.
  4. Select **Workers AI** permissions (`Account > Workers AI > Edit`).
  5. Click **Create Token** and copy the generated token (`cfut_...`).
  6. Configure both values:
     ```bash
     python main.py config --set api.cloudflare_account_id "<account_id>"
     python main.py config --set api.cloudflare_api_token "<api_token>"
     ```

---

## 7. Keyword & Tag Management

The cleaning engine uses a 3-tier dictionary to strip release tags:
1. **Shipped Scene Tags (`data/tags.json`)**: Default scene tags, audio formats, codecs, and languages.
2. **User Custom Tags (`custom_tags.json`)**: Stored in your configuration folder alongside `config.ini` for private release groups or tracker names:
   ```json
   {
     "tags": ["private_tracker", "custom_group"]
   }
   ```
3. **AI Learned Tags (`gemini_tags.json`)**: When keyword learning is enabled (`-L` or `options.learn = true`), missing release tags discovered by AI are validated and appended to `gemini_tags.json`.

---

## 8. Email Alerts & System Setup

### Gmail SMTP Setup
1. Enable **2-Step Verification** on your [Google Account](https://myaccount.google.com/security).
2. Generate a 16-character **App Password** under Account Security > App Passwords.
3. Configure credentials:
   ```bash
   python main.py config --set mail.mail "your_email@gmail.com"
   python main.py config --set mail.mail_pswd "your_16_char_password"
   ```

### FFmpeg / ffprobe Setup
Required only if resolution (`options.resolution`) or quality (`options.quality`) detection is enabled:
* **Windows**: `winget install ffmpeg`
* **macOS**: `brew install ffmpeg`
* **Linux**: `sudo apt install ffmpeg`
