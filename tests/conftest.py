import os
import pytest
from pathlib import Path
from src.config import config

# Clean up oversized environment variables (e.g. from subagent IDE tools) to prevent Windows SetEnvironmentVariable limit crash
for _k, _v in list(os.environ.items()):
    if len(_v) > 10000:
        os.environ.pop(_k, None)


@pytest.fixture(autouse=True)
def isolate_user_config(tmp_path, monkeypatch):
    """
    Quarantine all tests to an isolated temporary configuration directory.
    Guarantees that pytest never reads or modifies the user's real config.ini.
    """
    test_config_dir = tmp_path / "quarantine_rename_config"
    test_config_dir.mkdir(parents=True, exist_ok=True)
    test_config_file = test_config_dir / "config.ini"

    # 1. Point RENAME_CONFIG_FILE to the isolated file
    monkeypatch.setenv("RENAME_CONFIG_FILE", str(test_config_file))

    # 2. Also isolate APPDATA / XDG_CONFIG_HOME / HOME to the temp directory
    monkeypatch.setenv("APPDATA", str(test_config_dir))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(test_config_dir))
    monkeypatch.setenv("HOME", str(test_config_dir))

    # 3. Reload singleton config object with quarantined path
    config.config_path = test_config_file
    config.load()

    # 4. Reset runtime CLI flags
    from src import ui
    ui.NOTIFY_SUCCESS_ENABLED = False
    ui.NOTIFY_ERROR_ENABLED = False
    ui.RESOLUTION_ENABLED = False
    ui.QUALITY_ENABLED = False
    ui.SIMULATE_ENABLED = False
    ui.BYPASS_ENABLED = False
    ui.LOG_ENABLED = False
    ui.VERBOSE_ENABLED = False
    ui.AI_FALLBACK_ENABLED = False
    ui.AUTONOMOUS_ENABLED = False
    ui.POLLING_INTERVAL = 15
