# 🎬 Media Organizer & Renamer

A smart Python utility that scans a download directory, parses messy video filenames, fetches official titles via the **TMDB API**, and cleanly categorizes them into organized Movie and TV Show directories (following Plex naming conventions). 

If standard parsing fails due to obfuscated or missing data in the filename, the script intelligently leverages the **Gemini API** to analyze and correct the filename automatically!

## Features

* **🧠 Smart Parsing:** Extracts essential information (title, season, episode, year) from messy video filenames.
* **🎥 TMDB Integration:** Automatically queries The Movie Database (TMDB) to retrieve official titles and release years.
* **📂 Automated Sorting:** Automatically moves and renames media into structured directories:
  * **Movies:** `Movies/Title (Year).mkv`
  * **TV Shows:** `TV_Shows/Show Name/Season XX/Title SXXEXX.mkv`
* **🧹 Auto-Cleanup:** Empty folders left in the download directory are automatically removed after a successful run.
* **🤖 AI Fallback:** (Optional) Uses Google's Gemini API to fix unidentifiable filenames when standard parsing fails.
* **📧 Email Notifications:** (Optional) Sends an alert email if a critical error occurs during execution.

## Folder Requirements

To use the "rename and move" features, the script relies on a specific folder structure. You must configure the paths to these folders in the `config.py` file before running the script (see the Setup section).

*Note: The script will deliberately exit if the specified folders do not exist or are not configured.*

Here is the recommended folder setup:
```text
📂 Media_Center/
 ├── 📂 .downloads/        (Your unsorted, messy video files go here)   
 ├── 📂 Movies/            (Movies will be renamed and moved here)
 └── 📂 TV_Shows/          (TV Shows will be renamed and moved here)
```
(Note: The "rename only" feature can be used in any folder by passing the targeted path as an argument. See Usage below.)


## 🚀 Setup
### 1. Clone the repository:

```Bash
git clone [https://github.com/ugoteulier/rename.git](https://github.com/ugoteuliere/rename.git)
cd rename
```

### 2. Install dependencies:

```Bash
pip install -r requirements.txt
```

### 3. Configure Environment:
Create a config.py file in the root directory of the script and populate it with your specific paths and API keys:

```Python
# config.py

# --- Folder Paths ---
MOVIES_FOLDER = "path/to/Movies"
TV_SHOWS_FOLDER = "path/to/TV_Shows"
NOT_SORTED_MEDIA_FILES_FOLDER = "path/to/.downloads"

# --- API Keys ---
TMDB_API_KEY = "your_tmdb_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"

# --- Email Alerts (Optional) ---
MAIL = "your_email@gmail.com"
MAIL_PSWD = "your_app_password_here"
```

## 💻 Usage
Run the script via the command line. You have a few operational modes:

### 1. Default (Rename & Move)

Scans the configured download folder, renames the files, and moves them to the respective Movie or TV Show folders.

```Bash
python main.py
```

### 2. Rename Only

Renames files in the configured download folder but does not move them.

```Bash
python main.py --rename
```
Tip: You can target a specific folder outside of your configuration by providing a path:

```Bash
python main.py --rename --path="path/to/custom/folder"
```

### 3. Move Only

Moves already cleanly named files from the download folder into the Movie/TV Show folders.

```Bash
python main.py --move
```

### ⚠️ Notes
- Supported Extensions: .mkv, .mp4, .avi, .mov, .wmv, .m4v
- Ensure you have read/write permissions for the directories configured in your config.py.

## 📚 Guides & Tutorials

### How to get a TMDB API Key
1. Go to [The Movie Database (TMDB)](https://www.themoviedb.org/) and create a free account.
2. Log in and click on your profile icon in the top right corner, then select **Settings**.
3. In the left-hand sidebar, click on **API**.
4. Under "Request an API Key", click **Create** or **click here**.
5. Select **Developer**.
6. Accept the terms and fill out the required application form.
7. Once approved (usually instantly), you will see your **API Key (v3 auth)**. Copy this into your `config.py`.

### How to get a Gemini API Key (and Free Tier Limitations)
1. Go to [Google AI Studio](https://aistudio.google.com/) and sign in with your Google account.
2. Click on **Get API key** in the left sidebar.
3. Click the **Create API key** button. Copy this key into your `config.py`.

**🚨 Important limitations of the Gemini Free Tier:**
* **Rate Limits:** You are limited to **5 Requests Per Minute (RPM)**, 250 million Tokens Per Minute (TPM), and 20 Requests Per Day. If you process a massive folder of files that all require AI correction simultaneously, the script might hit this rate limit.

### How to get a Gmail App Password (for email alerts)
Because standard passwords are no longer supported for third-party scripts, you must generate a specific "App Password" if you want the script to send you email alerts.
1. Go to your [Google Account Management](https://myaccount.google.com/) page.
2. Click on **Security** in the left sidebar.
3. Under "How you sign in to Google", ensure **2-Step Verification** is turned **ON** (this is mandatory).
4. Search for **App passwords** in the top search bar of your Google Account settings (Google occasionally moves this menu, so searching is the easiest way to find it).
5. Create a new app password. You can name the app "Python Media Script" or similar.
6. Google will generate a **16-letter password**. Copy this exact password (without spaces) and paste it into `MAIL_PSWD` in your `config.py`.