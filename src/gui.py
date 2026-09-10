"""
Graphical Configuration Tool for Media Organizer & Renamer.
Built with Python's standard tkinter and ttk libraries (zero external dependencies).
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Any

from src.config import config as global_config, ConfigManager
from src import api, mail


class ConfigGUI:
    """Tkinter-based configuration window for Media Organizer & Renamer."""

    def __init__(self, root: tk.Tk, cm: Optional[ConfigManager] = None):
        self.root = root
        self.cm = cm or global_config
        self.root.title("🎬 Media Organizer & Renamer — Configuration")
        self.root.geometry("740x680")
        self.root.minsize(680, 560)

        # Style configuration
        self.style = ttk.Style(self.root)
        available_themes = self.style.theme_names()
        for theme in ("clam", "vista", "default"):
            if theme in available_themes:
                try:
                    self.style.theme_use(theme)
                    break
                except Exception:
                    pass

        self._init_variables()
        self._build_ui()
        self.load_values()

    def _init_variables(self):
        """Initializes Tkinter variables for all configuration fields."""
        # Paths
        self.var_movies = tk.StringVar()
        self.var_tv = tk.StringVar()
        self.var_downloads = tk.StringVar()

        # API keys
        self.var_tmdb = tk.StringVar()
        self.var_gemini = tk.StringVar()
        self.var_groq = tk.StringVar()
        self.var_openrouter = tk.StringVar()
        self.var_cf_tok = tk.StringVar()
        self.var_cf_acc = tk.StringVar()
        self.var_ai_provider = tk.StringVar(value="auto")
        self.var_tmdb_conf = tk.StringVar(value="0.75")
        self.var_ai_conf = tk.StringVar(value="0.70")
        self.var_show_secrets = tk.BooleanVar(value=False)

        # Options
        self.var_resolution = tk.BooleanVar(value=False)
        self.var_quality = tk.BooleanVar(value=False)
        self.var_bypass = tk.BooleanVar(value=False)
        self.var_autonomous = tk.BooleanVar(value=False)
        self.var_interval = tk.StringVar(value="15")
        self.var_ai = tk.BooleanVar(value=False)
        self.var_learn = tk.BooleanVar(value=False)
        self.var_log = tk.BooleanVar(value=False)
        self.var_verbose = tk.BooleanVar(value=False)

        # Email
        self.var_mail = tk.StringVar()
        self.var_mail_pswd = tk.StringVar()
        self.var_notify_success = tk.BooleanVar(value=False)
        self.var_notify_error = tk.BooleanVar(value=True)
        self.var_notify_tag = tk.BooleanVar(value=False)

        # Status text
        self.var_status = tk.StringVar(value="Ready")

    def _build_ui(self):
        """Builds the tabbed notebook and action buttons."""
        main_frame = ttk.Frame(self.root, padding="12 12 12 12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header banner
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            header_frame,
            text="🎬 Media Organizer & Renamer Settings",
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT)
        self.lbl_path = ttk.Label(
            header_frame,
            text=f"File: {self.cm.config_path}",
            font=("Helvetica", 8),
            foreground="gray"
        )
        self.lbl_path.pack(side=tk.RIGHT, pady=4)

        # Notebook tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_paths = ttk.Frame(self.notebook, padding=12)
        self.tab_api = ttk.Frame(self.notebook, padding=12)
        self.tab_options = ttk.Frame(self.notebook, padding=12)
        self.tab_email = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_paths, text="  📁 Storage Paths  ")
        self.notebook.add(self.tab_api, text="  🤖 API & Cloud AI  ")
        self.notebook.add(self.tab_options, text="  ⚙️ Renaming & Automation  ")
        self.notebook.add(self.tab_email, text="  📧 Email Alerts  ")

        self._build_paths_tab()
        self._build_api_tab()
        self._build_options_tab()
        self._build_email_tab()

        # Bottom Action Bar
        bottom_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        bottom_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(
            bottom_frame,
            textvariable=self.var_status,
            font=("Helvetica", 9, "italic")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        btn_close = ttk.Button(bottom_frame, text="Close", command=self.root.destroy)
        btn_close.pack(side=tk.RIGHT, padx=4)

        btn_reload = ttk.Button(bottom_frame, text="🔄 Reload", command=self.load_values)
        btn_reload.pack(side=tk.RIGHT, padx=4)

        btn_save = ttk.Button(bottom_frame, text="💾 Save Configuration", command=self.save_values)
        btn_save.pack(side=tk.RIGHT, padx=4)

    # --------------------------------------------------------------------------
    # Tab 1: Paths
    # --------------------------------------------------------------------------
    def _build_paths_tab(self):
        f = self.tab_paths
        ttk.Label(
            f,
            text="Configure your media directories. Folders can be local drives, external disks, or NAS shares.",
            wraplength=660,
            foreground="#555"
        ).pack(anchor=tk.W, pady=(0, 12))

        def make_path_row(parent, label_text, var, browse_title):
            group = ttk.LabelFrame(parent, text=label_text, padding=10)
            group.pack(fill=tk.X, pady=6)
            entry = ttk.Entry(group, textvariable=var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
            btn = ttk.Button(
                group,
                text="Browse...",
                command=lambda: self._browse_folder(var, browse_title)
            )
            btn.pack(side=tk.RIGHT)
            return entry

        self.entry_movies = make_path_row(f, "Movies Library Folder (Destination)", self.var_movies, "Select Movies Folder")
        self.entry_tv = make_path_row(f, "TV Shows Library Folder (Destination)", self.var_tv, "Select TV Shows Folder")
        self.entry_downloads = make_path_row(f, "Unsorted Incoming Downloads Folder (Source)", self.var_downloads, "Select Downloads Folder")

    def _browse_folder(self, var: tk.StringVar, title: str):
        chosen = filedialog.askdirectory(title=title, mustexist=False)
        if chosen:
            var.set(chosen)

    # --------------------------------------------------------------------------
    # Tab 2: API & Cloud AI
    # --------------------------------------------------------------------------
    def _build_api_tab(self):
        f = self.tab_api
        ttk.Label(
            f,
            text="TMDB API key is required for official metadata. Cloud AI providers act as smart fallbacks for cryptic filenames.",
            wraplength=660,
            foreground="#555"
        ).pack(anchor=tk.W, pady=(0, 8))

        # Show/hide secrets toggle
        chk_show = ttk.Checkbutton(
            f,
            text="Show Secret Keys",
            variable=self.var_show_secrets,
            command=self._toggle_secret_visibility
        )
        chk_show.pack(anchor=tk.E, pady=(0, 4))

        self.api_entries = []

        def make_key_row(parent, label_text, var, test_callback=None):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=3)
            lbl = ttk.Label(frame, text=label_text, width=28, anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            ent = ttk.Entry(frame, textvariable=var, show="*")
            ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
            self.api_entries.append(ent)
            if test_callback:
                btn = ttk.Button(frame, text="Test", width=6, command=test_callback)
                btn.pack(side=tk.RIGHT)
            return ent

        make_key_row(f, "TMDB API Key (v3/v4):", self.var_tmdb, self._test_tmdb)
        make_key_row(f, "Google Gemini API Key:", self.var_gemini, lambda: self._test_provider_api("gemini"))
        make_key_row(f, "Groq Cloud API Key:", self.var_groq, lambda: self._test_provider_api("groq"))
        make_key_row(f, "OpenRouter API Key:", self.var_openrouter, lambda: self._test_provider_api("openrouter"))
        make_key_row(f, "Cloudflare Workers AI Token:", self.var_cf_tok)
        make_key_row(f, "Cloudflare Account ID:", self.var_cf_acc, lambda: self._test_provider_api("cloudflare"))

        # Provider Selection & Thresholds
        settings_box = ttk.LabelFrame(f, text="Provider Orchestration & Confidence Thresholds", padding=10)
        settings_box.pack(fill=tk.X, pady=(10, 0))

        # Row 1: Default Provider
        r1 = ttk.Frame(settings_box)
        r1.pack(fill=tk.X, pady=3)
        ttk.Label(r1, text="Default AI Provider:", width=26, anchor=tk.W).pack(side=tk.LEFT)
        cbo_provider = ttk.Combobox(
            r1,
            textvariable=self.var_ai_provider,
            values=["auto", "gemini", "groq", "openrouter", "cloudflare"],
            state="readonly",
            width=18
        )
        cbo_provider.pack(side=tk.LEFT)
        ttk.Label(r1, text="(auto fails over across all configured providers)", foreground="gray").pack(side=tk.LEFT, padx=8)

        # Row 2: TMDB Minimum Confidence
        r2 = ttk.Frame(settings_box)
        r2.pack(fill=tk.X, pady=3)
        ttk.Label(r2, text="TMDB Min Confidence (0.0-1.0):", width=26, anchor=tk.W).pack(side=tk.LEFT)
        sp_tmdb = ttk.Spinbox(r2, from_=0.1, to=1.0, increment=0.05, textvariable=self.var_tmdb_conf, width=8)
        sp_tmdb.pack(side=tk.LEFT)
        ttk.Label(r2, text="Matches below this trigger AI verification (default: 0.75)", foreground="gray").pack(side=tk.LEFT, padx=8)

        # Row 3: AI Minimum Confidence
        r3 = ttk.Frame(settings_box)
        r3.pack(fill=tk.X, pady=3)
        ttk.Label(r3, text="AI Min Confidence (0.0-1.0):", width=26, anchor=tk.W).pack(side=tk.LEFT)
        sp_ai = ttk.Spinbox(r3, from_=0.1, to=1.0, increment=0.05, textvariable=self.var_ai_conf, width=8)
        sp_ai.pack(side=tk.LEFT)
        ttk.Label(r3, text="Threshold to accept AI title correction (default: 0.70)", foreground="gray").pack(side=tk.LEFT, padx=8)

    def _toggle_secret_visibility(self):
        show_char = "" if self.var_show_secrets.get() else "*"
        for ent in self.api_entries:
            ent.configure(show=show_char)

    def _test_tmdb(self):
        key = self.var_tmdb.get().strip()
        if not key:
            messagebox.showwarning("TMDB Test", "Please enter a TMDB API Key first.")
            return
        self.var_status.set("Testing TMDB API...")
        self.root.update_idletasks()
        old_key = getattr(api, "TMDB_API_KEY", None)
        try:
            api.TMDB_API_KEY = key
            success, title, year, _ = api.api_call("Inception", "2010", "en-US", "movie")
            if success:
                messagebox.showinfo("TMDB Test Success", f"✅ TMDB connection successful!\nRetrieved: {title} ({year})")
                self.var_status.set("TMDB connection verified.")
            else:
                messagebox.showerror("TMDB Test Failed", "❌ TMDB responded but query did not match.")
                self.var_status.set("TMDB query failed.")
        except Exception as e:
            messagebox.showerror("TMDB Test Error", f"❌ Connection failed:\n{e}")
            self.var_status.set("TMDB error.")
        finally:
            api.TMDB_API_KEY = old_key

    def _test_provider_api(self, provider: str):
        self.var_status.set(f"Testing {provider.capitalize()} AI...")
        self.root.update_idletasks()

        test_item = [{
            'File': 'Inception.2010.1080p.mkv',
            'Folder': 'Movies',
            'Path': '/movies/Inception.2010.1080p.mkv',
            'Clean': 'Inception',
            'Parse': 'Inception',
            'Media': 'movie'
        }]

        keys_to_restore = []
        try:
            if provider == "gemini":
                key = self.var_gemini.get().strip()
                if not key:
                    messagebox.showwarning("Gemini Test", "Please enter a Gemini API Key first.")
                    return
                keys_to_restore.append(("GEMINI_API_KEY", getattr(api, "GEMINI_API_KEY", None)))
                api.GEMINI_API_KEY = key
                call_func = api.call_gemini_batch
            elif provider == "groq":
                key = self.var_groq.get().strip()
                if not key:
                    messagebox.showwarning("Groq Test", "Please enter a Groq API Key first.")
                    return
                keys_to_restore.append(("GROQ_API_KEY", getattr(api, "GROQ_API_KEY", None)))
                api.GROQ_API_KEY = key
                call_func = api.call_groq_batch
            elif provider == "openrouter":
                key = self.var_openrouter.get().strip()
                if not key:
                    messagebox.showwarning("OpenRouter Test", "Please enter an OpenRouter API Key first.")
                    return
                keys_to_restore.append(("OPENROUTER_API_KEY", getattr(api, "OPENROUTER_API_KEY", None)))
                api.OPENROUTER_API_KEY = key
                call_func = api.call_openrouter_batch
            elif provider == "cloudflare":
                tok = self.var_cf_tok.get().strip()
                acc = self.var_cf_acc.get().strip()
                if not tok or not acc:
                    messagebox.showwarning("Cloudflare Test", "Please enter both Cloudflare Token and Account ID.")
                    return
                keys_to_restore.append(("CLOUDFLARE_API_TOKEN", getattr(api, "CLOUDFLARE_API_TOKEN", None)))
                keys_to_restore.append(("CLOUDFLARE_ACCOUNT_ID", getattr(api, "CLOUDFLARE_ACCOUNT_ID", None)))
                api.CLOUDFLARE_API_TOKEN = tok
                api.CLOUDFLARE_ACCOUNT_ID = acc
                call_func = api.call_cloudflare_batch
            else:
                return

            try:
                resp = call_func(test_item)
            except Exception as e:
                messagebox.showerror(f"{provider.capitalize()} Error", f"❌ Call failed:\n{e}")
                self.var_status.set(f"{provider.capitalize()} call error.")
                return
        finally:
            for attr, orig_val in keys_to_restore:
                setattr(api, attr, orig_val)

        if resp and resp.items:
            item = resp.items[0]
            messagebox.showinfo(
                f"{provider.capitalize()} Success",
                f"✅ {provider.capitalize()} connection successful!\nTitle: {item.title}\nYear: {item.year}\nConfidence: {item.confidence_score}"
            )
            self.var_status.set(f"{provider.capitalize()} verified.")
        else:
            messagebox.showwarning(f"{provider.capitalize()} Test", "Response received but items list was empty.")

    # --------------------------------------------------------------------------
    # Tab 3: Options & Automation
    # --------------------------------------------------------------------------
    def _build_options_tab(self):
        f = self.tab_options

        # Video stream tags
        grp_video = ttk.LabelFrame(f, text="🎞️ Video Stream Tags (FFmpeg)", padding=10)
        grp_video.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(grp_video, text="Detect and append resolution tags (e.g., [1080p], [4K])", variable=self.var_resolution).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_video, text="Detect and append encoding quality tags (e.g., [BluRay], [WEB-DL])", variable=self.var_quality).pack(anchor=tk.W, pady=2)

        # AI Options
        grp_ai = ttk.LabelFrame(f, text="🧠 Cloud AI Fallback & Keyword Learning", padding=10)
        grp_ai.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(grp_ai, text="Enable Cloud AI fallback by default (-i)", variable=self.var_ai).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_ai, text="Enable AI keyword learning by default (save new tags into gemini_tags.json) (-L)", variable=self.var_learn).pack(anchor=tk.W, pady=2)

        # Automation
        grp_auto = ttk.LabelFrame(f, text="⚡ Automation & Headless Watcher", padding=10)
        grp_auto.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(grp_auto, text="Bypass user confirmation prompts and run non-interactively (-b)", variable=self.var_bypass).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_auto, text="Enable autonomous background watcher by default (-a)", variable=self.var_autonomous).pack(anchor=tk.W, pady=2)

        row_int = ttk.Frame(grp_auto)
        row_int.pack(fill=tk.X, pady=3)
        ttk.Label(row_int, text="Autonomous polling interval (minutes):").pack(side=tk.LEFT)
        ttk.Spinbox(row_int, from_=1, to=1440, textvariable=self.var_interval, width=6).pack(side=tk.LEFT, padx=8)

        # Logging
        grp_log = ttk.LabelFrame(f, text="📝 Logging & Diagnostics", padding=10)
        grp_log.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(grp_log, text="Write console output to daily log files (log/YYYY-MM-DD.txt) (-l)", variable=self.var_log).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_log, text="Display verbose diagnostic logs and exception tracebacks (-v)", variable=self.var_verbose).pack(anchor=tk.W, pady=2)

    # --------------------------------------------------------------------------
    # Tab 4: Email Alerts
    # --------------------------------------------------------------------------
    def _build_email_tab(self):
        f = self.tab_email
        ttk.Label(
            f,
            text="Configure optional email notifications for headless servers or automated cron runs.",
            wraplength=660,
            foreground="#555"
        ).pack(anchor=tk.W, pady=(0, 10))

        grp_creds = ttk.LabelFrame(f, text="Gmail SMTP Credentials", padding=10)
        grp_creds.pack(fill=tk.X, pady=6)

        r1 = ttk.Frame(grp_creds)
        r1.pack(fill=tk.X, pady=3)
        ttk.Label(r1, text="Gmail Address:", width=22, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Entry(r1, textvariable=self.var_mail).pack(side=tk.LEFT, fill=tk.X, expand=True)

        r2 = ttk.Frame(grp_creds)
        r2.pack(fill=tk.X, pady=3)
        ttk.Label(r2, text="Gmail App Password:", width=22, anchor=tk.W).pack(side=tk.LEFT)
        ent_pswd = ttk.Entry(r2, textvariable=self.var_mail_pswd, show="*")
        ent_pswd.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.api_entries.append(ent_pswd)

        btn_test_mail = ttk.Button(grp_creds, text="Send Test Email", command=self._send_test_email)
        btn_test_mail.pack(anchor=tk.E, pady=(6, 0))

        grp_notif = ttk.LabelFrame(f, text="Notification Triggers", padding=10)
        grp_notif.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(grp_notif, text="Send email notification when media files are successfully processed", variable=self.var_notify_success).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_notif, text="Send email notification when a processing error occurs", variable=self.var_notify_error).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(grp_notif, text="Send email notification when a new AI keyword tag is discovered (-t)", variable=self.var_notify_tag).pack(anchor=tk.W, pady=2)

    def _send_test_email(self):
        address = self.var_mail.get().strip()
        password = self.var_mail_pswd.get().strip()
        if not address or not password:
            messagebox.showwarning("Email Test", "Please provide both Gmail address and App Password.")
            return

        self.var_status.set("Sending test email...")
        self.root.update_idletasks()
        old_mail = getattr(mail, "MAIL", None)
        old_pswd = getattr(mail, "MAIL_PSWD", None)
        try:
            mail.MAIL = address
            mail.MAIL_PSWD = password

            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText("This is a test notification from Media Organizer & Renamer.", "plain", "utf-8")
            msg["Subject"] = "🎬 Media Organizer Test Email"
            msg["From"] = address
            msg["To"] = address

            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
            server.starttls()
            server.login(address, password)
            server.send_message(msg)
            server.quit()

            messagebox.showinfo("Email Test Success", f"✅ Test email successfully sent to:\n{address}")
            self.var_status.set("Test email sent.")
        except Exception as e:
            messagebox.showerror("Email Test Failed", f"❌ Failed to send test email:\n{e}")
            self.var_status.set("Email test error.")
        finally:
            mail.MAIL = old_mail
            mail.MAIL_PSWD = old_pswd

    # --------------------------------------------------------------------------
    # Load & Save Logic
    # --------------------------------------------------------------------------
    def load_values(self):
        """Populates UI fields from the active ConfigManager."""
        self.var_movies.set(self.cm.get("paths.movies_folder") or "")
        self.var_tv.set(self.cm.get("paths.tv_shows_folder") or "")
        self.var_downloads.set(self.cm.get("paths.not_sorted_media_files_folder") or "")

        self.var_tmdb.set(self.cm.get("api.tmdb_api_key") or "")
        self.var_gemini.set(self.cm.get("api.gemini_api_key") or "")
        self.var_groq.set(self.cm.get("api.groq_api_key") or "")
        self.var_openrouter.set(self.cm.get("api.openrouter_api_key") or "")
        self.var_cf_tok.set(self.cm.get("api.cloudflare_api_token") or "")
        self.var_cf_acc.set(self.cm.get("api.cloudflare_account_id") or "")
        self.var_ai_provider.set(self.cm.get("options.ai_provider") or "auto")
        self.var_tmdb_conf.set(str(self.cm.get("options.tmdb_min_confidence") or "0.75"))
        self.var_ai_conf.set(str(self.cm.get("options.ai_min_confidence") or "0.70"))

        self.var_resolution.set(bool(self.cm.get("options.resolution", False)))
        self.var_quality.set(bool(self.cm.get("options.quality", False)))
        self.var_bypass.set(bool(self.cm.get("options.bypass", False)))
        self.var_autonomous.set(bool(self.cm.get("options.autonomous", False)))
        self.var_interval.set(str(self.cm.get("options.polling_interval") or "15"))
        self.var_ai.set(bool(self.cm.get("options.ai", False)))
        self.var_learn.set(bool(self.cm.get("options.learn", False)))
        self.var_log.set(bool(self.cm.get("options.log", False)))
        self.var_verbose.set(bool(self.cm.get("options.verbose", False)))

        self.var_mail.set(self.cm.get("mail.mail") or "")
        self.var_mail_pswd.set(self.cm.get("mail.mail_pswd") or "")
        self.var_notify_success.set(bool(self.cm.get("options.notify_on_success", False)))
        self.var_notify_error.set(bool(self.cm.get("options.notify_on_error", True)))
        self.var_notify_tag.set(bool(self.cm.get("options.notify_on_tag", False)))

        self.var_status.set("Configuration loaded from disk.")

    def save_values(self):
        """Saves current UI values into config.ini."""
        # Paths
        self.cm.set("paths.movies_folder", self.var_movies.get().strip())
        self.cm.set("paths.tv_shows_folder", self.var_tv.get().strip())
        self.cm.set("paths.not_sorted_media_files_folder", self.var_downloads.get().strip())

        # API keys
        self.cm.set("api.tmdb_api_key", self.var_tmdb.get().strip())
        self.cm.set("api.gemini_api_key", self.var_gemini.get().strip())
        self.cm.set("api.groq_api_key", self.var_groq.get().strip())
        self.cm.set("api.openrouter_api_key", self.var_openrouter.get().strip())
        self.cm.set("api.cloudflare_api_token", self.var_cf_tok.get().strip())
        self.cm.set("api.cloudflare_account_id", self.var_cf_acc.get().strip())

        # Provider & thresholds
        self.cm.set("options.ai_provider", self.var_ai_provider.get().strip())
        try:
            tmdb_val = float(self.var_tmdb_conf.get().strip())
            if 0.0 <= tmdb_val <= 1.0:
                self.cm.set("options.tmdb_min_confidence", str(tmdb_val))
        except ValueError:
            pass

        try:
            ai_val = float(self.var_ai_conf.get().strip())
            if 0.0 <= ai_val <= 1.0:
                self.cm.set("options.ai_min_confidence", str(ai_val))
        except ValueError:
            pass

        # Options
        self.cm.set("options.resolution", "true" if self.var_resolution.get() else "false")
        self.cm.set("options.quality", "true" if self.var_quality.get() else "false")
        self.cm.set("options.bypass", "true" if self.var_bypass.get() else "false")
        self.cm.set("options.autonomous", "true" if self.var_autonomous.get() else "false")
        try:
            int_val = int(self.var_interval.get().strip())
            if int_val >= 1:
                self.cm.set("options.polling_interval", str(int_val))
        except ValueError:
            pass

        self.cm.set("options.ai", "true" if self.var_ai.get() else "false")
        self.cm.set("options.learn", "true" if self.var_learn.get() else "false")
        self.cm.set("options.log", "true" if self.var_log.get() else "false")
        self.cm.set("options.verbose", "true" if self.var_verbose.get() else "false")

        # Email
        self.cm.set("mail.mail", self.var_mail.get().strip())
        self.cm.set("mail.mail_pswd", self.var_mail_pswd.get().strip())
        self.cm.set("options.notify_on_success", "true" if self.var_notify_success.get() else "false")
        self.cm.set("options.notify_on_error", "true" if self.var_notify_error.get() else "false")
        self.cm.set("options.notify_on_tag", "true" if self.var_notify_tag.get() else "false")

        self.var_status.set("✅ Configuration successfully saved!")
        messagebox.showinfo("Saved", f"✅ Configuration successfully saved to:\n{self.cm.config_path}")


def launch_config_gui(cm: Optional[ConfigManager] = None) -> bool:
    """Launches the graphical configuration tool. Returns True if opened, False if headless."""
    try:
        root = tk.Tk()
        app = ConfigGUI(root, cm=cm)
        root.mainloop()
        return True
    except (tk.TclError, Exception) as e:
        sys.stderr.write(f"\n❌ Unable to launch GUI: {e}\n💡 Running in headless/terminal mode? Use 'python main.py configure' instead.\n\n")
        return False
