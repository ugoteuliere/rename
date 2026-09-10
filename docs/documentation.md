# 📖 Documentation

## 🗂️ Media Folders & Best Practices

The tool operates on three independent folders:
- **Downloads folder**: contains your incoming, unsorted video files.
- **Movies folder**: where renamed movie files are sorted.
- **TV Shows folder**: where renamed series and seasons are sorted.

These folders do not depend on a rigid directory structure and can each be located anywhere independently on your system (e.g. across different drives or network shares). 

As an organization best practice, you may optionally group them under a shared parent directory:

```text
Media_Center/              # (Optional shared parent)
├── .downloads/            # Incoming unsorted files
├── Movies/                # Movie files: Title (Year).ext
└── TV_Shows/              # TV series: Show Name/Season XX/Show Name - SXXEXX.ext
```

Within the Movies and TV Shows directories, items are automatically formatted following official Plex naming recommendations.

## 🛠️ Configuration Commands

You can configure and inspect your settings directly via the command line:

### Interactive Setup Wizard (Recommended)
```bash
python main.py configure
```
Guides you through setting your library directories, API keys, email notifications and preferences.

### Inspect Settings
```bash
# Display active settings (sensitive keys are masked)
python main.py config --list

# Display active settings with unmasked API keys and passwords
python main.py config --list --show-secrets

# View the active configuration file location
python main.py config --path

# Get the value of a specific setting
python main.py config --get paths.movies_folder
python main.py config --get api.tmdb_api_key
```

### Update or Remove Settings
```bash
# Update a folder path
python main.py config --set paths.movies_folder "D:/Media/Movies"
python main.py config --set paths.tv_shows_folder "D:/Media/TV_Shows"
python main.py config --set paths.not_sorted_media_files_folder "D:/Media/.downloads"

# Update an API key or email
python main.py config --set api.tmdb_api_key "your_tmdb_api_key"
python main.py config --set api.gemini_api_key "your_gemini_api_key"
python main.py config --set mail.mail "your_email@gmail.com"
python main.py config --set mail.mail_pswd "your_app_password"

# Configure default runtime options (y/n or true/false)
python main.py config --set options.bypass y
python main.py config --set options.learn true

# Remove a setting
python main.py config --unset api.gemini_api_key
```

## 🚀 Operational Modes

### 1. Default (Rename & Move)
Scans the download folder, renames messy files using official TMDB titles, and moves them into their respective `Movies/` and `TV_Shows/` directories.
```bash
python main.py
```

Override the incoming download folder to rename and move files from a specific folder:
```bash
python main.py --path="path/to/folder"
```

### 2. Rename Only
Renames the files in place without moving them to library directories:
```bash
python main.py --only-rename
# or
python main.py -r
```

Target a specific folder to rename in-place (works standalone without any library or download folders configured):
```bash
python main.py -r --path="path/to/folder"
```

### 3. Simulation Mode (Dry-Run Preview)
Simulates the entire workflow without making any changes to your files or sending emails. Displays exactly what renames and moves would happen:
```bash
python main.py --simulate
# or
python main.py -s
```
You can combine `--simulate` with any other flags (e.g. `python main.py -s -r` or `python main.py -s -i` or `python main.py -s --path="path/to/folder"`).

### 4. Autonomous Background Watcher
Runs continuously in the background, periodically polling the incoming downloads folder every X minutes:
```bash
# Start background watcher with configured polling interval (default: 15 min)
python main.py -a

# Start with a specific interval (e.g. 10 minutes)
python main.py -a --interval 10
```
Key behaviors of Autonomous Mode:
- **Automatic Cascading**: Automatically turns on `-b` (`bypass`) to avoid interactive prompts and `-l` (`log`) to write all output to daily log files (`log/YYYY-MM-DD.txt`).
- **Strict Folder Verification**: Confirms all 3 folders (`movies_folder`, `tv_shows_folder`, `not_sorted_media_files_folder`) are configured and reachable before starting.
- **In-Progress Download Protection**: Automatically skips files that are actively being downloaded (locked by other processes or with extensions such as `.crdownload`, `.part`, `.!ut`, `.tmp`).
- **Responsive Exit**: Pressing `Ctrl+C` cleanly terminates the watcher loop immediately.

## ⚙️ Options

Options can be enabled/disabled in the configuration file or enabled temporarily with command-line flags.

| Flag | Long Option | Config Key | Default | Description |
|---|---|---|---|---|
| `-a` | `--autonomous` | `options.autonomous` | `false` | Run continuously in autonomous mode with periodic background polling. Automatically enables `-b` and `-l`. |
| — | `--interval <min>` | `options.polling_interval` | `15` | Polling interval in minutes for autonomous mode (integer $\ge 1$). |
| `-s` | `--simulate` | — | `false` | Dry-run preview: prints planned renames and moves without modifying disk or sending emails. |
| `-r` | `--only-rename` | — | `false` | Renames files in-place without moving them to destination library directories. |
| `-R` | `--resolution` | `options.resolution` | `false` | Detects and appends video resolution tags (e.g. `[1080p]`, `[4K]`). Requires `ffprobe`. |
| `-q` | `--quality` | `options.quality` | `false` | Detects and appends video encoding/source quality tags (e.g. `[FullHD BluRay]`). Requires `ffprobe`. |
| `-b` | `--bypass` | `options.bypass` | `false` | Bypass user confirmation prompts and run non-interactively. |
| `-i` | `--ai` | `options.ai` | `false` | Enables Cloud AI fallback to identify heavily obfuscated filenames when standard parsing fails. |
| `-L` | `--learn` | `options.learn` | `false` | Enables AI keyword learning: saves missing tags discovered by AI into `gemini_tags.json`. Available across all operational modes. Automatically enables AI fallback. |
| — | `--provider <name>` | `options.ai_provider` | `auto` | Choose AI Cloud provider (`auto`, `gemini`, `groq`, `openrouter`, `cloudflare`). |
| — | — | `options.tmdb_min_confidence` | `0.75` | Confidence threshold ($0.0 - 1.0$) for local TMDB matches before triggering AI fallback. |
| — | — | `options.ai_min_confidence` | `0.70` | Minimum confidence score ($0.0 - 1.0$) required from AI models to accept renamed title. |
| `-l` | `--log` | `options.log` | `false` | Suppresses terminal output and writes logs to a dedicated daily log file. |
| `-v` | `--verbose` | `options.verbose` | `false` | Displays detailed error tracebacks in terminal output. |
| — | `--notify-success` | `options.notify_on_success` | `false` | Sends an email notification each time a media file is successfully processed. |
| — | `--notify-error` | `options.notify_on_error` | `true` | Sends an email notification when a processing error occurs. |
| `-t` | `--notify-tag` | `options.notify_on_tag` | `false` | Sends an email notification when a new AI keyword tag is discovered and saved to `gemini_tags.json`. |
| — | `--path="<path>"` | — | Incoming folder | Override incoming download folder for rename & move; or rename in-place with -r (works standalone). |

### Examples

```bash
# Simulation run: see what would happen before touching anything
python main.py -s

# Simulation run with AI keyword learning (learns new tags while keeping media untouched on disk)
python main.py -s -L

# Non-interactive run with AI fallback and keyword learning enabled
python main.py --bypass --ai --learn

# Run with a specific AI Cloud Provider (e.g. Groq)
python main.py --ai --provider groq

# Autonomous watcher with AI keyword learning
python main.py -a -L

# Enable AI keyword learning and receive email notifications when new tags are learned
python main.py -L -t

# Rename files in a custom folder without moving
python main.py -r --path="D:/Torrents/Complete"

# Non-interactive server run with logging to file
python main.py --bypass --log
```

## 🧠 Multi-Cloud AI Architecture & Smart Fallback

The media parser features an intelligent multi-cloud AI fallback system designed for speed, resilience, and zero maintenance:

- **100% Optional & Independent**: The tool is fully functional without any AI API key or AI fallback activated. If you only want standard regex/PTN parsing and TMDB queries, no AI setup is required. Keyword learning (`-L`) and AI fallback (`-i`) are completely separate and optional.
- **TMDB Match Probability Scorer**: After local parsing, the system computes a match probability $P \in [0.0, 1.0]$ between the parsed filename and TMDB search results (combining sequence similarity, token overlap, containment, and release year proximity). If the score is below threshold (default `< 0.75`) and AI fallback is enabled, the item is queued for AI verification.
- **Batch Processing**: Instead of calling external AI APIs file-by-file, items needing AI fallback are bundled into batches (up to 25 files per request), slashing latency and token usage.
- **Single-Provider Execution with Quota Failover**: For each batch, exactly one active provider is called. If that provider returns a quota exhaustion or rate-limit error (HTTP 429 / ResourceExhausted), the batch automatically fails over to the next configured provider in your chain.
- **Structured Pydantic Outputs**: Responses are validated via Pydantic models with title sanitization (defending against path traversal) and confidence score validation.

---

## 🔑 Setup Guides & Free API Key Tutorials

### 1. TMDB API Key (Core Metadata)
The Movie Database (TMDB) API key is required to query official movie and series metadata:
1. Create a free account at [The Movie Database (TMDB)](https://www.themoviedb.org/).
2. Go to **Settings** > **API**.
3. Under "Request an API Key", select **Developer**.
4. Fill in the application details and accept the terms of service.
5. Copy your **API Key (v3 auth)** (or API Read Access Token) and configure it:
   ```bash
   python main.py config --set api.tmdb_api_key "your_tmdb_key_here"
   # Or environment variable:
   export RENAME_TMDB_API_KEY="your_tmdb_key_here"
   ```

---

### 2. Google Gemini API (AI Cloud Provider)
Powered by `gemini-2.5-flash-lite`, Google Gemini provides fast, state-of-the-art title extraction and missing tag detection:
- **Free Tier**: 15 requests per minute, 1,500 requests per day (free of charge).
- **Tutorial**:
  1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey).
  2. Sign in with your Google account.
  3. Click **Get API key** > **Create API key**.
  4. Select or create a Google Cloud project and copy your API key.
  5. Configure it in the tool:
     ```bash
     python main.py config --set api.gemini_api_key "AIzaSy..."
     # Or environment variable:
     export RENAME_GEMINI_API_KEY="AIzaSy..."
     ```

---

### 3. Groq Cloud API (AI Cloud Provider)
Powered by ultra-fast LPU inference running `llama-3.3-70b-versatile`:
- **Free Tier**: Generous free rate limits with high throughput.
- **Tutorial**:
  1. Visit [Groq Cloud Console](https://console.groq.com/).
  2. Sign in with Google, GitHub, or your email.
  3. In the left navigation menu, click **API Keys** (or go to https://console.groq.com/keys).
  4. Click **Create API Key**, enter a name (e.g. `rename-tool`), and copy the key (starts with `gsk_...`).
  5. Configure it in the tool:
     ```bash
     python main.py config --set api.groq_api_key "gsk_..."
     # Or environment variable:
     export RENAME_GROQ_API_KEY="gsk_..."
     ```

---

### 4. OpenRouter API (AI Cloud Provider)
Aggregates free and commercial open-source models (uses `meta-llama/llama-3.3-70b-instruct:free`):
- **Free Tier**: Access free models with zero upfront balance.
- **Tutorial**:
  1. Visit [OpenRouter](https://openrouter.ai/).
  2. Sign in with Google, GitHub, or email.
  3. Go to **Settings** > **Keys** (or https://openrouter.ai/settings/keys).
  4. Click **Create Key**, give it a name (e.g. `rename-app`), and copy the generated key (starts with `sk-or-v1-...`).
  5. Configure it in the tool:
     ```bash
     python main.py config --set api.openrouter_api_key "sk-or-v1-..."
     # Or environment variable:
     export RENAME_OPENROUTER_API_KEY="sk-or-v1-..."
     ```

---

### 5. Cloudflare Workers AI (AI Cloud Provider)
Runs Meta Llama 3.1 8B (`@cf/meta/llama-3.1-8b-instruct`) on Cloudflare's serverless edge:
- **Free Tier**: 10,000 free Neurons per day (sufficient for thousands of media titles per day).
- **Tutorial**:
  1. Sign in or create a free account at [Cloudflare Dashboard](https://dash.cloudflare.com/).
  2. **Get your Account ID**: On the dashboard homepage, look at the right sidebar (under "Account ID") or in the URL `dash.cloudflare.com/<ACCOUNT_ID>`. Copy your 32-character Account ID.
  3. **Generate an API Token**:
     - Go to **My Profile** (top-right avatar) > **API Tokens** (or https://dash.cloudflare.com/profile/api-tokens).
     - Click **Create Token**.
     - Choose the **Workers AI (Read & Write)** template (or create a custom token with `Account > Workers AI > Edit` permissions).
     - Click **Continue to summary** and then **Create Token**.
     - Copy your API Token.
  4. Configure both values in the tool:
     ```bash
     python main.py config --set api.cloudflare_account_id "<account_id>"
     python main.py config --set api.cloudflare_api_token "<api_token>"
     # Or environment variables:
     export RENAME_CLOUDFLARE_ACCOUNT_ID="<account_id>"
     export RENAME_CLOUDFLARE_API_TOKEN="<api_token>"
     ```

---

### 6. Gmail App Password & Email Notifications
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is enabled.
3. In the search bar at the top, type **App passwords**.
4. Generate a new app password (e.g. name it "Media Renamer").
5. Copy the 16-character password and configure email:
   ```bash
   python main.py config --set mail.mail "your_email@gmail.com"
   python main.py config --set mail.mail_pswd "your_16_char_password"

   # Enable/disable specific notifications (ideal for automated server runs)
   python main.py config --set options.notify_on_success y   # Email each time a media is processed
   python main.py config --set options.notify_on_error y     # Email when an error occurs
   python main.py config --set options.notify_on_tag y       # Email when new AI keywords are learned
   ```
*(Note: You can also configure these settings interactively via `python main.py configure`).*

### FFmpeg Setup
FFmpeg (specifically `ffprobe`) is **only** required if you activate video resolution and quality detection in filenames (`options.resolution` or `options.quality`). It is not needed for standard movie and TV show renaming.

- **Windows (PowerShell Admin)**:
  ```powershell
  winget install ffmpeg
  ```
- **macOS (Homebrew)**:
  ```bash
  brew install ffmpeg
  ```
- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt install ffmpeg
  ```

*(Note: Restart your terminal or IDE after installation so that `ffprobe` is available in your System PATH).*

---

## 🏷️ Custom & Learned Keywords (Tag Management)

The application uses an isolated 3-tier system to strip release tags (codecs, resolutions, release groups) from filenames before querying metadata APIs:

1. **Core Defaults (`data/tags.json`)**: Shipped with the repository and maintained in source control. Contains standard scene tags, audio formats, and languages.
2. **User Custom Tags (`custom_tags.json`)**: Located in your configuration directory (alongside `config.ini`). You can add custom tracker tags or private release groups here without modifying repository files:
   ```json
   {
     "tags": ["my_private_tracker", "custom_group"]
   }
   ```
3. **Gemini Learned Tags (`gemini_tags.json`)**: When AI learning is enabled (`options.learn = true` in config or `-L / --learn` flag) and Gemini analyzes an obfuscated file, any discovered missing release tags are validated against strict guardrails (minimum length $\ge 3$, stopword blacklist, alphanumeric format) and saved to `gemini_tags.json` in your configuration folder. You can also receive dedicated email alerts whenever new keywords are learned using `-t` (`--notify-tag`) or `options.notify_on_tag = true`, showing the newly learned tags and the file in which they were found.

#### AI Keyword Learning Across Operational Modes
- **Default (Rename & Move)**: New tags are learned and saved while files are organized.
- **Rename-Only (`-r`)**: New tags are learned and saved while files are renamed in-place.
- **Simulation Mode (`-s`)**: New tags are learned and saved into `gemini_tags.json`, but all video files and directories on disk remain completely unmodified.
- **Autonomous Mode (`-a`)**: New tags are continuously learned across background polling cycles whenever cryptic filenames are encountered.
- **Toggle / Persistent Setting**:
  - Interactively configure via `python main.py configure`.
  - Set permanently via CLI: `python main.py config --set options.learn true` or environment variable `RENAME_LEARN=true`.
  - Enable for a single execution using `-L` or `--learn`.

