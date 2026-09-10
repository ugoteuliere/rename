import os
import sys
import shutil
import tempfile
import configparser
from pathlib import Path

class ConfigManager:
    SCHEMA = {
        "paths": ["movies_folder", "tv_shows_folder", "not_sorted_media_files_folder"],
        "api": ["tmdb_api_key", "gemini_api_key"],
        "mail": ["mail", "mail_pswd"],
        "options": [
            "bypass", "ai", "log", "verbose", "resolution", "quality",
            "notify_on_success", "notify_on_error", "autonomous", "polling_interval", "learn"
        ]
    }

    ENV_MAPPING = {
        "paths.movies_folder": ["RENAME_MOVIES_FOLDER"],
        "paths.tv_shows_folder": ["RENAME_TV_SHOWS_FOLDER"],
        "paths.not_sorted_media_files_folder": ["RENAME_NOT_SORTED_MEDIA_FILES_FOLDER", "RENAME_DOWNLOADS_FOLDER"],
        "api.tmdb_api_key": ["RENAME_TMDB_API_KEY", "TMDB_API_KEY"],
        "api.gemini_api_key": ["RENAME_GEMINI_API_KEY", "GEMINI_API_KEY"],
        "mail.mail": ["RENAME_MAIL"],
        "mail.mail_pswd": ["RENAME_MAIL_PSWD"],
        "options.bypass": ["RENAME_BYPASS"],
        "options.ai": ["RENAME_AI"],
        "options.learn": ["RENAME_LEARN"],
        "options.log": ["RENAME_LOG"],
        "options.verbose": ["RENAME_VERBOSE"],
        "options.resolution": ["RENAME_RESOLUTION"],
        "options.quality": ["RENAME_QUALITY"],
        "options.notify_on_success": ["RENAME_NOTIFY_ON_SUCCESS"],
        "options.notify_on_error": ["RENAME_NOTIFY_ON_ERROR"],
        "options.autonomous": ["RENAME_AUTONOMOUS"],
        "options.polling_interval": ["RENAME_POLLING_INTERVAL"],
    }

    KEY_TO_ATTR = {
        "paths.movies_folder": "MOVIES_FOLDER",
        "paths.tv_shows_folder": "TV_SHOWS_FOLDER",
        "paths.not_sorted_media_files_folder": "NOT_SORTED_MEDIA_FILES_FOLDER",
        "api.tmdb_api_key": "TMDB_API_KEY",
        "api.gemini_api_key": "GEMINI_API_KEY",
        "mail.mail": "MAIL",
        "mail.mail_pswd": "MAIL_PSWD",
        "options.bypass": "BYPASS",
        "options.ai": "AI",
        "options.learn": "LEARN",
        "options.log": "LOG",
        "options.verbose": "VERBOSE",
        "options.resolution": "RESOLUTION",
        "options.quality": "QUALITY",
        "options.notify_on_success": "NOTIFY_ON_SUCCESS",
        "options.notify_on_error": "NOTIFY_ON_ERROR",
        "options.autonomous": "AUTONOMOUS",
        "options.polling_interval": "POLLING_INTERVAL",
    }

    ATTR_TO_KEY = {v: k for k, v in KEY_TO_ATTR.items()}

    BOOLEAN_KEYS = {
        "options.bypass",
        "options.ai",
        "options.learn",
        "options.log",
        "options.verbose",
        "options.resolution",
        "options.quality",
        "options.notify_on_success",
        "options.notify_on_error",
        "options.autonomous"
    }

    SECRET_KEYS = {"api.tmdb_api_key", "api.gemini_api_key", "mail.mail_pswd"}

    def __init__(self, custom_path=None):
        self.custom_path = custom_path
        self.config_path = self._resolve_config_path(custom_path)
        self.parser = configparser.ConfigParser()
        self.load()

    def _resolve_config_path(self, custom_path=None) -> Path:
        if custom_path:
            return Path(custom_path).resolve()

        env_config = os.environ.get("RENAME_CONFIG_FILE")
        if env_config:
            return Path(env_config).resolve()

        # Check local project override in current working directory
        local_ini = Path(".rename.ini").resolve()
        if local_ini.is_file():
            return local_ini

        local_config_ini = Path("config.ini").resolve()
        if local_config_ini.is_file():
            return local_config_ini

        # Quarantine safeguard: Never touch real user configuration during automated pytest runs
        if "PYTEST_CURRENT_TEST" in os.environ:
            base_dir = Path(tempfile.gettempdir()) / "pytest_rename_quarantine"
            return (base_dir / "config.ini").resolve()

        # Standard user config directory
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA')
            if appdata:
                base_dir = Path(appdata) / "rename"
            else:
                base_dir = Path.home() / ".config" / "rename"
        else:
            xdg = os.environ.get('XDG_CONFIG_HOME')
            if xdg:
                base_dir = Path(xdg) / "rename"
            else:
                base_dir = Path.home() / ".config" / "rename"

        return (base_dir / "config.ini").resolve()

    def load(self):
        self.parser = configparser.ConfigParser()
        if self.config_path.is_file():
            self.parser.read(str(self.config_path), encoding="utf-8")

    def save(self):
        """Atomic write using temporary file to prevent corruption."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        dir_to_use = self.config_path.parent
        
        with tempfile.NamedTemporaryFile("w", dir=dir_to_use, delete=False, encoding="utf-8") as tf:
            self.parser.write(tf)
            temp_path = tf.name

        shutil.move(temp_path, str(self.config_path))

    def get_with_source(self, section_dot_key: str):
        """Returns tuple of (value, source) where source is 'ENV', 'INI', or 'DEFAULT'."""
        # 1. Check environment variables
        env_vars = self.ENV_MAPPING.get(section_dot_key, [])
        for var in env_vars:
            if var in os.environ:
                val = os.environ[var]
                if section_dot_key in self.BOOLEAN_KEYS:
                    return (val.strip().lower() in ("true", "1", "yes", "y", "t"), "ENV")
                return (val, "ENV")

        # 2. Check INI file
        if "." in section_dot_key:
            section, key = section_dot_key.split(".", 1)
            if self.parser.has_section(section) and self.parser.has_option(section, key):
                raw = self.parser.get(section, key)
                if section_dot_key in self.BOOLEAN_KEYS:
                    return (raw.strip().lower() in ("true", "1", "yes", "y", "t"), "INI")
                return (raw if raw.strip() else None, "INI")

        # 3. Default fallback
        if section_dot_key == "options.notify_on_error":
            return (True, "DEFAULT")
        if section_dot_key == "options.polling_interval":
            return (15, "DEFAULT")
        if section_dot_key in self.BOOLEAN_KEYS:
            return (False, "DEFAULT")
        return (None, "DEFAULT")

    def get(self, section_dot_key: str, default=None):
        val, _ = self.get_with_source(section_dot_key)
        return val if val is not None else default

    def set(self, section_dot_key: str, value: str):
        if "." not in section_dot_key:
            raise ValueError(f"Key must be in format 'section.key', got '{section_dot_key}'")

        section, key = section_dot_key.split(".", 1)
        section = section.strip().lower()
        key = key.strip().lower()

        if section not in self.SCHEMA:
            raise ValueError(f"Unknown section '{section}'. Valid sections: {', '.join(self.SCHEMA.keys())}")
        if key not in self.SCHEMA[section]:
            raise ValueError(f"Unknown key '{key}' in section '{section}'. Valid keys: {', '.join(self.SCHEMA[section])}")

        if not self.parser.has_section(section):
            self.parser.add_section(section)

        # Validate specific option types
        if section_dot_key == "options.polling_interval":
            try:
                int_val = int(str(value).strip())
                if int_val < 1:
                    raise ValueError()
                self.parser.set(section, key, str(int_val))
            except ValueError:
                raise ValueError("Polling interval must be a positive integer (>= 1 minute).")
        # Normalize boolean values
        elif f"{section}.{key}" in self.BOOLEAN_KEYS:
            val_bool = str(value).strip().lower() in ("true", "1", "yes", "y", "t")
            self.parser.set(section, key, "true" if val_bool else "false")
        else:
            self.parser.set(section, key, str(value).strip())

        self.save()

    def unset(self, section_dot_key: str) -> bool:
        if "." not in section_dot_key:
            raise ValueError(f"Key must be in format 'section.key', got '{section_dot_key}'")

        section, key = section_dot_key.split(".", 1)
        section = section.strip().lower()
        key = key.strip().lower()

        if self.parser.has_section(section) and self.parser.remove_option(section, key):
            self.save()
            return True
        return False

    def list_all(self, show_secrets: bool = False):
        """Returns structured list of all settings across all schema sections."""
        items = []
        for section, keys in self.SCHEMA.items():
            for key in keys:
                full_key = f"{section}.{key}"
                val, source = self.get_with_source(full_key)
                is_secret = full_key in self.SECRET_KEYS

                display_val = val
                if is_secret and val and not show_secrets:
                    val_str = str(val)
                    if len(val_str) > 8:
                        display_val = f"{val_str[:4]}****{val_str[-4:]}"
                    else:
                        display_val = "****"

                items.append({
                    "section": section,
                    "key": key,
                    "full_key": full_key,
                    "value": val,
                    "display_value": display_val if display_val is not None else "(not configured)",
                    "source": source,
                    "is_secret": is_secret
                })
        return items

    def run_wizard(self):
        """Interactive terminal configuration wizard."""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm

        console = Console()
        console.print("\n[bold cyan]==============================================[/bold cyan]")
        console.print("[bold cyan]   🎬 Media Organizer & Renamer Setup Wizard   [/bold cyan]")
        console.print("[bold cyan]==============================================[/bold cyan]\n")
        console.print(f"Target Configuration File: [yellow]{self.config_path}[/yellow]\n")
        console.print("Press [green]Enter[/green] to keep current value.\n")

        # --- 1. Folder Paths ---
        console.print("[bold magenta]📂 Folder Paths Configuration[/bold magenta]")
        console.print("[dim]Best Practice: Keep incoming downloads in an unsorted folder, separate from your Movies and TV Shows libraries. Folders can be local drives, USB disks, or NAS network shares.[/dim]")
        
        def _prompt_and_validate_folder(label, key):
            current = self.get(key) or ""
            folder_input = Prompt.ask(label, default=current)
            folder_clean = folder_input.strip()
            if folder_clean:
                if not os.path.isdir(folder_clean):
                    console.print(f"[bold red]❌ Error: The directory '{folder_clean}' does not exist on disk or is not reachable.[/bold red]")
                self.set(key, folder_clean)

        _prompt_and_validate_folder("Movies Folder", "paths.movies_folder")
        _prompt_and_validate_folder("TV Shows Folder", "paths.tv_shows_folder")
        _prompt_and_validate_folder("Unsorted Downloads Folder", "paths.not_sorted_media_files_folder")

        # --- 2. API Keys ---
        console.print("\n[bold magenta]🔑 API Keys Configuration[/bold magenta]")
        console.print("[dim]Best Practice: TMDB API key is required to query official movie/series metadata. Gemini AI key is an optional fallback for highly cryptic filenames.[/dim]")
        
        current_tmdb = self.get("api.tmdb_api_key") or ""
        tmdb_masked = f"{current_tmdb[:4]}...{current_tmdb[-4:]}" if len(current_tmdb) > 8 else current_tmdb
        tmdb_input = Prompt.ask("TMDB API Key (Bearer/v3 token)", default=tmdb_masked)
        if tmdb_input.strip() and tmdb_input != tmdb_masked:
            self.set("api.tmdb_api_key", tmdb_input)

        current_gemini = self.get("api.gemini_api_key") or ""
        gemini_masked = f"{current_gemini[:4]}...{current_gemini[-4:]}" if len(current_gemini) > 8 else current_gemini
        gemini_input = Prompt.ask("Google Gemini API Key (Optional AI Fallback)", default=gemini_masked)
        if gemini_input.strip() and gemini_input != gemini_masked:
            self.set("api.gemini_api_key", gemini_input)

        # --- 3. Email Alerts (Optional) ---
        console.print("\n[bold magenta]📧 Email Alerts Configuration (Optional)[/bold magenta]")
        console.print("[dim]Best Practice: Useful for headless/server cron jobs. Requires a 16-letter Gmail App Password created via Google Account Security.[/dim]")
        current_mail = self.get("mail.mail") or ""
        mail_input = Prompt.ask("Gmail Address", default=current_mail)
        if mail_input.strip():
            self.set("mail.mail", mail_input)

        current_pswd = self.get("mail.mail_pswd") or ""
        pswd_masked = "****" if current_pswd else ""
        pswd_input = Prompt.ask("Gmail App Password (16-letter password)", default=pswd_masked)
        if pswd_input.strip() and pswd_input != pswd_masked:
            self.set("mail.mail_pswd", pswd_input)

        # --- 4. Automation & Runtime Options ---
        console.print("\n[bold magenta]⚙️ Automation & Runtime Options[/bold magenta]")
        console.print("[dim]Best Practice: Set default execution behaviors so you do not need to specify flags on every run. CLI flags (-b, -i, -L, -l, -v) will always override these defaults.[/dim]")
        cur_bypass = bool(self.get("options.bypass", False))
        bypass_input = Confirm.ask("Bypass confirmation prompts and run non-interactively (-b)?", default=cur_bypass)
        self.set("options.bypass", "true" if bypass_input else "false")

        cur_autonomous = bool(self.get("options.autonomous", False))
        auto_input = Confirm.ask("Enable autonomous background watcher mode by default (-a)?", default=cur_autonomous)
        self.set("options.autonomous", "true" if auto_input else "false")

        cur_interval = str(self.get("options.polling_interval") or "15")
        interval_input = Prompt.ask("Polling interval in minutes for autonomous mode", default=cur_interval)
        try:
            int_val = int(interval_input.strip())
            if int_val >= 1:
                self.set("options.polling_interval", str(int_val))
            else:
                self.set("options.polling_interval", "15")
        except ValueError:
            self.set("options.polling_interval", "15")

        cur_ai = bool(self.get("options.ai", False))
        ai_input = Confirm.ask("Enable Gemini AI fallback by default for unrecognized filenames (-i)?", default=cur_ai)
        self.set("options.ai", "true" if ai_input else "false")

        cur_learn = bool(self.get("options.learn", False))
        learn_input = Confirm.ask("Enable AI keyword learning by default (save missing tags discovered by Gemini) (-L)?", default=cur_learn)
        self.set("options.learn", "true" if learn_input else "false")

        cur_log = bool(self.get("options.log", False))
        log_input = Confirm.ask("Write execution logs to daily log files instead of terminal (-l)?", default=cur_log)
        self.set("options.log", "true" if log_input else "false")

        cur_verbose = bool(self.get("options.verbose", False))
        verbose_input = Confirm.ask("Display detailed error logs and exception tracebacks (-v)?", default=cur_verbose)
        self.set("options.verbose", "true" if verbose_input else "false")

        cur_succ = bool(self.get("options.notify_on_success", False))
        notify_succ_input = Confirm.ask("Send an email notification on successful processing?", default=cur_succ)
        self.set("options.notify_on_success", "true" if notify_succ_input else "false")

        cur_err = bool(self.get("options.notify_on_error", True))
        notify_err_input = Confirm.ask("Send an email notification when an error occurs?", default=cur_err)
        self.set("options.notify_on_error", "true" if notify_err_input else "false")

        # --- 5. Technical Video Tags ---
        console.print("\n[bold magenta]🎞️ Video Stream Options (Requires FFmpeg)[/bold magenta]")
        console.print("[dim]Best Practice: Extracts video stream metadata to append clean tags (e.g. [4K] [1080p] [BluRay]). Requires 'ffprobe' installed in System PATH.[/dim]")
        cur_res = bool(self.get("options.resolution", False))
        res_input = Confirm.ask("Detect and append resolution tags (e.g., [4K], [FullHD])?", default=cur_res)
        self.set("options.resolution", "true" if res_input else "false")

        cur_qual = bool(self.get("options.quality", False))
        qual_input = Confirm.ask("Detect and append quality tags (e.g., [BluRay], [WEB-DL])?", default=cur_qual)
        self.set("options.quality", "true" if qual_input else "false")

        if (res_input or qual_input) and not shutil.which("ffprobe"):
            console.print("\n[bold red]❌ Error: 'ffprobe' (FFmpeg) was not found in your System PATH.[/bold red]")
            console.print("[yellow]Resolution and quality tags will fail to be detected until FFmpeg is installed.[/yellow]")
            console.print("[dim]Installation guide: docs/documentation.md#ffmpeg-setup[/dim]")

        console.print(f"\n[bold green]✅ Configuration successfully saved to:[/bold green] [yellow]{self.config_path}[/yellow]\n")

    # Module-level property accessors
    @property
    def MOVIES_FOLDER(self):
        return self.get("paths.movies_folder")

    @property
    def TV_SHOWS_FOLDER(self):
        return self.get("paths.tv_shows_folder")

    @property
    def NOT_SORTED_MEDIA_FILES_FOLDER(self):
        return self.get("paths.not_sorted_media_files_folder")

    @property
    def TMDB_API_KEY(self):
        return self.get("api.tmdb_api_key")

    @property
    def GEMINI_API_KEY(self):
        return self.get("api.gemini_api_key")

    @property
    def MAIL(self):
        return self.get("mail.mail")

    @MAIL.setter
    def MAIL(self, value):
        if value is None:
            self.unset("mail.mail")
        else:
            self.set("mail.mail", str(value))

    @property
    def MAIL_PSWD(self):
        return self.get("mail.mail_pswd")

    @MAIL_PSWD.setter
    def MAIL_PSWD(self, value):
        if value is None:
            self.unset("mail.mail_pswd")
        else:
            self.set("mail.mail_pswd", str(value))

    @property
    def NOTIFY_ON_SUCCESS(self) -> bool:
        return bool(self.get("options.notify_on_success", False))

    @NOTIFY_ON_SUCCESS.setter
    def NOTIFY_ON_SUCCESS(self, value):
        self.set("options.notify_on_success", "true" if value else "false")

    @property
    def NOTIFY_ON_ERROR(self) -> bool:
        return bool(self.get("options.notify_on_error", True))

    @NOTIFY_ON_ERROR.setter
    def NOTIFY_ON_ERROR(self, value):
        self.set("options.notify_on_error", "true" if value else "false")

    @property
    def BYPASS(self) -> bool:
        return bool(self.get("options.bypass", False))

    @BYPASS.setter
    def BYPASS(self, value):
        self.set("options.bypass", "true" if value else "false")

    @property
    def AI(self) -> bool:
        return bool(self.get("options.ai", False))

    @AI.setter
    def AI(self, value):
        self.set("options.ai", "true" if value else "false")

    @property
    def LEARN(self) -> bool:
        return bool(self.get("options.learn", False))

    @LEARN.setter
    def LEARN(self, value):
        self.set("options.learn", "true" if value else "false")

    @property
    def LOG(self) -> bool:
        return bool(self.get("options.log", False))

    @LOG.setter
    def LOG(self, value):
        self.set("options.log", "true" if value else "false")

    @property
    def VERBOSE(self) -> bool:
        return bool(self.get("options.verbose", False))

    @VERBOSE.setter
    def VERBOSE(self, value):
        self.set("options.verbose", "true" if value else "false")

    @property
    def RESOLUTION(self):
        return bool(self.get("options.resolution", False))

    @property
    def QUALITY(self):
        return bool(self.get("options.quality", False))

    @property
    def AUTONOMOUS(self) -> bool:
        return bool(self.get("options.autonomous", False))

    @AUTONOMOUS.setter
    def AUTONOMOUS(self, value):
        self.set("options.autonomous", "true" if value else "false")

    @property
    def POLLING_INTERVAL(self) -> int:
        val = self.get("options.polling_interval", 15)
        try:
            val_int = int(val)
            return val_int if val_int >= 1 else 15
        except (ValueError, TypeError):
            return 15

    @POLLING_INTERVAL.setter
    def POLLING_INTERVAL(self, value):
        self.set("options.polling_interval", str(value))


# Singleton instance
config = ConfigManager()
