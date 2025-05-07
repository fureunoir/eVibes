from evibes.settings.base import getenv

if getenv("DBBACKUP_SFTP_HOST") and getenv("DBBACKUP_SFTP_USER") and getenv("DBBACKUP_SFTP_PASS"):
    DBBACKUP_STORAGE = "storages.backends.sftpstorage.SFTPStorage"
    DBBACKUP_STORAGE_OPTIONS = {
        "host": getenv("DBBACKUP_SFTP_HOST"),
        "root_path": "/db_backups/",
        "params": {
            "username": getenv("DBBACKUP_SFTP_USER"),
            "password": getenv("DBBACKUP_SFTP_PASS"),
            "allow_agent": False,
            "look_for_keys": False,
        },
        "interactive": False,
        "file_mode": 0o600,
        "dir_mode": 0o700,
    }
else:
    DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
    DBBACKUP_STORAGE_OPTIONS = {"location": "/app/db_backups/"}
