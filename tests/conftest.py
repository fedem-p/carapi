import shutil
import os
import pytest

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")
BACKUP_PATH = SETTINGS_PATH + ".bak"


@pytest.fixture(autouse=True)
def backup_and_restore_settings():
    # Backup before test
    shutil.copy2(SETTINGS_PATH, BACKUP_PATH)
    yield
    # Restore after test
    shutil.move(BACKUP_PATH, SETTINGS_PATH)
