# 📖 CLI Reference & Documentation

A complete reference guide for using and configuring the **Media Organizer & Renamer** from the terminal.

---

## 🗂️ Folder Structure

The tool organizes your media library following Plex standards:

```text
Media_Center/
├── .downloads/        (Your unsorted video files)
├── Movies/            (Organized as: Title (Year).ext)
└── TV_Shows/          (Organized as: Show Name/Season XX/Show Name - SXXEXX.ext)
```

---

## 🛠️ Configuration Commands

You can configure and inspect your settings directly via the command line:

### Interactive Setup Wizard (Recommended)
```bash
python main.py configure
```
Guides you through setting your library directories, API keys, email notifications, and metadata preferences with automatic path validation.

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
python main.py config --set email.mail "your_email@gmail.com"
python main.py config --set email.mail_pswd "your_app_password"

# Toggle resolution/quality tags
python main.py config --set options.resolution true
python main.py config --set options.quality true

# Remove a setting
python main.py config --unset api.gemini_api_key
```

---

## 🚀 Operational Modes

### 1. Default (Rename & Move)
Scans the download folder, renames messy files using official TMDB titles, and moves them into their respective `Movies/` and `TV_Shows/` directories.
```bash
python main.py
```

### 2. Rename Only
Renames the files in place without moving them to library directories:
```bash
python main.py --only_rename
# or short form:
python main.py -r
```

Target a specific custom directory instead of the default download folder:
```bash
python main.py -r --path="path/to/folder"
```

### 3. Move Only
Moves already cleanly named media files from the download folder into your movie and series library:
```bash
python main.py --only_move
# or short form:
python main.py -m
```

---

## ⚙️ Options & Flags

Combine these flags with any operational mode:

| Flag | Long Option | Description |
|---|---|---|
| `-a` | `--auto` | Runs non-interactively without prompting for confirmation. |
| `-i` | `--ai` | Enables Gemini AI fallback to identify heavily obfuscated filenames when standard parsing fails. |
| `-e` | `--mail` | Sends an email alert if a critical error occurs during execution. |
| `-l` | `--log` | Suppresses terminal output and writes logs to a dedicated log file. |
| `-v` | `--verbose` | Displays detailed error tracebacks in terminal output. |
| `--path` | `--path="<path>"` | Targets a specific folder when using `--only_rename` (`-r`). |

### Examples

```bash
# Automatic run with AI fallback enabled
python main.py --auto --ai

# Rename files in a custom folder without moving
python main.py -r --path="D:/Torrents/Complete"

# Automatic run with logging to file and error emails
python main.py --auto --log --mail
```

---

## 🔑 External Services Setup

### TMDB API Key
1. Create a free account at [The Movie Database (TMDB)](https://www.themoviedb.org/).
2. Go to **Settings** > **API**.
3. Under "Request an API Key", select **Developer**.
4. Accept the terms and submit the application.
5. Copy the generated **API Key (v3 auth)** and set it via:
   ```bash
   python main.py config --set api.tmdb_api_key "your_key_here"
   ```

### Gemini API Key (AI Fallback)
1. Sign in to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API key** in the left navigation.
3. Click **Create API key**.
4. Copy the key and set it via:
   ```bash
   python main.py config --set api.gemini_api_key "your_key_here"
   ```
*(Note: Gemini Free Tier provides 5 requests per minute, which is sufficient for unidentifiable media).*

### Gmail App Password (Error Alerts)
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is enabled.
3. In the search bar at the top, type **App passwords**.
4. Generate a new app password (e.g. name it "Media Renamer").
5. Copy the 16-character password and configure email:
   ```bash
   python main.py config --set email.mail "your_email@gmail.com"
   python main.py config --set email.mail_pswd "your_16_char_password"
   ```
