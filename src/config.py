import os
import sys
import tempfile
import configparser
from pathlib import Path

class ConfigManager:
    SCHEMA = {
        "paths": ["movies_folder", "tv_shows_folder", "not_sorted_media_files_folder"],
        "api": ["tmdb_api_key", "gemini_api_key"],
        "mail": ["mail", "mail_pswd"],
        "options": ["resolution", "quality"]
    }

    ENV_MAPPING = {
        "paths.movies_folder": ["RENAME_MOVIES_FOLDER"],
        "paths.tv_shows_folder": ["RENAME_TV_SHOWS_FOLDER"],
        "paths.not_sorted_media_files_folder": ["RENAME_NOT_SORTED_MEDIA_FILES_FOLDER", "RENAME_DOWNLOADS_FOLDER"],
        "api.tmdb_api_key": ["RENAME_TMDB_API_KEY", "TMDB_API_KEY"],
        "api.gemini_api_key": ["RENAME_GEMINI_API_KEY", "GEMINI_API_KEY"],
        "mail.mail": ["RENAME_MAIL"],
        "mail.mail_pswd": ["RENAME_MAIL_PSWD"],
        "options.resolution": ["RENAME_RESOLUTION"],
        "options.quality": ["RENAME_QUALITY"],
    }

    KEY_TO_ATTR = {
        "paths.movies_folder": "MOVIES_FOLDER",
        "paths.tv_shows_folder": "TV_SHOWS_FOLDER",
        "paths.not_sorted_media_files_folder": "NOT_SORTED_MEDIA_FILES_FOLDER",
        "api.tmdb_api_key": "TMDB_API_KEY",
        "api.gemini_api_key": "GEMINI_API_KEY",
        "mail.mail": "MAIL",
        "mail.mail_pswd": "MAIL_PSWD",
        "options.resolution": "RESOLUTION",
        "options.quality": "QUALITY",
    }

    ATTR_TO_KEY = {v: k for k, v in KEY_TO_ATTR.items()}

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

        os.replace(temp_path, str(self.config_path))

    def get_with_source(self, section_dot_key: str):
        """Returns tuple of (value, source) where source is 'ENV', 'INI', or 'DEFAULT'."""
        # 1. Check environment variables
        env_vars = self.ENV_MAPPING.get(section_dot_key, [])
        for var in env_vars:
            if var in os.environ:
                val = os.environ[var]
                if section_dot_key in ("options.resolution", "options.quality"):
                    return (val.strip().lower() in ("true", "1", "yes", "y", "t"), "ENV")
                return (val, "ENV")

        # 2. Check INI file
        if "." in section_dot_key:
            section, key = section_dot_key.split(".", 1)
            if self.parser.has_section(section) and self.parser.has_option(section, key):
                raw = self.parser.get(section, key)
                if section_dot_key in ("options.resolution", "options.quality"):
                    return (raw.strip().lower() in ("true", "1", "yes", "y", "t"), "INI")
                return (raw if raw.strip() else None, "INI")

        # 3. Default fallback
        if section_dot_key in ("options.resolution", "options.quality"):
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

        # Normalize boolean values
        if f"{section}.{key}" in ("options.resolution", "options.quality"):
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
        
        current_movies = self.get("paths.movies_folder") or ""
        movies_input = Prompt.ask("Movies Folder", default=current_movies)
        if movies_input.strip():
            self.set("paths.movies_folder", movies_input)

        current_tv = self.get("paths.tv_shows_folder") or ""
        tv_input = Prompt.ask("TV Shows Folder", default=current_tv)
        if tv_input.strip():
            self.set("paths.tv_shows_folder", tv_input)

        current_dl = self.get("paths.not_sorted_media_files_folder") or ""
        dl_input = Prompt.ask("Unsorted Downloads Folder", default=current_dl)
        if dl_input.strip():
            self.set("paths.not_sorted_media_files_folder", dl_input)

        # --- 2. API Keys ---
        console.print("\n[bold magenta]🔑 API Keys Configuration[/bold magenta]")
        
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
        current_mail = self.get("mail.mail") or ""
        mail_input = Prompt.ask("Gmail Address", default=current_mail)
        if mail_input.strip():
            self.set("mail.mail", mail_input)

        current_pswd = self.get("mail.mail_pswd") or ""
        pswd_masked = "****" if current_pswd else ""
        pswd_input = Prompt.ask("Gmail App Password (16-letter password)", default=pswd_masked)
        if pswd_input.strip() and pswd_input != pswd_masked:
            self.set("mail.mail_pswd", pswd_input)

        # --- 4. Technical Options ---
        console.print("\n[bold magenta]⚙️ Technical Options[/bold magenta]")
        cur_res = bool(self.get("options.resolution", False))
        res_input = Confirm.ask("Detect and append resolution tags (e.g., [4K], [FullHD])?", default=cur_res)
        self.set("options.resolution", "true" if res_input else "false")

        cur_qual = bool(self.get("options.quality", False))
        qual_input = Confirm.ask("Detect and append quality tags (e.g., [BluRay], [WEB-DL])?", default=cur_qual)
        self.set("options.quality", "true" if qual_input else "false")

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

    @property
    def MAIL_PSWD(self):
        return self.get("mail.mail_pswd")

    @property
    def RESOLUTION(self):
        return bool(self.get("options.resolution", False))

    @property
    def QUALITY(self):
        return bool(self.get("options.quality", False))


# Singleton instance
config = ConfigManager()
