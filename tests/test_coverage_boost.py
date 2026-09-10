import os
import sys
import json
import runpy
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

import main
from src import ui, files, utils, mail, api
from src.config import ConfigManager

# =========================================================================
# 1. Tests for main.py execution flows and error handling
# =========================================================================

def test_main_no_media_files_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with patch("src.ui.parse_arguments") as mock_args, \
         patch("src.utils.verify_folders"), \
         patch("src.files.search_media_files", return_value=(pd.DataFrame(), pd.DataFrame())), \
         patch("src.ui.print_log") as mock_log:

        mock_args.return_value = MagicMock(subcommand=None, path=None, only_rename=False, simulate=False)
        assert main.main() == 0
        logged = " ".join([str(c[0][0]) for c in mock_log.call_args_list if c[0]])
        assert "No media files found to process" in logged


def test_main_no_media_files_to_rename(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    df_messy = pd.DataFrame([{"File": "A.mkv"}])
    df_clean = pd.DataFrame([{"Original": "A.mkv", "Corrected": "A.mkv"}])

    with patch("src.ui.parse_arguments") as mock_args, \
         patch("src.utils.verify_folders"), \
         patch("src.files.search_media_files", return_value=(df_messy, df_clean)), \
         patch("src.utils.get_corrected_media_filenames", return_value=df_clean), \
         patch("src.utils.has_files_to_rename", return_value=False), \
         patch("src.ui.print_log") as mock_log:

        mock_args.return_value = MagicMock(subcommand=None, path=None, only_rename=False, simulate=False)
        assert main.main() == 0
        logged = " ".join([str(c[0][0]) for c in mock_log.call_args_list if c[0]])
        assert "No media files to rename" in logged


def test_main_only_rename_execution(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["main.py", "--only-rename"])
    video_file = tmp_path / "Movie (2020).mkv"
    video_file.touch()

    df_messy = pd.DataFrame([{"File": "Movie.mkv"}])
    df_clean = pd.DataFrame([{
        "File": "Movie.mkv",
        "Original": "Movie.mkv",
        "Corrected": "Movie (2020)",
        "Path": str(video_file),
        "Media": "movie"
    }])

    with patch("src.ui.parse_arguments") as mock_args, \
         patch("src.utils.verify_folders"), \
         patch("src.files.search_media_files", return_value=(df_messy, pd.DataFrame())), \
         patch("src.utils.get_corrected_media_filenames", return_value=df_clean), \
         patch("src.utils.has_files_to_rename", return_value=True), \
         patch("src.ui.display_corrected_filenames"), \
         patch("src.ui.user_confirmation"), \
         patch("src.files.rename_media_files", return_value=df_clean), \
         patch("src.mail.send_media_success_email") as mock_mail:

        mock_args.return_value = MagicMock(subcommand=None, path=None, only_rename=True, simulate=False)
        assert main.main() == 0
        mock_mail.assert_called_once_with(
            media_name="Movie (2020).mkv",
            original_name="Movie.mkv",
            media_type="movie",
            destination_path=str(video_file)
        )


def test_main_normal_flow_success(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    old_f = tmp_path / "Old.mkv"
    new_f = tmp_path / "New.mkv"

    df_messy = pd.DataFrame([{"File": "Old.mkv"}])
    df_clean = pd.DataFrame([{"File": "Old.mkv", "Original": "Old.mkv", "Corrected": "New", "Path": str(old_f), "Media": "movie"}])

    with patch("src.ui.parse_arguments") as mock_args, \
         patch("src.utils.verify_folders"), \
         patch("src.files.search_media_files", return_value=(df_messy, pd.DataFrame())), \
         patch("src.utils.get_corrected_media_filenames", return_value=df_clean), \
         patch("src.utils.has_files_to_rename", return_value=True), \
         patch("src.ui.display_corrected_filenames"), \
         patch("src.ui.user_confirmation"), \
         patch("src.files.rename_media_files", return_value=df_clean), \
         patch("src.files.sort_media_files", return_value=[(old_f, new_f)]), \
         patch("src.ui.display_sorted_files"), \
         patch("src.files.move_media_files") as mock_move:

        mock_args.return_value = MagicMock(subcommand=None, path=None, only_rename=False, simulate=False)
        assert main.main() == 0
        mock_move.assert_called_once()


def test_main_normal_flow_empty_clean_after_rename(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    df_messy = pd.DataFrame([{"File": "Old.mkv"}])
    df_clean = pd.DataFrame([{"File": "Old.mkv", "Original": "Old.mkv", "Corrected": "New", "Path": "/tmp/old", "Media": "movie"}])

    with patch("src.ui.parse_arguments") as mock_args, \
         patch("src.utils.verify_folders"), \
         patch("src.files.search_media_files", return_value=(df_messy, pd.DataFrame())), \
         patch("src.utils.get_corrected_media_filenames", return_value=df_clean), \
         patch("src.utils.has_files_to_rename", return_value=True), \
         patch("src.ui.display_corrected_filenames"), \
         patch("src.ui.user_confirmation"), \
         patch("src.files.rename_media_files", return_value=pd.DataFrame()), \
         patch("src.ui.print_log") as mock_log:

        mock_args.return_value = MagicMock(subcommand=None, path=None, only_rename=False, simulate=False)
        assert main.main() == 0
        logged = " ".join([str(c[0][0]) for c in mock_log.call_args_list if c[0]])
        assert "No media files to sort and move" in logged


def test_main_runtime_error_handled(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with patch("src.ui.parse_arguments", side_effect=RuntimeError("Fatal runtime err")), \
         patch("src.ui.print_log") as mock_log, \
         patch("src.mail.send_error_email") as mock_mail:

        with pytest.raises(SystemExit) as exc_info:
            main.main()
        assert exc_info.value.code == 1
        mock_mail.assert_called_once_with(error_message="Fatal runtime err")


def test_main_generic_exception_handled(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with patch("src.ui.parse_arguments", side_effect=ZeroDivisionError("division by zero")), \
         patch("src.ui.print_log") as mock_log, \
         patch("src.mail.send_error_email") as mock_mail:

        with pytest.raises(SystemExit) as exc_info:
            main.main()
        assert exc_info.value.code == 1
        assert mock_mail.call_count == 1
        assert "division by zero" in mock_mail.call_args[1]["error_message"]


def test_main_dunder_main(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "config", "--path"])
    with patch("src.ui.handle_config_command"):
        runpy.run_path("main.py", run_name="__main__")


# =========================================================================
# 2. Tests for src/api.py (Gemini response parsing & error handling)
# =========================================================================

def test_gemini_api_call_success_with_missing_tags(monkeypatch):
    media_info = {
        'File': "Blade.Runner.mkv",
        'Folder': "test",
        'Path': "/test/Blade.Runner.mkv",
        'Clean': "Blade Runner",
        'Parse': None,
        'Media': "movie"
    }

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "success": 1,
        "name": "Blade Runner",
        "year": "1982",
        "original_language": "en",
        "missing_tags": ["remux", "1080p"]
    })
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client), \
         patch("src.api.send_email") as mock_send_email, \
         patch("src.api.print_log") as mock_print_log, \
         patch("src.ui.VERBOSE_ENABLED", True):

        res = api.gemini_api_call(media_info)
        assert res[0] is True
        assert res[1] == "Blade Runner"
        assert res[2] == "1982"
        assert res[3] == "en"
        assert res[4] == ["remux", "1080p"]
        mock_send_email.assert_called_once()


def test_gemini_api_call_success_equals_zero(monkeypatch):
    media_info = {'File': "unrecognized.mkv", 'Folder': "test", 'Path': "/test", 'Clean': "unknown", 'Parse': None, 'Media': "movie"}
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"success": 0})
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client), \
         patch("src.api.print_log") as mock_print_log:

        res = api.gemini_api_call(media_info)
        assert res == [False, None, None, None, None]
        logged = " ".join([str(c[0][0]) for c in mock_print_log.call_args_list if c[0]])
        assert "Impossible to read the json data" in logged


def test_gemini_api_call_json_decode_error(monkeypatch):
    media_info = {'File': "corrupted.mkv", 'Folder': "test", 'Path': "/test", 'Clean': "corrupted", 'Parse': None, 'Media': "movie"}
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "NOT_JSON{{"
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client), \
         patch("src.api.print_error") as mock_err:

        res = api.gemini_api_call(media_info)
        assert res == [False, None, None, None, None]
        mock_err.assert_called_once()


# =========================================================================
# 3. Tests for src/config.py (paths resolution and properties)
# =========================================================================

def test_resolve_config_path_variations(tmp_path, monkeypatch):
    cm = ConfigManager.__new__(ConfigManager)

    # 1. Custom path parameter
    assert cm._resolve_config_path("custom.ini") == Path("custom.ini").resolve()

    # 2. Local config.ini in cwd
    local_config = tmp_path / "config.ini"
    local_config.touch()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("RENAME_CONFIG_FILE", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert cm._resolve_config_path() == local_config.resolve()
    local_config.unlink()

    # 3. Quarantine path when PYTEST_CURRENT_TEST is present
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "running")
    quarantine = cm._resolve_config_path()
    assert "pytest_rename_quarantine" in str(quarantine)
    monkeypatch.delenv("PYTEST_CURRENT_TEST")

    # 4. NT without APPDATA
    with patch("os.name", "nt"), patch.dict(os.environ, {"USERPROFILE": str(tmp_path), "HOME": str(tmp_path)}, clear=True):
        nt_path = cm._resolve_config_path()
        assert ".config" in str(nt_path)

    # 5. Posix with XDG_CONFIG_HOME
    with patch("os.name", "posix"), patch("src.config.Path") as mock_p:
        mock_p(".rename.ini").resolve.return_value.is_file.return_value = False
        mock_p("config.ini").resolve.return_value.is_file.return_value = False
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/xdg"}, clear=True):
            cm._resolve_config_path()
            mock_p.assert_any_call("/custom/xdg")

    # 6. Posix without XDG_CONFIG_HOME
    with patch("os.name", "posix"), patch("src.config.Path") as mock_p:
        mock_p(".rename.ini").resolve.return_value.is_file.return_value = False
        mock_p("config.ini").resolve.return_value.is_file.return_value = False
        with patch.dict(os.environ, {}, clear=True):
            cm._resolve_config_path()
            mock_p.home.assert_called_once()


def test_config_property_setters_and_string_getters(tmp_path):
    test_ini = tmp_path / "props.ini"
    cm = ConfigManager(custom_path=str(test_ini))

    # MAIL and MAIL_PSWD
    cm.MAIL = "my@mail.com"
    assert cm.MAIL == "my@mail.com"
    cm.MAIL = None
    assert cm.MAIL is None

    cm.MAIL_PSWD = "secret_password"
    assert cm.MAIL_PSWD == "secret_password"
    cm.MAIL_PSWD = None
    assert cm.MAIL_PSWD is None

    # NOTIFY_ON_SUCCESS
    cm.NOTIFY_ON_SUCCESS = True
    assert cm.NOTIFY_ON_SUCCESS is True
    cm.set("options.notify_on_success", "yes")
    assert cm.NOTIFY_ON_SUCCESS is True
    cm.NOTIFY_ON_SUCCESS = False
    assert cm.NOTIFY_ON_SUCCESS is False

    # NOTIFY_ON_ERROR
    cm.NOTIFY_ON_ERROR = True
    assert cm.NOTIFY_ON_ERROR is True
    cm.set("options.notify_on_error", "1")
    assert cm.NOTIFY_ON_ERROR is True
    cm.NOTIFY_ON_ERROR = False
    assert cm.NOTIFY_ON_ERROR is False

    # BYPASS
    cm.BYPASS = True
    assert cm.BYPASS is True
    cm.set("options.bypass", "true")
    assert cm.BYPASS is True
    cm.BYPASS = False
    assert cm.BYPASS is False

    # AI
    cm.AI = True
    assert cm.AI is True
    cm.set("options.ai", "y")
    assert cm.AI is True
    cm.AI = False
    assert cm.AI is False

    # LOG
    cm.LOG = True
    assert cm.LOG is True
    cm.set("options.log", "t")
    assert cm.LOG is True
    cm.LOG = False
    assert cm.LOG is False

    # VERBOSE
    cm.VERBOSE = True
    assert cm.VERBOSE is True
    cm.set("options.verbose", "yes")
    assert cm.VERBOSE is True
    cm.VERBOSE = False
    assert cm.VERBOSE is False

    # RESOLUTION and QUALITY
    cm.set("options.resolution", "y")
    cm.set("options.quality", "n")
    assert cm.RESOLUTION is True
    assert cm.QUALITY is False


# =========================================================================
# 4. Tests for src/files.py coverage edges
# =========================================================================

def test_move_media_files_with_clean_data_table_and_fallback(tmp_path, monkeypatch):
    movies_dir = tmp_path / "Movies"
    tv_dir = tmp_path / "TV"
    downloads_dir = tmp_path / "Downloads"
    movies_dir.mkdir()
    tv_dir.mkdir()
    downloads_dir.mkdir()

    f1 = downloads_dir / "f1.mkv"
    f2 = downloads_dir / "f2.mkv"
    f1.write_text("1")
    f2.write_text("2")

    dest1 = movies_dir / "f1_dest.mkv"
    dest2 = tv_dir / "f2_dest.mkv"

    clean_df = pd.DataFrame([
        {"File": "f1.mkv", "Corrected": "f1_dest", "Media": "movie"}
    ])

    monkeypatch.setattr(files, "MOVIES_FOLDER", str(movies_dir))
    monkeypatch.setattr(files, "TV_SHOWS_FOLDER", str(tv_dir))
    monkeypatch.setattr(files, "NOT_SORTED_MEDIA_FILES_FOLDER", str(downloads_dir))

    with patch("src.mail.send_media_success_email") as mock_success_mail, \
         patch("src.files.remove_empty_folders"):

        files.move_media_files([(f1, dest1), (f2, dest2)], clean_data_table=clean_df)
        assert mock_success_mail.call_count == 2
        # First call has media from table
        assert mock_success_mail.call_args_list[0][1]["media_type"] == "movie"
        # Second call resolved fallback to tv
        assert mock_success_mail.call_args_list[1][1]["media_type"] == "tv"


def test_move_media_files_fallback_movie_and_exception(tmp_path, monkeypatch):
    movies_dir = tmp_path / "Movies"
    downloads_dir = tmp_path / "Downloads"
    other_dir = tmp_path / "other"
    movies_dir.mkdir()
    downloads_dir.mkdir()
    other_dir.mkdir()

    f1 = downloads_dir / "f1.mkv"
    f1.write_text("1")
    dest1 = movies_dir / "f1_dest.mkv"

    f2 = downloads_dir / "f2.mkv"
    f2.write_text("2")
    dest2 = other_dir / "f2_dest.mkv"

    monkeypatch.setattr(files, "MOVIES_FOLDER", str(movies_dir))
    monkeypatch.setattr(files, "TV_SHOWS_FOLDER", None)
    monkeypatch.setattr(files, "NOT_SORTED_MEDIA_FILES_FOLDER", str(downloads_dir))

    # Test movie fallback
    with patch("src.mail.send_media_success_email") as mock_mail, \
         patch("src.files.remove_empty_folders"):
        files.move_media_files([(f1, dest1)], clean_data_table=None)
        assert mock_mail.call_args[1]["media_type"] == "movie"

    # Test is_relative_to raising exception (lines 257-258)
    with patch("src.mail.send_media_success_email") as mock_mail, \
         patch.object(Path, "is_relative_to", side_effect=Exception("mock err")), \
         patch("src.files.remove_empty_folders"):
        files.move_media_files([(f2, dest2)], clean_data_table=None)
        assert mock_mail.call_args[1]["media_type"] == "unknown"


def test_move_media_files_error_email_failure_caught(tmp_path, monkeypatch):
    downloads = tmp_path / "dl"
    downloads.mkdir()
    bad_source = downloads / "non_existent.mkv"
    dest = tmp_path / "dest.mkv"

    monkeypatch.setattr(files, "NOT_SORTED_MEDIA_FILES_FOLDER", str(downloads))

    with patch("src.mail.send_error_email", side_effect=Exception("SMTP Connection dead")), \
         patch("src.ui.print_log") as mock_log, \
         patch("src.files.remove_empty_folders"):

        files.move_media_files([(bad_source, dest)])
        logged = " ".join([str(c[0][0]) for c in mock_log.call_args_list if c[0]])
        assert "Failed to send error email" in logged


# =========================================================================
# 5. Tests for src/mail.py coverage edges
# =========================================================================

def test_dispatch_email_missing_credentials():
    with patch("src.mail._get_credentials", return_value=(None, None)), \
         patch("src.mail.smtplib.SMTP_SSL") as mock_smtp:

        msg = MagicMock()
        mail._dispatch_email(msg)
        mock_smtp.assert_not_called()


def test_send_media_success_email_dispatch_error_logged():
    with patch("src.mail.is_success_mail_enabled", return_value=True), \
         patch("src.mail._get_credentials", return_value=("me@test.com", "pass")), \
         patch("src.mail._dispatch_email", side_effect=Exception("Timeout")), \
         patch("src.ui.print_log") as mock_log:

        mail.send_media_success_email("Test", "Test.mkv", "movie", "/dest/path")
        logged = " ".join([str(c[0][0]) for c in mock_log.call_args_list if c[0]])
        assert "Failed to send success email: Timeout" in logged


def test_send_email_with_exception_in_details():
    with patch("src.mail.is_error_mail_enabled", return_value=True), \
         patch("src.mail._get_credentials", return_value=("me@test.com", "pass")), \
         patch("src.mail._dispatch_email"):

        # Exception string is not already in message
        exc = RuntimeError("Strange filesystem error")
        mail.send_email(message="A failure happened", exception=exc)
